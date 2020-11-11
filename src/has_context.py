from flask import has_request_context, request


def get_host_url():
    if has_request_context():
        return request.host_url
    return "noserver.testing"
