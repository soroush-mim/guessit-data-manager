from flask import Flask

import server.flask
import server.route_handle
from modules.config.arg_parse import arg_parse

server.flask.app = Flask(__name__)
server.route_handle.addRoutes()

if __name__ == '__main__':
    isThereArg = arg_parse()
    
    if not isThereArg:
        server.flask.getApp()run(debug=True, host='0.0.0.0', port='3003')
        # server.flask.getApp().run(debug=True)
