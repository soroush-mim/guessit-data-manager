from flask import Flask 
from modules.argParse import arg_parse

import server.flask
import server.routeHandle 


server.flask.app = Flask(__name__)
server.routeHandle.addRoutes()

if __name__ == '__main__':
    isThereArg = arg_parse()
    
    if not isThereArg:
        # server.flask.app.run(debug=True, host='0.0.0.0', port='3003')
        server.flask.getApp().run(debug=True)