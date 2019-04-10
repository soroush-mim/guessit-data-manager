import server.flask
from flask import Flask

import server.routeHandle as routeHandler

server.flask.app = Flask(__name__)
routeHandler.addRoutes()

if __name__ == '__main__':

    # server.flask.app.run(debug=True, host='0.0.0.0', port='3001')
    server.flask.getApp().run(debug=True)