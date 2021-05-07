import sys

class Player:
    def __init__(self):
        self.participant_id = 0
        self.summoner_name = ""
        self.account_id = ""
        self.champion_id = 0
        self.kills = 0
        self.deaths = 0
        self.assists = 0

    def __init__(self, participant_id, summoner_name, account_id, champion_id, kills, deaths, assists):
        self.participant_id = participant_id
        self.summoner_name = summoner_name
        self.account_id = account_id
        self.champion_id = champion_id
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

    def add_player(self, player):
        assert(len(self.players) <= Team.MAX_TEAM_SIZE)
        self.players.append(player)

    def is_player_on_team(self, account_id):
        for player in self.players:
            if player.account_id == account_id:
                return True
        return False

class Match:
    TEAM_WIN_VALUE = "Win"

    def __init__(self, blue_team, red_team, winner):
        self.blue_team = blue_team
        self.red_team = red_team
        self.winner = winner

    def is_player_on_winning_team(self, account_id):
        if self.winner == Team.BLUE_TEAM_NAME:
            return self.blue_team.is_player_on_team(account_id)
        else:
            return self.red_team.is_player_on_team(account_id)
