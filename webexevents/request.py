import time
from . import __version__
from . import exceptions
from .configuration import Configuration, endpoint_url
from .http_client import DefaultHttpClient
from .response import Response
from .helpers import lang_version, platform_desc

logger = Configuration.get_logger().getChild(__name__)


def request_configurations():
    return {
        'timeout': (Configuration.get_connect_timeout_sec(), Configuration.get_read_timeout_sec())
    }


def retryable(delay_sec=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            max_retries = Configuration.get_max_retries()
            retries = 0
            send_kwargs = kwargs
            while retries < max_retries:
                try:
                    send_kwargs.update({'retry_count': retries})
                    return func(*args, **kwargs)
                except exceptions.WebexEventsException as e:
                    if not e.is_retryable():
                        raise
                    logger.warning(f"Retrying... ({retries+1}/{max_retries}) error:{e}")
                    retries += 1
                    if retries == max_retries:
                        logger.error(f"Operation failed after maximum retries ({retries}/{max_retries}) Error: {e}")
                        raise
                    time.sleep(delay_sec)
        return wrapper

    return decorator


class Request:

    def __init__(self, query: str, operation_name: str, variables=None, request_options=None,
                 http_client=DefaultHttpClient()):
        if request_options is None:
            request_options = {}
        if variables is None:
            variables = {}

        self.query = query
        self.variables = variables
        self.operation_name = operation_name
        self.request_options = request_options
        self.__access_token = Configuration.get_access_token()
        self.http_client = http_client
        self.response = None

    @retryable()
    def execute(self, **kwargs) -> Response:
        assert self.__access_token is not None

        url = endpoint_url()
        body = {
            'query': self.query,
            'variables': self.variables,
            'operation_name': self.operation_name
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.__access_token}",
            'X-Sdk-Name': 'Python SDK',
            'X-Sdk-Version': __version__,
            'X-Sdk-Lang-Version': lang_version(),
            'User-Agent': f"webex_events_python sdk v{__version__} OS({platform_desc()})"
        }
        if idp := self.request_options.get('idempotency_key'):
            headers['Idempotency-Key'] = idp

        send_request_options = request_configurations()

        self.response = self.http_client.post(url, data=body, headers=headers, **send_request_options)
        self.response.set_retry_count(kwargs['retry_count'])
        if self.response.is_success():
            return self.response

        self.__raise_relevant_error()

    def __raise_relevant_error(self):
        status = self.response.status_code
        if status == 400:
            self.__raise_bad_request()
        elif status == 401:
            raise exceptions.AuthenticationRequiredError(self.response)
        elif status == 403:
            raise exceptions.AuthorizationFailedError(self.response)
        elif status == 404:
            raise exceptions.ResourceNotFoundError(self.response)
        elif status == 408:
            raise exceptions.RequestTimeoutError(self.response)
        elif status == 409:
            raise exceptions.ConflictError(self.response)
        elif status == 413:
            raise exceptions.QueryComplexityIsTooHighError(self.response)
        elif status == 422:
            raise exceptions.UnprocessableEntityError(self.response)
        elif status == 429:
            self.__raise_too_many_request()
        elif status == 500:
            raise exceptions.ServerError(self.response)
        elif status == 502:
            raise exceptions.BadGatewayError(self.response)
        elif status == 503:
            raise exceptions.ServiceUnavailableError(self.response)
        elif status == 504:
            raise exceptions.GatewayTimeoutError(self.response)
        elif status in range(400, 500):
            raise exceptions.ClientError(self.response)
        elif status in range(500, 600):
            raise exceptions.ServerError(self.response)

        raise exceptions.NoneStatusError(self.response)

    def __raise_too_many_request(self):
        if get := getattr(self.response.content, 'get', None):
            if extensions := get('extensions'):
                if int(extensions.get('dailyAvailableCost')) < 1:
                    raise exceptions.DailyQuotaIsReachedError(self.response)
                if int(extensions.get('availableCost')) < 1:
                    raise exceptions.SecondBasedQuotaIsReachedError(self.response)
        raise exceptions.TooManyRequestError(self.response)

    def __raise_bad_request(self):
        content = self.response.content
        if 'extensions' not in content:
            raise exceptions.BadRequestError(self.response)

        code = content['extensions'].get('code')
        if code in ("TOKEN_IS_REVOKED", "INVALID_TOKEN", "JWT_TOKEN_IS_INVALID"):
            raise exceptions.InvalidAccessTokenError(self.response)
        elif code in ("TOKEN_IS_EXPIRED", "JWT_TOKEN_IS_EXPIRED"):
            raise exceptions.AccessTokenIsExpiredError(self.response)
        raise exceptions.BadRequestError(self.response)
