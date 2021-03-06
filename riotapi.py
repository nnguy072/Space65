from riotwatcher import LolWatcher, ApiError
from models import Player, Team, Match
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics
from catboost import CatBoostClassifier

import sys
import json
import time
import itertools
import pandas as pd
import category_encoders as ce

class RiotApi:

    GAME_MODE = "ARAM"
    MY_REGION = "na1"
    ARAM_QUEUE_ID = 450
    MATCHES_FILE_NAME = "matches.txt"

    def __init__(self, api_key):
        self.lol_watcher = LolWatcher(api_key)
        
        champion_data_tup = self.get_champion_id_to_name_mapping()
        self.current_champion_version = champion_data_tup[0]
        self.champion_id_mapping = champion_data_tup[1]
        self.champion_square_assets_base_link = f"https://ddragon.leagueoflegends.com/cdn/{self.current_champion_version}/img/champion/"
        
        summoner_spell_data_tup = self.get_summoner_spell_id_to_name_mapping()
        self.current_summoner_spell_version = summoner_spell_data_tup[0]
        self.summoner_spell_id_mapping = summoner_spell_data_tup[1]
        self.summoner_spell_assets_base_link = f"https://ddragon.leagueoflegends.com/cdn/{self.current_summoner_spell_version}/img/spell/"

        self.profile_icon_assets_base_link = f"https://ddragon.leagueoflegends.com/cdn/{self.current_champion_version}/img/profileicon/"

    # Ex. 1 -> Annie
    def get_champion_id_to_name_mapping(self):
        versions = self.lol_watcher.data_dragon.versions_for_region(RiotApi.MY_REGION)
        champions_version = versions['n']['champion']

        # get some champions
        current_champ_dict = self.lol_watcher.data_dragon.champions(champions_version)["data"]

        clean_champ_dict = {int(value["key"]):key for key, value in current_champ_dict.items()}
        return(champions_version, clean_champ_dict)

    def get_champion_name_by_id(self, champion_id):
        # should almost never hit else case except if playing a brand new champion and data dragon hasn't been updated yet
        return self.champion_id_mapping[champion_id] if champion_id in self.champion_id_mapping else "NA"

    def get_summoner_spell_id_to_name_mapping(self):
        versions = self.lol_watcher.data_dragon.versions_for_region(RiotApi.MY_REGION)
        summoner_spells_version = versions['n']['summoner']

        # get some summoner spells
        current_spells_dict = self.lol_watcher.data_dragon.summoner_spells(summoner_spells_version)["data"]

        clean_spells_dict = {int(value["key"]):{"name": value["name"], "image": value["image"]} for key, value in current_spells_dict.items()}
        # return (clean_spells_dict)
        return (summoner_spells_version, clean_spells_dict)

    def get_summoner_spell_by_id(self, spell_id):
        # should almost never hit else case except if playing on a brand new version and data dragon hasn't been updated yet
        return {"name": self.summoner_spell_id_mapping[spell_id]["name"], "asset": self.summoner_spell_id_mapping[spell_id]["image"]["full"]} if spell_id in self.summoner_spell_id_mapping else "NA"

    # returns summoner info json object that contains name and all the ids, etc.
    # more details here: https://developer.riotgames.com/apis#summoner-v4/GET_getBySummonerName
    def get_summoner_info(self, summoner_name):
        try:
            summoner = self.lol_watcher.summoner.by_name(RiotApi.MY_REGION, summoner_name)
            return summoner
        except ApiError as err:
            return err.response.json()

    # returns Match object from models.py for a specific match
    def process_match_info(self, match_dict):
        # create team objects
        blue_team = Team(Team.BLUE_TEAM_ID)
        red_team = Team(Team.RED_TEAM_ID)

        # # loop through list of player specific info
        for index, item in enumerate(match_dict["participants"]):
            summoner_name = match_dict["participantIdentities"][index]["player"]["summonerName"]
            champion_id = item["championId"]
            champion_name = self.get_champion_name_by_id(champion_id)

            spell_1_id = item["spell1Id"]
            spell_1_name = self.get_summoner_spell_by_id(spell_1_id)
            spell_2_id = item["spell2Id"]
            spell_2_name = self.get_summoner_spell_by_id(spell_2_id)
            profile_icon = match_dict["participantIdentities"][index]["player"]["profileIcon"]

            stats_obj = item["stats"]
            kills = stats_obj["kills"]
            deaths = stats_obj["deaths"]
            assists = stats_obj["assists"]

            team_id = item["teamId"]
            
            current_player = Player(summoner_name, champion_id, champion_name, kills, deaths, assists, spell_1_id, spell_1_name, spell_2_id, spell_2_name, profile_icon)
            if (team_id == Team.BLUE_TEAM_ID):
                blue_team.add_player(current_player)
            else:
                red_team.add_player(current_player)
        
        # # find out what team won. blue team info is always first
        winner = Team.BLUE_TEAM_NAME if match_dict["teams"][0]["win"] == Match.TEAM_WIN_VALUE else Team.RED_TEAM_NAME
        return_match = Match(match_dict["gameId"], blue_team, red_team, winner)
        return return_match

    def read_list_of_matches_from_file(self):
        data = {}
        with open(RiotApi.MATCHES_FILE_NAME, "r") as json_file:
            data = json.load(json_file)

        return data

    def write_list_of_matches_from_file(self, data):
        with open(RiotApi.MATCHES_FILE_NAME, "w") as json_file:
            json.dump(data, json_file)

    # get latest 25 games and update matches.txt with it for games that aren't already in there
    def update_list_of_matches(self, summoner_name, champion_ids = [], begin_index = None, end_index = None):  
        summoner = self.get_summoner_info(summoner_name)  
        previous_matches_json = self.read_list_of_matches_from_file()
        previous_matches_array = previous_matches_json["matches"]
        list_of_previous_match_ids = [x["gameId"] for x in previous_matches_array]

        matches = self.lol_watcher.match.matchlist_by_account(
            RiotApi.MY_REGION, summoner["accountId"],
            queue = [RiotApi.ARAM_QUEUE_ID],
            champion = champion_ids,
            begin_index = begin_index,
            end_index = end_index
        )

        # get only new matches that we haven't included yet
        new_matches = [x for x in matches["matches"] if x["gameId"] not in list_of_previous_match_ids]
        for match in new_matches:
            previous_matches_array.append(self.lol_watcher.match.by_id(RiotApi.MY_REGION, match["gameId"]))

        latest_matches = {"matches": previous_matches_array}
        # construct new dictionary with previous matches + new matches
        self.write_list_of_matches_from_file(latest_matches)

    def batch_update_list_of_matches(self, summoner_name):
        summoner = self.get_summoner_info(summoner_name)  
        previous_matches_json = self.read_list_of_matches_from_file()
        previous_matches_array = previous_matches_json["matches"]
        list_of_previous_match_ids = [x["gameId"] for x in previous_matches_array]

        for i in range(10):
            begin_index = 75 * i
            end_index = 75 * (i + 1)

            matches = self.lol_watcher.match.matchlist_by_account(
                RiotApi.MY_REGION, summoner["accountId"],
                queue = [RiotApi.ARAM_QUEUE_ID],
                begin_index = begin_index,
                end_index = end_index
            )

            # get only new matches that we haven't included yet
            new_matches = [x for x in matches["matches"] if x["gameId"] not in list_of_previous_match_ids]
            for match in new_matches:
                previous_matches_array.append(self.lol_watcher.match.by_id(RiotApi.MY_REGION, match["gameId"]))

            latest_matches = {"matches": previous_matches_array}
            # construct new dictionary with previous matches + new matches
            self.write_list_of_matches_from_file(latest_matches)

            print(i)

            time.sleep(130)

    # return live match json object from riot api: https://developer.riotgames.com/apis#spectator-v4/GET_getCurrentGameInfoBySummoner
    def get_live_match(self, summoner_name):
        summoner = self.get_summoner_info(summoner_name)
        match = self.lol_watcher.spectator.by_summoner(RiotApi.MY_REGION, summoner["id"])

        return match

    # return Match object from models.py but with no winner value as game isn't finished yet
    # match param is json object of live match
    def process_live_match(self, match):
        # currently on care about aram games that aren't custom games
        # custom games won't have a gameQueueConfigId field
        # if match["gameQueueConfigId"] is None or match["gameQueueConfigId"] != RiotApi.ARAM_QUEUE_ID:
        #     return None
        
        # create team objects
        blue_team = Team(Team.BLUE_TEAM_ID)
        red_team = Team(Team.RED_TEAM_ID)

        for item in match["participants"]:
            summoner_name = item["summonerName"]
            champion_id = item["championId"]
            champion_name = self.get_champion_name_by_id(champion_id)

            spell_1_id = item["spell1Id"]
            spell_1_name = self.get_summoner_spell_by_id(spell_1_id)
            spell_2_id = item["spell2Id"]
            spell_2_name = self.get_summoner_spell_by_id(spell_2_id)
            profile_icon = item["profileIconId"]

            team_id = item["teamId"]

            current_player = Player(summoner_name, champion_id, champion_name, 
                    spell_1_id=spell_1_id, spell_1_name=spell_1_name, spell_2_id=spell_2_id,
                    spell_2_name=spell_2_name, profile_icon=profile_icon)
            if (team_id == Team.BLUE_TEAM_ID):
                blue_team.add_player(current_player)
            else:
                red_team.add_player(current_player)

        return_match = Match(match["gameId"], blue_team, red_team, Match.LIVE_GAME_WINNER)
        return return_match

    def get_live_match_api(self, summoner_name):
        processed_live_match = self.process_live_match(self.get_live_match(summoner_name))
        return processed_live_match.get_live_match_dict(summoner_name,
            {"champion": self.champion_square_assets_base_link, "summoner_spell": self.summoner_spell_assets_base_link, "profile_icon": self.profile_icon_assets_base_link}
        )

    # will return whether you will win or not (details depend on what model we use)
    def get_win_prediction(self, summoner_name):
        previous_matches_list = self.read_list_of_matches_from_file()
        processed_matches_list = [self.process_match_info(match) for match in previous_matches_list["matches"]]
        
        # get only matches where player is in the game
        filtered_matches_list = [match for match in processed_matches_list if match.is_player_in_match(summoner_name)]
        if (len(filtered_matches_list) <= 0):
            return {}, 404

        data = pd.DataFrame([match.get_model_dict(summoner_name) for match in filtered_matches_list])
        list_of_dicts = []
        for row in data.itertuples():
            values = row[4:]

            ally_champion_permutations = list(itertools.permutations(values, 4))
            for permutation in ally_champion_permutations:
                result_dict = {}
                result_dict["winner"] = row[1]
                result_dict["ally_summoner"] = row[2]
                result_dict["ally_summoner_champion"] = row[3]
                result_dict["ally_1_champion"] = permutation[0]
                result_dict["ally_2_champion"] = permutation[1]
                result_dict["ally_3_champion"] = permutation[2]
                result_dict["ally_4_champion"] = permutation[3]
                list_of_dicts.append(result_dict)

        data = pd.DataFrame(list_of_dicts)

        feature_columns = [col for col in data.columns if "ally" in col if "champion" in col]
        label_columns = ["winner"]

        for col in feature_columns:
            data[col] = data[col].astype("category")

        x = data[feature_columns]
        y = data[label_columns]

        x_train, x_test, y_train, y_test = train_test_split(x, y, train_size=0.8)
        # This takes a while to train the mode. Around ~
        model=CatBoostClassifier(iterations=200, max_ctr_complexity=2, eval_metric="AUC", loss_function="Logloss", task_type="CPU", allow_writing_files=False)
        model.fit(x_train, y_train, cat_features=feature_columns, eval_set=(x_test, y_test), verbose = 200, use_best_model=True)

        y_pred_test = model.predict(x_test)

        live_match = self.get_live_match(summoner_name)
        processed_live_match = self.process_live_match(live_match)
        live_match_pd = pd.DataFrame([processed_live_match.get_model_dict(summoner_name)])
        pred_data = live_match_pd[feature_columns]
        y_pred = model.predict(pred_data)

        return {"accuracy": metrics.accuracy_score(y_test, y_pred_test), "result": str(y_pred[0])}
