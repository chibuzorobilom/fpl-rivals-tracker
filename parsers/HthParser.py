from analyzers.utility_functions import auth
from parsers.Parser import Parser


class HthParser(Parser):
    __url = "https://fantasy.premierleague.com/api/leagues-h2h-matches/league/{}/?page={}&event={}"
    __HUGE_HTH_LEAGUE = 19824

    def __init__(self, team_id, leagues, current_event):
        super().__init__(team_id)
        self.__leagues = leagues
        self.__current_event = current_event

    """
    self.__leagues is a dictionary:
    - keys are leagues codes
    - values are strings = names of these leagues
    result is a dictionary:
    - keys are opponent ids
    - values are strings = names of the league where the match is going to be played
    """
    def get_opponents_ids(self):
        result = {}
        session = auth()

        for key, value in self.__leagues.items():
            # Ignoring this league because there's an issue with it
            if key == self.__HUGE_HTH_LEAGUE:
                continue

            (opponent_id, (my_points, opponent_points)) = self.__get_opponent_id(session=session, league_code=key)

            # Regular match
            if opponent_id is not None:
                result[opponent_id] = value
            # H2H league with odd number of players:
            # In this case, opponent is league's average score
            # opponent_id[1] = average score
            else:
                result["AVERAGE"] = (my_points, opponent_points, value)

        return result

    # TO-DO: Issue with HUGE H2H leagues
    #        Example league: 19824
    def __get_opponent_id(self, session, league_code, page_cnt=1):
        new_url = self.__url.format(league_code, page_cnt, self.__current_event)
        response = session.get(new_url).json()
        # has_next = response["has_next"]

        data = response["results"]
        opponent_id = -1
        points = -1

        for element in data:
            match = [element["entry_1_entry"], element["entry_2_entry"]]
            points = [element["entry_1_points"], element["entry_2_points"]]

            if match[0] == self._id:
                opponent_id = match[1]
            elif match[1] == self._id:
                opponent_id = match[0]
                points.reverse()

        if opponent_id != -1:
            result = (opponent_id, points)
            return result
        else:
            return self.__get_opponent_id(session, league_code, page_cnt + 1)
