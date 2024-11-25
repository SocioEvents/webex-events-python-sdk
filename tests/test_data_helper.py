from unittest.mock import Mock

token_prod_test = 'sk_121212'

# headers should be Case Insensitive dict
success_headers = {
    "DATE": "Tue, 23 Jul 2024 20:03:47 GMT",
    "CONTENT-TYPE": "application/json; charset=utf-8",
    "CONTENT-LENGTH": "245",
    "X-FRAME-OPTIONS": "SAMEORIGIN",
    "X-XSS-PROTECTION": "0",
    "X-CONTENT-TYPE-OPTIONS": "nosniff",
    "X-PERMITTED-CROSS-DOMAIN-POLICIES": "none",
    "REFERRER-POLICY": "strict-origin-when-cross-origin",
    "VARY": "Accept, Origin",
    "X-DAILY-CALL-LIMIT": "62/2000",
    "X-SECONDLY-CALL-LIMIT": "1/500",
    "ETAG": "W2d5bb6de22c82e2b954b669e42963f93",
    "CACHE-CONTROL": "max-age=0, private, must-revalidate",
    "X-REQUEST-ID": "d877259b-8388-4087-b548-280702cc1b67",
    "X-RUNTIME": "0.076380",
}
rate_limited_headers = {**success_headers,
                        'X-DAILY-RETRY-AFTER': 10,
                        'X-SECONDLY-RETRY-AFTER': 20}
request_headers = {"Content-Type": "application/json",
                   "Authorization": "Bearer sk_test_token",
                   "X-Sdk-Name": "PHP SDK",
                   "X-Sdk-Version": "1.0.0",
                   "X-Sdk-Lang-Version": "8.3.9",
                   "User-Agent": "WebexEventsPhpSDK",
                   "Accept": "application/json"}
request_body = '{"query":"query Query {\\n  currenciesList {\\n    isoCode\\n  }\\n}","operation_name":"currenciesList"}'
url = 'https://public.sandbox-api.socio.events/graphql'
success_response_text = '{"data":{"currenciesList":[{"isoCode":"USD"},{"isoCode":"EUR"},{"isoCode":"GBP"},{"isoCode":"AUD"},{"isoCode":"CAD"},{"isoCode":"SGD"},{"isoCode":"NZD"},{"isoCode":"CHF"},{"isoCode":"MXN"},{"isoCode":"THB"},{"isoCode":"BRL"},{"isoCode":"SEK"}]}}'
success_mutation_response_text = '{"data":{"componentCreate":{"id":177,"eventId":2,"featureTypeId":6,"name":"component name"}}}'


def response_body_with_error(extension_code):
    return '{"message":"Invalid Access Token.","extensions":{"code":"' + extension_code + '"}}'


def mock_success_post_query(mock_post):
    return mock_post_with_status(mock_post, status=200, response_text=success_response_text)


def mock_failed_post_query(mock_post, extension_code):
    return mock_post_with_status(mock_post, status=400, response_text=response_body_with_error(extension_code))


def mock_success_mutation(mock_post):
    return mock_post_with_status(mock_post, status=200, response_text=success_mutation_response_text)


def mock_post_with_status(mock_post, status, response_text):
    mock_post.return_value.status_code = status
    mock_post.return_value.text = response_text
    mock_post.return_value.elapsed.microseconds = 100
    mock_post.return_value.headers = success_headers
    mock_post.return_value.request.headers = request_headers
    mock_post.return_value.request.body = request_body
    mock_post.return_value.request.url = url


def create_mock(status, response_text):
    send_kwargs = {
        "status_code": status,
        "text": response_text,
        "elapsed.microseconds": 100,
        "headers": success_headers,
        "request.headers": request_headers,
        "request.body": request_body,
        "request.url": url
        }
    return Mock(**send_kwargs)
