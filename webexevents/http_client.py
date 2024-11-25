import json
import logging
from functools import cache
from abc import ABC, abstractmethod
from .response import Response
from .configuration import Configuration


logger = Configuration.get_logger().getChild(__name__)


class HttpClient(ABC):
    @classmethod
    @abstractmethod
    def post(cls, url, data, headers, **kwargs) -> Response:
        pass


class DefaultHttpClient(HttpClient):

    @classmethod
    def post(cls, url, data, headers, **kwargs) -> Response:
        import requests
        http_response = requests.post(url=url, data=json.dumps(data), headers=headers, **kwargs)

        cls.__log_if_debug(http_response, kwargs)

        response_details = {
            'time_spend_in_ms': http_response.elapsed.microseconds // 1000,
            'response_headers': http_response.headers,  # headers is a case-insensitive dictionary
            'request_headers': http_response.request.headers,
            'request_body': http_response.request.body,
            'url': http_response.request.url
        }
        return Response(http_response.status_code, http_response.text, **response_details)

    @classmethod
    def __log_if_debug(cls, http_response, kwargs):
        if DefaultHttpClient.is_logger_level_debug():
            logger.debug(f" Request: url:{http_response.url}"
                         f" headers:{http_response.request.headers}"
                         f" body:{http_response.request.body}"
                         f" options:{kwargs}")

            logger.debug(f" Response: {http_response.status_code}"
                         f" headers:{http_response.headers} "
                         f" content:{http_response.content}")

    @classmethod
    @cache
    def is_logger_level_debug(cls):
        return logging.DEBUG in (logger.level, logger.parent.level)
