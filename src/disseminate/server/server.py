"""
Setup the server
"""
import bottle
from beaker.middleware import SessionMiddleware

from .. import settings


def run_server(in_directory='.', out_directory='.', port=settings.default_port):
    # Setup the bottle app
    app = bottle.app()
    app.config['in_directory'] = in_directory

    # Setup the session middleware
    session_opts = {
        'session.type': 'memory',
        'session.cookie_expires': 600,  # 10 minutes
        'session.auto': True,
    }

    app = SessionMiddleware(app, session_opts, environ_key='session')
    bottle.run(app=app, host='localhost', port=port, debug=True)
