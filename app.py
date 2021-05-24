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
def update():
    summoner_name = request.args.get("summonerName")
    summoner = riot_api.get_summoner_info(summoner_name)
    if "status" in summoner:
        return {}, summoner["status"]["status_code"]
    riot_api.update_list_of_matches(summoner["name"], begin_index = 0, end_index = 50)
    return {}, 204

@app.route('/batch-update', methods=['POST'])
@cross_origin()
def batch_update():
    summoner_name = request.args.get("summonerName")
    summoner = riot_api.get_summoner_info(summoner_name)
    if "status" in summoner:
        return {}, summoner["status"]["status_code"]
    riot_api.batch_update_list_of_matches(summoner["name"])
    return {}, 204

@app.route('/live-match', methods=['GET'])
@cross_origin()
def get_live_match():
    summoner_name = request.args.get("summonerName")
    summoner = riot_api.get_summoner_info(summoner_name)
    if "status" in summoner:
        return {}, summoner["status"]["status_code"]
    return riot_api.get_live_match_api(summoner["name"]), 200

@app.route('/my-summoner', methods=['GET'])
@cross_origin()
def get_win_prediction():
    summoner_name = request.args.get("summonerName")
        
    summoner = riot_api.get_summoner_info(summoner_name)
    if "status" in summoner:
        return {}, summoner["status"]["status_code"]
    return riot_api.get_win_prediction(summoner["name"])
    

