class Player:

    def __init__(self, summoner_name, champion_id, champion_name, kills=0, deaths=0, assists=0):
        self.summoner_name = summoner_name
        self.champion_id = champion_id
        self.champion_name = champion_name
        self.kills = kills
        self.deaths = deaths
        self.assists = assists

class Team: 
    MAX_TEAM_SIZE = 5
    BLUE_TEAM_ID = 100
    RED_TEAM_ID = 200   
    BLUE_TEAM_NAME = "Blue"
    RED_TEAM_NAME = "RED"

    def __init__(self, team_id):
        self.players = []
        self.team_id = team_id
        self.win = ""

    def get_team_name(self):
        if self.team_id == Team.BLUE_TEAM_ID:
            return Team.BLUE_TEAM_NAME
        else:
            return Team.RED_TEAM_NAME

    def add_player(self, player):
        assert(len(self.players) < Team.MAX_TEAM_SIZE)
        self.players.append(player)

    def is_player_on_team(self, summoner_name):
        for player in self.players:
            if player.summoner_name == summoner_name:
                return True
        return False

    def get_champion_id_by_summoner_name(self, summoner_name):
        for player in self.players:
            if (player.summoner_name == summoner_name):
                return player.champion_id
        return 0

    def get_champion_name_by_summoner_name(self, summoner_name):
        for player in self.players:
            if (player.summoner_name == summoner_name):
                return player.champion_name
        return "NA"

class Match:
    TEAM_WIN_VALUE = "Win"
    LIVE_GAME_WINNER = "NONE"

    def __init__(self, match_id, blue_team, red_team, winner):
        self.match_id = match_id
        self.blue_team = blue_team
        self.red_team = red_team
        self.winner = winner

    def is_player_on_winning_team(self, summoner_name):
        if self.winner == Team.BLUE_TEAM_NAME:
            return self.blue_team.is_player_on_team(summoner_name)
        else:
            return self.red_team.is_player_on_team(summoner_name)

    def get_ally_and_enemy_team_list(self, summoner_name):
        if (self.blue_team.is_player_on_team(summoner_name)):
            return {"ally_team": self.blue_team, "enemy_team": self.red_team}
        else:
            return {"ally_team": self.red_team, "enemy_team": self.blue_team}
        
    def get_champion_id_by_summoner_name(self, summoner_name):
        team = self.blue_team if self.blue_team.is_player_on_team(summoner_name) else self.red_team
        return team.get_champion_id_by_summoner_name(summoner_name)

    def get_champion_name_by_summoner_name(self, summoner_name):
        team = self.blue_team if self.blue_team.is_player_on_team(summoner_name) else self.red_team
        return team.get_champion_name_by_summoner_name(summoner_name)

    def get_dict(self, summoner_name):
        result_dict = {}
        teams_dict = self.get_ally_and_enemy_team_list(summoner_name)
        result_dict["winner"] = 1 if self.is_player_on_winning_team(summoner_name) else 0
        result_dict["ally_summoner"] = summoner_name
        result_dict["ally_summoner_champion"] = self.get_champion_name_by_summoner_name(summoner_name)

        index = 1
        for player in teams_dict["ally_team"].players:
            if (player.summoner_name != summoner_name):
                result_dict["ally_" + str(index) + "_champion"] = player.champion_name
                index = index + 1

        return result_dict
