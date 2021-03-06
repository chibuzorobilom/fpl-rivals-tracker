import requests


class LiveDataParser:
    __live_data_url = "https://fantasy.premierleague.com/api/event/{}/live/"

    def __init__(self, current_event, is_dgw=False):
        self.__live_data = requests.get(self.__live_data_url.format(current_event)).json()
        self.__all_players = self.__live_data["elements"]
        self.__is_dgw = is_dgw

    def count_players_played(self, players_ids):
        result = (self.__players_played_in_sgw(players_ids), ())

        if self.__is_dgw:
            dgw_players_count = self.__players_played_in_dgw(players_ids)
            result = (result[0], dgw_players_count)

        return result

    def get_player_points(self, player_id):
        for player in self.__all_players:
            if player["id"] == player_id:
                return player["stats"]["total_points"]

    def __players_played_in_sgw(self, players_ids):
        count = 0

        for player_id in players_ids:
            player_data = self.__get_player_data(player_id)
            minutes_played = player_data["stats"]["minutes"]

            if minutes_played > 0:
                count += 1

        return count

    def __players_played_in_dgw(self, players_ids):
        dgw_players_played = 0
        dgw_players_count = 0

        for player_id in players_ids:
            player_data = self.__get_player_data(player_id)["explain"]

            if len(player_data) == 2:
                dgw_players_count += 1

                # fixtures aren't sorted in the provided data
                minutes_played_first_fixture = player_data[0]["stats"][0]["value"]
                minutes_played_second_fixture = player_data[1]["stats"][0]["value"]

                if minutes_played_first_fixture > 0 and minutes_played_second_fixture > 0:
                    dgw_players_played += 1

        result = (dgw_players_played, dgw_players_count)
        return result

    def __get_player_data(self, player_id):
        for player in self.__all_players:
            if player["id"] == player_id:
                return player
