from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

import sys
from riotapi import RiotApi

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

riot_api = RiotApi(app.config["RIOT_API_KEY"])

@app.route('/')
@cross_origin()
def hello_world():
    return 'Hello, World!'

@app.route('/test', methods=['GET'])
@cross_origin()
def hello_world_test():
    return riot_api.champion_id_mapping

@app.route('/my_summoner', methods=['GET'])
@cross_origin()
def get_win_prediction():
    summoner_name = request.args.get("summonerName")
    return riot_api.get_win_prediction(summoner_name)
    

