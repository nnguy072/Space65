from flask import Flask, redirect, request, jsonify
from flask_cors import CORS, cross_origin

import sys
import os
from riotapi import RiotApi

app = Flask(__name__, instance_relative_config=True)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

riot_api = RiotApi(os.environ.get("RIOT_API_KEY"))

# Uncomment these 2 lines if doing local testing
# app.config.from_pyfile('config.py')
# riot_api = RiotApi(app.config["RIOT_API_KEY"])

@app.route('/')
@cross_origin()
def hello_world():
    return redirect("https://chimera65.azurewebsites.net/home")

@app.route('/api/v1/update', methods=['POST'])
@cross_origin()
def update():
    summoner_name = request.args.get("summonerName")
    summoner = riot_api.get_summoner_info(summoner_name)
    if "status" in summoner:
        return {}, summoner["status"]["status_code"]
    riot_api.update_list_of_matches(summoner["name"], begin_index = 0, end_index = 50)
    return {}, 204

@app.route('/api/v1/batch-update', methods=['POST'])
@cross_origin()
def batch_update():
    summoner_name = request.args.get("summonerName")
    summoner = riot_api.get_summoner_info(summoner_name)
    if "status" in summoner:
        return {}, summoner["status"]["status_code"]
    riot_api.batch_update_list_of_matches(summoner["name"])
    return {}, 204

@app.route('/api/v1/live-match', methods=['GET'])
@cross_origin()
def get_live_match():
    summoner_name = request.args.get("summonerName")
    summoner = riot_api.get_summoner_info(summoner_name)
    if "status" in summoner:
        return {}, summoner["status"]["status_code"]
    return riot_api.get_live_match_api(summoner["name"]), 200

@app.route('/api/v1/my-summoner', methods=['GET'])
@cross_origin()
def get_win_prediction():
    summoner_name = request.args.get("summonerName")
        
    summoner = riot_api.get_summoner_info(summoner_name)
    if "status" in summoner:
        return {}, summoner["status"]["status_code"]
    return riot_api.get_win_prediction(summoner["name"])
    

if __name__ == "__main":
    app.run()