from riotwatcher import LolWatcher, ApiError
from models import Player, Team, Match
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics

import sys
import json
import pandas as pd

class RiotApi:

    GAME_MODE = "ARAM"
    MY_REGION = "na1"
    ARAM_QUEUE_ID = "450"

    def __init__(self, api_key):
        self.lol_watcher = LolWatcher(api_key)
        self.champion_id_mapping = self.get_champion_id_to_name_mapping()

    # Ex. 1 -> Annie
    def get_champion_id_to_name_mapping(self):
        versions = self.lol_watcher.data_dragon.versions_for_region(RiotApi.MY_REGION)
        champions_version = versions['n']['champion']

        # get some champions
        current_champ_dict = self.lol_watcher.data_dragon.champions(champions_version)["data"]

        clean_champ_dict = {int(value["key"]):key for key, value in current_champ_dict.items()}
        return(clean_champ_dict)

    def get_champion_name_by_id(self, champion_id):
        # should almost never hit else case except if playing a brand new champion and data dragon hasn't been updated yet
        return self.champion_id_mapping[champion_id] if champion_id in self.champion_id_mapping else "NA"

    # returns summoner info json object that contains name and all the ids, etc.
    # more details here: https://developer.riotgames.com/apis#summoner-v4/GET_getBySummonerName
    def get_summoner_info(self, summoner_name):
        return self.lol_watcher.summoner.by_name(RiotApi.MY_REGION, summoner_name)

    # returns Match object from models.py for a specific match
    def get_match_info(self, match_id):
        match = self.lol_watcher.match.by_id(RiotApi.MY_REGION, match_id)

        # create team objects
        blue_team = Team(Team.BLUE_TEAM_ID)
        red_team = Team(Team.RED_TEAM_ID)

        # loop through list of player specific info
        for index, item in enumerate(match["participants"]):
            summoner_name = match["participantIdentities"][index]["player"]["summonerName"]
            champion_id = item["championId"]
            champion_name = self.get_champion_name_by_id(champion_id)

            stats_obj = item["stats"]
            kills = stats_obj["kills"]
            deaths = stats_obj["deaths"]
            assists = stats_obj["assists"]

            team_id = item["teamId"]
            
            current_player = Player(summoner_name, champion_id, champion_name, kills, deaths, assists)
            if (team_id == Team.BLUE_TEAM_ID):
                blue_team.add_player(current_player)
            else:
                red_team.add_player(current_player)
        
        # find out what team won. blue team info is always first
        winner = Team.BLUE_TEAM_NAME if match["teams"][0]["win"] == Match.TEAM_WIN_VALUE else Team.RED_TEAM_NAME
        return_match = Match(match_id, blue_team, red_team, winner)
        return return_match

    def get_list_of_matches(self, summoner, champion_ids = [], begin_index = None, end_index = None):
        matches = self.lol_watcher.match.matchlist_by_account(
            RiotApi.MY_REGION, summoner["accountId"],
            queue = [RiotApi.ARAM_QUEUE_ID],
            champion = champion_ids,
            begin_index = begin_index,
            end_index = end_index
        )
        match_list = [self.get_match_info(match_info["gameId"]) for match_info in matches["matches"]]

        return match_list

    # return Match object from models.py but with no winner value as game isn't finished yet
    # info about json object here: https://developer.riotgames.com/apis#spectator-v4/GET_getCurrentGameInfoBySummoner
    def get_live_match(self, summoner):
        match = self.lol_watcher.spectator.by_summoner(RiotApi.MY_REGION, summoner["id"])

        # currently on care about aram games that aren't custom games
        # custom games won't have a gameQueueConfigId field
        if match["gameQueueConfigId"] is None or match["gameQueueConfigId"] != RiotApi.ARAM_QUEUE_ID:
            return None
        
        # create team objects
        blue_team = Team(Team.BLUE_TEAM_ID)
        red_team = Team(Team.RED_TEAM_ID)

        for item in match["participants"]:
            summoner_name = match["participantIdentities"][index]["player"]["summonerName"]
            champion_id = item["championId"]
            champion_name = self.get_champion_name_by_id(champion_id)

            current_player = Player(summoner_name, champion_id, champion_name)
            if (team_id == Team.BLUE_TEAM_ID):
                blue_team.add_player(current_player)
            else:
                red_team.add_player(current_player)

        return_match = Match(match_id, blue_team, red_team, Match.LIVE_GAME_WINNER)
        return return_match

    # take in current (live) match data for the team champion compositions
    # take in list of previous matches as "training" data for our model
    # currently placeholder
    def calculate_percentage_of_winning(self, summoner_name, live_match, previous_match_list):
        return "0"

    

    # will return whether you will win or not (details depend on what model we use)
    def get_win_prediction(self, summoner_name):
        summoner = self.get_summoner_info(summoner_name)

        #live_match = self.get_live_match(summoner)
        #current_champion_id = live_match.get_champion_id_by_summoner_name(summoner_name)

        previous_matches = self.get_list_of_matches(summoner, begin_index = 0, end_index = 10)
        return self.calculate_percentage_of_winning(summoner_name, previous_matches[0], previous_matches)