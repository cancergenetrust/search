from flask import Flask

app = Flask(__name__)


@app.route('/dude')
def hello_world():
    return 'Hello, World!'
