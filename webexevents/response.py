import json
import logging
from .configuration import Configuration
from .rate_limiter import RateLimiter

logger = Configuration.get_logger().getChild(__name__)


class Response:
    def __init__(self, status_code, content,
                 response_headers=None,
                 request_headers=None,
                 request_body=None,
                 url='',
                 time_spend_in_ms=0,
                 retry_count=0,
                 **kwargs):
        if request_body is None:
            request_body = ''
        if request_headers is None:
            request_headers = {}
        if response_headers is None:
            response_headers = {}

        self.status_code = status_code
        self.content = self.__to_json(content)
        self.response_headers = response_headers
        self.request_headers = request_headers
        self.request_body = request_body
        self.url = url
        self.time_spend_in_ms = time_spend_in_ms
        self.retry_count = retry_count
        self.args = kwargs
        self.rate_limiter = RateLimiter(self.response_headers)

    def __to_json(self, content):
        try:
            return json.loads(content)
        except Exception as ex:
            if self.is_success():
                logger.error(f"Json decode error:{content}")
                raise
            elif logger.parent.level < logging.INFO:
                logger.info(f"Json decode error:{content}")
            return {'raw_content': content}

    def is_success(self):
        return self.status_code == 200

    def set_retry_count(self, retry_count):
        self.retry_count = retry_count

    def __str__(self):
        return f"<WebexResponse {self.status_code} elapsed_ms:{self.time_spend_in_ms} headers: {self.response_headers} content:{self.content}>"
