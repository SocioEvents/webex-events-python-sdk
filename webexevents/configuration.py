import logging
import sys


class Configuration:
    """
    SDK configurations
    :var  __access_token: token
    :var __connect_timeout_sec, __read_timeout_sec, __max_retries: request default params, can be changed using setter

    :var __max_retries: maximum try count, means: once + retries = max retry
    """
    __access_token = None
    __logger_name = 'WebexEvents'

    __connect_timeout_sec = 30.0
    __read_timeout_sec = 60.0
    __max_retries = 3

    @classmethod
    def get_connect_timeout_sec(cls) -> float:
        return cls.__connect_timeout_sec

    @classmethod
    def get_read_timeout_sec(cls) -> float:
        return cls.__read_timeout_sec

    @classmethod
    def get_max_retries(cls) -> int:
        return cls.__max_retries

    @classmethod
    def set_connect_timeout_sec(cls, connect_time_out_sec: float):
        if connect_time_out_sec is not None:
            assert float(connect_time_out_sec) > 0
            cls.__connect_timeout_sec = float(connect_time_out_sec)

    @classmethod
    def set_read_timeout_sec(cls, read_time_out_sec: float = None):
        if read_time_out_sec is not None:
            assert float(read_time_out_sec) > 0
            cls.__read_timeout_sec = float(read_time_out_sec)

    @classmethod
    def set_max_retries(cls, max_retry: int):
        if max_retry is not None:
            assert int(max_retry) >= 0
            cls.__max_retries = int(max_retry)

    @classmethod
    def set_access_token(cls, token):
        cls.__access_token = token

    @classmethod
    def get_access_token(cls):
        return cls.__access_token

    @classmethod
    def set_logger_stream(cls, level=logging.WARNING, format_string=None):
        if format_string is None:
            format_string = "%(asctime)s %(name)s [%(levelname)s] %(message)s"
        stream = sys.stderr if level in (logging.WARNING, logging.ERROR) else sys.stdout
        logger = logging.getLogger(cls.__logger_name)
        logger.setLevel(level)
        handler = logging.StreamHandler(stream=stream)
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(format_string))
        logger.addHandler(handler)

    @classmethod
    def get_logger(cls):
        return logging.getLogger(cls.__logger_name)


def endpoint_url() -> str:
    path = '/graphql'
    if is_live_token():
        return 'https://public.api.socio.events' + path
    else:
        return 'https://public.sandbox-api.socio.events' + path


def is_live_token() -> bool:
    token = Configuration.get_access_token()
    if token.find('sk_live') == 0:
        return True
    return False


Configuration.get_logger().addHandler(logging.NullHandler())

