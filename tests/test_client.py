import uuid
from unittest.mock import patch
import pytest

from webexevents.client import query, do_introspection_query
from webexevents.configuration import Configuration
from webexevents import exceptions
from .test_data_helper import *


@patch('requests.post')
def test_query_success(mock_post):
    mock_success_post_query(mock_post)

    Configuration.set_access_token(token_prod_test)
    query_str = 'query Query { currenciesList {   isoCode  } }'
    operation_str = 'currencyList'
    response = query(query_str, operation_str)

    assert response.status_code == 200
    mock_post.assert_called_once()
    called_kwargs = mock_post.call_args.kwargs
    assert called_kwargs['timeout'] == (Configuration.get_connect_timeout_sec(), Configuration.get_read_timeout_sec())
    assert called_kwargs['headers']['Authorization'] == f"Bearer {token_prod_test}"

    assert response.rate_limiter.daily_based_cost_threshold == 2000


@patch('requests.post')
def test_query_failed(mock_post):
    mock_failed_post_query(mock_post, 'TOKEN_IS_REVOKED')

    Configuration.set_access_token(token_prod_test)
    query_str = 'query Query { currenciesList {   isoCode  } }'
    operation_str = 'currencyList'
    with pytest.raises(exceptions.InvalidAccessTokenError, match="Invalid Access Token.") as ex:
        query(query_str, operation_str)
    response = ex.value.response
    assert response.status_code == 400
    assert response.retry_count == 0
    mock_post.assert_called_once()
    called_kwargs = mock_post.call_args.kwargs
    assert called_kwargs['timeout'] == (Configuration.get_connect_timeout_sec(), Configuration.get_read_timeout_sec())
    assert called_kwargs['headers']['Authorization'] == f"Bearer {token_prod_test}"


@patch('requests.post')
def test_query_failed_and_retry_and_failed(mock_post):
    response_text = 'Bad gateway'
    mock_post_with_status(mock_post, 502, response_text)

    Configuration.set_access_token(token_prod_test)
    query_str = 'query Query { currenciesList {   isoCode  } }'
    operation_str = 'currencyList'
    with pytest.raises(exceptions.BadGatewayError, match=response_text) as ex:
        query(query_str, operation_str)

    response = ex.value.response
    assert response.status_code == 502
    assert response.retry_count == Configuration.get_max_retries() - 1  # once + retry counts
    assert mock_post.call_count == Configuration.get_max_retries()

    called_kwargs = mock_post.call_args.kwargs
    assert called_kwargs['timeout'] == (Configuration.get_connect_timeout_sec(), Configuration.get_read_timeout_sec())
    assert called_kwargs['headers']['Authorization'] == f"Bearer {token_prod_test}"


@patch('requests.post')
def test_query_failed_and_retry_and_success(mock_post):
    bad_gateway_response_text = 'Bad gateway'
    mock_post.side_effect = [
        create_mock(502, bad_gateway_response_text),
        create_mock(502, bad_gateway_response_text),
        create_mock(200, success_response_text),
    ]


    Configuration.set_access_token(token_prod_test)
    query_str = 'query Query { currenciesList {   isoCode  } }'
    operation_str = 'currencyList'
    response = query(query_str, operation_str)

    assert response.status_code == 200
    assert response.retry_count == Configuration.get_max_retries() - 1  # once + retry counts
    assert mock_post.call_count == Configuration.get_max_retries()

    called_kwargs = mock_post.call_args.kwargs
    assert called_kwargs['timeout'] == (Configuration.get_connect_timeout_sec(), Configuration.get_read_timeout_sec())
    assert called_kwargs['headers']['Authorization'] == f"Bearer {token_prod_test}"


@patch('requests.post')
def test_introspection(mock_post):
    mock_success_post_query(mock_post)

    Configuration.set_access_token(token_prod_test)

    response = do_introspection_query()

    assert response.status_code == 200
    mock_post.assert_called_once()
    called_kwargs = mock_post.call_args.kwargs
    assert called_kwargs['timeout'] == (Configuration.get_connect_timeout_sec(), Configuration.get_read_timeout_sec())
    assert called_kwargs['headers']['Authorization'] == f"Bearer {token_prod_test}"


@patch('requests.post')
def test_query_mutation_success(mock_post):
    mock_success_mutation(mock_post)

    Configuration.set_access_token(token_prod_test)
    mutation_str = """mutation ComponentCreate($input: ComponentCreateInput!) {
                          componentCreate(input: $input) {
                            id
                            eventId
                            featureTypeId
                            name
                          } }"""
    mutation_operation = 'componentCreate'
    mutation_variables = {
        "input": {
            "eventId": 2,
            "featureTypeId": 6,
            "name": "CmpPyhtonSdkTest2",
            "pictureUrl": 'https://media.socio.events/',
            "settings": {
                "displayMethod": "GRID",
                "isHidden": False
            }
        }
    }
    idempotency_key = str(uuid.uuid1())

    response = query(mutation_str, mutation_operation, mutation_variables, {'idempotency_key': idempotency_key})

    assert response.status_code == 200
    assert response.retry_count == 0

    called_kwargs = mock_post.call_args.kwargs
    assert called_kwargs['headers']['Authorization'] == f"Bearer {token_prod_test}"
    assert called_kwargs['headers']['Idempotency-Key'] == idempotency_key
