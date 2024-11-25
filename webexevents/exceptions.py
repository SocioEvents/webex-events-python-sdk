class WebexEventsException(Exception):
    def __init__(self, response):
        self.response = response
        self.status = response.status_code
        self.message = response.content.get('message') or str(response.content)
        self.extensions = response.content.get('extensions')
        if self.extensions:
            self.code = self.extensions.get('code')

    def __str__(self):
        return f"{self.status} - {self.message}"

    def is_retryable(self):
        return False


class ResourceNotFoundError(WebexEventsException):
    pass


class ConflictError(WebexEventsException):
    def is_retryable(self):
        return True


class AuthenticationRequiredError(WebexEventsException):
    pass


class AuthorizationFailedError(WebexEventsException):
    pass


class UnprocessableEntityError(WebexEventsException):
    pass


class InvalidAccessTokenError(WebexEventsException):
    pass


class AccessTokenIsExpiredError(WebexEventsException):
    pass


class DailyQuotaIsReachedError(WebexEventsException):
    pass


class SecondBasedQuotaIsReachedError(WebexEventsException):
    def is_retryable(self):
        return True


class QueryComplexityIsTooHighError(WebexEventsException):
    pass


class RequestTimeoutError(WebexEventsException):
    def is_retryable(self):
        return True


class BadGatewayError(WebexEventsException):
    def is_retryable(self):
        return True


class ServiceUnavailableError(WebexEventsException):
    def is_retryable(self):
        return True


class GatewayTimeoutError(WebexEventsException):
    def is_retryable(self):
        return True


class ClientError(WebexEventsException):
    pass


class NoneStatusError(WebexEventsException):
    pass


class BadRequestError(WebexEventsException):
    pass


class TooManyRequestError(WebexEventsException):
    pass


class ServerError(WebexEventsException):
    def reference_id(self):
        return self.__extensions.get('referenceId')
