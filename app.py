from flask import Flask, Response, request, jsonify
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

@app.route('/update', methods=['POST'])
@cross_origin()
def hello_world_test():
    summoner_name = request.args.get("summonerName")
    riot_api.update_list_of_matches(summoner_name, begin_index = 0, end_index = 50)
    return {}, 200

@app.route('/live-match', methods=['GET'])
@cross_origin()
def get_live_match():
    summoner_name = request.args.get("summonerName")
    return riot_api.get_live_match_api(summoner_name)

@app.route('/my-summoner', methods=['GET'])
@cross_origin()
def get_win_prediction():
    summoner_name = request.args.get("summonerName")
    return riot_api.get_win_prediction(summoner_name)
    

