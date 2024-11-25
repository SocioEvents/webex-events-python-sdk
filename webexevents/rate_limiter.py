class RateLimiter:
    def __init__(self, response_headers: dict):
        """
        Parses and store rate limiter response

        `secondly_retry_after_in_ms`: wait before retrying the request
        `daily_retry_after_in_second`: wait before sending next request

        :param response_headers: case-insensitive dictionary of headers
        """
        self.response_headers = response_headers
        self.used_second_based_cost = None
        self.second_based_cost_threshold = None
        self.used_daily_based_cost = None
        self.daily_based_cost_threshold = None
        self.daily_retry_after_in_second = None
        self.secondly_retry_after_in_ms = None

        self.__parse_secondly_retry_after_in_ms()
        self.__parse_daily_retry_after()
        self.__parse_daily_based_cost()
        self.__parse_second_based_cost()

    def __parse_secondly_retry_after_in_ms(self):
        self.secondly_retry_after_in_ms = self.__read_from_header('X-SECONDLY-RETRY-AFTER')

    def __parse_daily_retry_after(self):
        self.daily_retry_after_in_second = self.__read_from_header('X-DAILY-RETRY-AFTER')

    def __parse_daily_based_cost(self):
        values = self.__read_used_and_treshold('X-DAILY-CALL-LIMIT')
        if not values:
            return
        used, threshold = values
        self.used_daily_based_cost = int(used)
        self.daily_based_cost_threshold = int(threshold)

    def __parse_second_based_cost(self):
        values = self.__read_used_and_treshold('X-SECONDLY-CALL-LIMIT')
        if not values:
            return
        used, threshold = values
        self.used_second_based_cost = int(used)
        self.second_based_cost_threshold = int(threshold)

    def __read_used_and_treshold(self, key):
        value = self.response_headers.get(key)
        if not value:
            return None
        return value.split('/')

    def __read_from_header(self, key):
        value = self.response_headers.get(key)
        if value:
            return int(value)
        return None
