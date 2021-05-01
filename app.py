from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
@cross_origin()
def hello_world():
  return 'Hello, World!'

@app.route('/test', methods=['POST'])
@cross_origin()
def hello_world_test():
  return jsonify(request.json)
