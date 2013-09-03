"""
    Collection of tools which may be used as a param_parser http protocol params
"""

def rest_params_parser(method, parsed_url, body):
    #TODO: add support for body params
    return '', [parsed_url.path], {}
