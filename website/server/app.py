from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def my_app():
    return 'Hello from server'

@app.route('/test1')
def test1():
    response = 'This is a first server call'
    return response

@app.route('/test2')
def test2():
    return 'This is a second server call'


if __name__ == '__main__':
    app.run()


