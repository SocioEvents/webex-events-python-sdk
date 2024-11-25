from .configuration import Configuration
from .response import Response
from .request import Request
from .helpers import introspection_query_string

logger = Configuration.get_logger().getChild(__name__)


def query(query_str: str, operation_name: str, variables: dict = None, options: dict = None) -> Response:
    """
    :param query_str: graphql query or mutation string
    :param operation_name: operation name
    :param variables: query or mutation variables, dict
    :param options: dictionary for request, for mutations `idempotency_key` is required
    :return: Response
    """
    if options is None:
        options = {}
    if variables is None:
        variables = {}
    logger.info('Starting request')
    return Request(query_str, operation_name, variables, options).execute()


def do_introspection_query() -> Response:
    """
    executes introspection query
    :return: Response
    """
    logger.info('Starting introspection query...')
    return query(introspection_query_string(), 'IntrospectionQuery')
