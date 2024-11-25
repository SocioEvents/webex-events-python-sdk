[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE.txt)
[![Webex Events](https://github.com/SocioEvents/webex-events-python-sdk/actions/workflows/python-package.yml/badge.svg)](https://github.com/SocioEvents/webex-events-python-sdk/actions)


[![Webex EVENTS](webex-events-logo-white.svg 'Webex Events')](https://socio.events)

# Webex Events Api Python SDK

Webex Events provides a range of additional SDKs to accelerate your development process.
They allow a standardized way for developers to interact with and leverage the features and functionalities. 
Pre-built code modules will help access the APIs with your private keys, simplifying data gathering and update flows.

Requirements
-----------------

- Python 3.9+

Installation
-----------------

Via command line:

```shell
pip install webex-events
```


In your python script:

```python
from webexevents.client import query
```

Configuration
-----------------

```python
from webexevents.configuration import Configuration

Configuration.set_access_token('access_token') # required
Configuration.set_read_timeout_sec(40.0) # optional, default 60.0
Configuration.set_connect_timeout_sec(30.0) # optional, default 30.0
Configuration.set_max_retries(5) # optional, default 3
Configuration.set_logger_stream(level=logging.DEBUG) # default logging is disabled

```

Usage
-----------------

```python
from webexevents.client import query

query_str = """
    query EventsConnection($first: Int) {
        eventsConnection(first: $first){
            edges{
                cursor
                node{
                    id
                    name
                    groups{
                        id
                        name
                    }
                }
            }
        }
    }
  """
response = query(query_str, 'EventsConnection', {'first': 20})
event = response.content["data"]["eventsConnection"]["edges"][0]
```

If the request is successful, `Client.query` will return `Response` object which has the following properties.

| Method             | Type                                                                                                          |
|--------------------|---------------------------------------------------------------------------------------------------------------|
| `status_code`      | `int`                                                                                                         |
| `response_headers` | `dict`                                                                                                        |
| `content`          | `dict`                                                                                                        |
| `request_headers`  | `dict`                                                                                                        |
| `request_body`     | `str`                                                                                                         |
| `url`              | `str`                                                                                                         |
| `retry_count`      | `int`                                                                                                         |
| `time_spent_in_ms` | `int`                                                                                                         |
| `rate_limiter`     | [`RateLimiter`](https://github.com/SocioEvents/webex-events-python-sdk/blob/main/webexevents/rate_limiter.py) |


For non 200 status codes, an exception is raised for every status code such as `webexevents.exceptions.ServerError` for server errors. 
For the flow-control these exceptions should be handled like the following. This is an example for `429` status code.
For the full list please refer to [this](https://github.com/SocioEvents/webex-events-python-sdk/blob/main/webexevents/exceptions.py) file.

```python
from webexevents.client import query
from webexevents.exceptions import *
import time

query_str = 'your query here'

try:
    response = query(query_str, 'EventsConnection', {'first': 20})
except DailyQuotaIsReachedError as ex:
    pass
    # Do something here
except SecondBasedQuotaIsReachedError as e:
    sleep_time = e.response.rate_limiter.second_based_cost_threshold
    time.sleep(sleep_time)
    # retry
```
By default, `webexevents.client.query` is retryable under the hood. It retries the request several times for the following exceptions.
```
webexevents.exceptions.RequestTimeoutError => 408
webexevents.exceptions.ConflictError => 409
webexevents.exceptions.SecondBasedQuotaIsReachedError => 429
webexevents.exceptions.BadGatewayError => 502
webexevents.exceptions.ServiceUnavailableError => 503
webexevents.exceptions.GatewayTimeoutError => 504
```

For Introspection
-----------------
```
Client.do_introspection_query
```

Idempotency
-----------------
The API supports idempotency for safely retrying requests without accidentally performing the same operation twice. 
When doing a mutation request, use an idempotency key. If a connection error occurs, you can repeat 
the request without risk of creating a second object or performing the update twice.

To perform mutation request, you must add a header which contains the idempotency key such as 
`Idempotency-Key: <your key>`. The SDK does not produce an Idempotency Key on behalf of you if it is missed. Here is an example
like the following:

```python
from webexevents.client import query
from webexevents.exceptions import *
import time

mutation_str = """
          mutation TrackDelete($input: TrackDeleteInput!) {
            trackDelete(input: $input) {
              success
            }
          }
"""

try:
    response = query(mutation_str, "trackDelete", {"id": 10}, options={"idempotency_key": "unique_key"})

except ConflictError as e:  # Conflict errors are retriable, but to guarantee it you can handle the exception again.
    time.sleep(0.2)
    # retry

```

Telemetry Data Collection
-----------------
Webex Events collects telemetry data, including hostname, operating system, language and SDK version, via API requests. 
This information allows us to improve our services and track any usage-related faults/issues. We handle all data with 
the utmost respect for your privacy. For more details, please refer to the Privacy Policy at https://www.cisco.com/c/en/us/about/legal/privacy-full.html

Development
-----------------
After checking out the repo and then install pip-tools if it has not been installed already.

```shell
python -m pip install pip-tools
```

compile project 

```shell
 pip-compile pyproject.toml
``` 

and install dependencies: 
```shell
pip-sync
```

then, you need to install dev dependencies 

```shell
pip install '.[dev]'
```


to run the tests 

```shell 
pytest 
```

build and upload to test env:

```shell
python -m pip install build twine
python -m build
twine check dist/*
cat ~/.pypirc #check api key is here
twine upload -r testpypi dist/*
```

install package to local as editable package 
``python -m pip install -e .``

Contributing
-----------------
Please see the [contributing guidelines](CONTRIBUTING.md).

License
-----------------

The package is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).

Code of Conduct
-----------------

Everyone interacting in the Webex Events API project's codebases, issue trackers, chat rooms and mailing lists is expected to follow the [code of conduct](https://github.com/SocioEvents/webex-events-python-sdk/blob/main/CODE_OF_CONDUCT.md).
