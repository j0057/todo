
from jjm import xhttp

import model

app = lambda req: { 'x-status': xhttp.status.OK, 'content-type': 'text/plain', 'x-content': 'Hello, world!' }
app = xhttp.catcher(app)
app = xhttp.xhttp_app(app)

if __name__ == '__main__':
    xhttp.run_server(app, port=8080)
