from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from riotwatcher import LolWatcher, ApiError
import json
import sys
import statistics

from models import Player, Team, Match

app = Flask(__name__, instance_relative_config=True)
#app.config.from_object('config')
app.config.from_pyfile('config.py')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

lol_watcher = LolWatcher(app.config["RIOT_API_KEY"])
my_region = 'na1'
aram_queue_id = "450"

def calculate_percentage_of_winning(current_match, list_of_previous_matches)

def get_match_info(match_id):
    match = lol_watcher.match.by_id(my_region, match_id)
    #return match

    # Create team objects
    blue_team = Team(Team.BLUE_TEAM_ID)
    red_team = Team(Team.RED_TEAM_ID)

    # blue_team.win = x["win"] for x in teams_list if x["team_id"] == blue_team_id
    # red_team.win = x["win"] for x in teams_list if x["team_id"] == red_team_id

    # loop through list of player specific info
    for index, item in enumerate(match["participants"]):
        participant_id = item["participantId"]
        summoner_name = match["participantIdentities"][index]["player"]["summonerName"]
        account_id = match["participantIdentities"][index]["player"]["accountId"]
        champion_id = item["championId"]

        stats_obj = item["stats"]
        kills = stats_obj["kills"]
        deaths = stats_obj["deaths"]
        assists = stats_obj["assists"]

        team_id = item["teamId"]
        
        current_player = Player(participant_id, summoner_name, account_id, champion_id, kills, deaths, assists)
        if (team_id == Team.BLUE_TEAM_ID):
            blue_team.add_player(current_player)
        else:
            red_team.add_player(current_player)
    
    # Get team info array
    teams_list = match["teams"]

    # find out what team won. blue team info is always first
    winner = Team.BLUE_TEAM_NAME if teams_list[0]["win"] == Match.TEAM_WIN_VALUE else Team.RED_TEAM_NAME
    current_match = Match(blue_team, red_team, winner)

    return current_match

def get_list_of_matches(account_id):
    matches = lol_watcher.match.matchlist_by_account(my_region, account_id, queue = [aram_queue_id])
    match_list = []
    win_loss_list = []

    for match_info in matches["matches"]:
        current_match = get_match_info(match_info["gameId"])
        match_list.append(current_match)
        win_loss_list.append(current_match.is_player_on_winning_team(account_id))

    # convert boolean to int so True -> 1 and False -> 0 to calculate win %
    win_loss_list = list(map(int, win_loss_list))

    #data = {}
    #data["win_loss"] = win_loss_list
    #json_data = json.dumps(data)
    win_percentage = statistics.mean(win_loss_list)
    return str(win_percentage)
    

  

@app.route('/')
@cross_origin()
def hello_world():
    return 'Hello, World!'

@app.route('/test', methods=['POST'])
@cross_origin()
def hello_world_test():
    return jsonify(request.json)

@app.route('/my_summoner', methods=['GET'])
@cross_origin()
def get_summoner_info():
    summoner_name = request.args.get("summonerName")
    me = lol_watcher.summoner.by_name(my_region, summoner_name)
    #return me
    return get_list_of_matches(me['accountId'])
    

