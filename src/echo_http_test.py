import requests
import json
from test_helpers import url

def test_echo(url):
    '''
    A simple test to check echo
    '''
    resp = requests.get(url + 'echo', params={'data': 'hello'})
    assert json.loads(resp.text) == {'data': 'hello'}