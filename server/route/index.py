from server.flask import getApp
from flask import json, request

def add():
    app = getApp()
    @app.route('/', methods=['GET'])
    def index():

        '''
        index of server

        page context:
            show the index of question server and links that can go with
        '''
        Response = {
            'ok': 1,
            'message': 'question server is on',
            'urls': 'some',
        }

        return json.dumps(Response)