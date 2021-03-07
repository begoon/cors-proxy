from collections import Mapping
import datetime
import requests

from flask import (
    Flask,
    render_template_string,
    request,
    Response,
)

application = Flask(__name__)

start_time = datetime.datetime.now()
processed_requests = 0

control_panel_template = """
<html>
<head>
<link
    rel="stylesheet"
    href="https://unpkg.com/purecss@2.0.5/build/pure-min.css"
    integrity="sha384-LTIDeidl25h2dPxrB2Ekgc9c7sEC3CWGM6HeFmuDNUjX76Ert4Z4IY714dhZHPLd"
    crossorigin="anonymous">
</head>
<style>
* {
    margin: 4px;
    font-size: 12px;
}
</style>
</head>
<body>
Start time: {{start_time}}, processed requests: {{processed_requests}}
</body>
</html>
"""


@application.route("/", methods=['GET', 'POST', 'PUT', 'PATCH'])
def index(*args, **kwargs):
    return render_template_string(
        control_panel_template,
        start_time=start_time,
        processed_requests=processed_requests,
    )


def print_headers(headers):
    if isinstance(headers, Mapping):
        headers = headers.items()
    headers_text = '\n'.join(
        [f'{header}: {value}' for header, value in headers]
    )
    print(headers_text)


@application.route(
    "/<path:path>",
    methods=[
        'GET',
        'POST',
        'PUT',
        'PATCH',
        'OPTIONS',
    ],
)
def proxy(*args, **kwargs):
    global processed_requests
    if request.path.startswith('/favicon.ico'):
        return Response(status=200)

    processed_requests += 1

    print(
        f'\nREQUEST ({processed_requests}): {request.method} {request.url}\n'
        f'{str(request.headers).strip()}\n'
    )
    request_data = request.get_data()
    if request_data:
        print(f'{request_data}\n')

    if request.method == 'OPTIONS':
        headers = (
            ('Access-Control-Allow-Origin', '*'),
            (
                'Access-Control-Allow-Methods',
                request.headers['Access-Control-Request-Method'],
            ),
            (
                'Access-Control-Allow-Headers',
                request.headers['Access-Control-Request-Headers'],
            ),
        )
        print(f'RESPONSE ({processed_requests}): 200')
        print_headers(headers)
        return Response(status=200, headers=headers)

    redirect_url = kwargs['path']
    redirect_headers = {
        key: value
        for (key, value) in request.headers
        if key not in ['Host', 'Origin']
    }
    redirect_data = request_data
    print(f'REDIRECT ({processed_requests}): {redirect_url}\n')
    print_headers(redirect_headers)
    print()
    if request_data:
        print(f'{redirect_data}\n')

    response = requests.request(
        method=request.method,
        url=redirect_url,
        headers=redirect_headers,
        data=redirect_data,
        cookies=request.cookies,
        allow_redirects=False,
    )

    print(f'ORIGINAL RESPONSE ({processed_requests}): {response.status_code}')
    print_headers(response.headers)
    print()

    excluded_headers = [
        'content-encoding',
        'content-length',
        'transfer-encoding',
        'connection',
    ]
    headers = [
        (name, value)
        for (name, value) in response.raw.headers.items()
        if name.lower() not in excluded_headers
    ]

    if not bool([h for h, _ in headers if h == 'Access-Control-Allow-Origin']):
        headers.append(('Access-Control-Allow-Origin', '*'))

    print(f'RESPONSE ({processed_requests}): {response.status_code}')
    print_headers(headers)
    content = response.content
    if content:
        print(f'{content}\n')

    return Response(response.content, response.status_code, headers)
