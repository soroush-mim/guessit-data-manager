from flask import Flask, request
import json
from pprint import pprint

from template_engine.TemplateEngine import create_question
# from template_engine.TemplateEngine import TemplateEngine

app = Flask(__name__)


@app.route('/', methods=['GET'])
def main():
    '''
    index of server

    page context:
        show the index of question server and links that can go with
    '''
    Response = {
        'ok': 1,
        'message': 'question server is on',
        'urls': [],
    }

    return json.dumps(Response)




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='3002')