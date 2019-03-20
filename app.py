from flask import Flask, request
import json
from pprint import pprint

from template_engine.TemplateEngine import create_question
# from template_engine.TemplateEngine import TemplateEngine

app = Flask(__name__)

URLS_CONST = {
    'getQ':'get_question',
    'chkAns':'check_answer',
}



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
        'urls': list(URLS_CONST.values()),
    }

    return json.dumps(Response)




@app.route(f'/{URLS_CONST["getQ"]}', methods=['POST', 'GET'])
def get_question():
    '''
    get question part of server

    page context:
        get the question py post request
    '''
    
    Response = ''
    
    if request.method == 'POST':
        Request = request.json


        Response = Request
    
    elif request.method == 'GET':
        Response = {
            'ok': 0,
            'error': 'please use post request for get question',
            'request': {
                'tag': 'some tag that you want',
            }
        }
    
    return json.dumps(Response)




@app.route(f'/{URLS_CONST["chkAns"]}', methods=['POST', 'GET'])
def check_answer():
    '''
    check the answer of a question

    page context:
        check the answer of question by a post request
    '''
    
    Response = ''

    if request.method == 'POST':
        Request = request.json


        Response = Request
    
    elif request.method == 'GET':
        Response = {
            'ok': 0,
            'error': 'please use post request for check Ans',
            'request': {
                'id': 'question ID',
                'answer': 'answer or answers',
            }
        }
    
    return json.dumps(Response)





if __name__ == '__main__':
    app.debug = True
    app.run()