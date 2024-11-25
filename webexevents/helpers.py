import sys
import platform
from functools import cache


def introspection_query_string() -> str:
    return """query IntrospectionQuery {
        __schema {
            queryType { name }
              mutationType { name }
              subscriptionType { name }
              types {
                ...FullType
              }
              directives {
                name
                description
                locations
                args {
                    ...InputValue
                }
              }
            }
          }
          fragment FullType on __Type {
        kind
            name
            description
            fields(includeDeprecated: true) {
            name
              description
              args {
            ...InputValue
              }
              type {
            ...TypeRef
              }
              isDeprecated
              deprecationReason
            }
            inputFields {
            ...InputValue
            }
            interfaces {
            ...TypeRef
            }
            enumValues(includeDeprecated: true) {
            name
              description
              isDeprecated
              deprecationReason
            }
            possibleTypes {
            ...TypeRef
            }
          }
          fragment InputValue on __InputValue {
        name
            description
            type { ...TypeRef }
            defaultValue
          }
          fragment TypeRef on __Type {
        kind
            name
            ofType {
            kind
              name
              ofType {
                kind
                name
                ofType {
                    kind
                  name
                  ofType {
                        kind
                    name
                    ofType {
                            kind
                      name
                      ofType {
                                kind
                        name
                        ofType {
                                    kind
                          name
                        }
                      }
                    }
                  }
                }
              }
            }
          }"""


@cache
def lang_version():
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


@cache
def platform_desc():
    return platform.platform()
