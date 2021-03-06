from managers.Manager import Manager

from parsers.EventDataParser import EventDataParser
from parsers.TeamDataParser import TeamDataParser


class ClassicManager(Manager):
    def __init__(self, team_id, current_event, is_dgw=False, live_data_parser=None):
        super().__init__(team_id, current_event)
        self.__is_dgw = is_dgw
        self.__live_data_parser = live_data_parser

        self.row_num = 0

        [self.__total_points, self.overall_rank, self.__gw_points] = [0, 0, 0]

        self.__gw_points_string = ""
        self.__used_chips_string = ""

        [self.gw_transfers, self.gw_hits] = [0, 0]
        [self.__squad_value, self.__money_itb, self.team_value] = [0.0, 0.0, 0.0]

        self.__players_played = self.__dgw_players_played = ""

    def run(self):
        self.__init_all_properties()

    # This method is used a list of managers to get sorted by 'gw_points' attribute
    def gw_points(self):
        hit_cost = 4
        return self.__gw_points - self.gw_hits*hit_cost

    def to_list(self):
        result = [self.row_num, self.manager_name,
                  self.overall_rank, self.__total_points, self.__used_chips_string,
                  self.__gw_points_string, self.captain_name, self.vice_captain_name, self.active_chip,
                  self.__players_played,
                  self.gw_transfers, self.gw_hits,
                  self.__squad_value, self.__money_itb, self.team_value]

        if self.__is_dgw:
            result.insert(10, self.__dgw_players_played)

        return result

    """
    This method is used to format both overall_rank and total points columns before printing the SORTED array
    Will have effect once when any of the given players get higher than 999pts
    """
    def format_total_points_and_overall_rank(self):
        self.overall_rank = "{:,}".format(self.overall_rank)
        self.__total_points = "{:,}".format(self.__total_points)

    """
      This method is used to format gameweek points column before printing the SORTED array
      The point is to show a player's result concatenated with his hit(s) count (if any)
      Example: 42(-4)
      Explanation: gameweek score = 42 with 1 hit taken
    """
    def format_gw_points(self):
        self.__gw_points_string = str(self.__gw_points)

        if self.gw_hits != 0:
            self.__gw_points_string += "(-" + str(self.gw_hits*4) + ")"

    def format_players_played(self, count):
        self.__players_played = self.__players_played.format(count)

    def format_dgw_players_played(self, count, total_dgw_players):
        self.__dgw_players_played = "{} / {}".format(count, total_dgw_players)

    def get_id(self):
        return self._id

    def __init_all_properties(self):
        self.__team_data_parser = TeamDataParser(self._id)
        self.event_data_parser = EventDataParser(self._id, self._current_event)

        self.manager_name = self.__team_data_parser.get_manager_name()
        [self.__total_points, self.overall_rank, self.__gw_points] = self.__team_data_parser.get_ranks_and_points()

        # If any manager used none of their chips, the method will return "None"
        # Otherwise -- it returns a string of used chips, separated by commas.
        self.used_chips_by_gw = self.__team_data_parser.get_used_chips_by_gw()
        self.__used_chips_string = "None" if len(self.used_chips_by_gw) == 0 else ", ".join(self.used_chips_by_gw)

        [self.captain_id, self.vice_captain_id] = self.event_data_parser.get_captains_id()

        self.captain_name = self.event_data_parser.get_player_name(self.captain_id)
        self.vice_captain_name = self.event_data_parser.get_player_name(self.vice_captain_id)

        self.active_chip = self.event_data_parser.get_active_chip()
        [self.gw_transfers, self.gw_hits] = self.__team_data_parser.get_transfers()
        [self.__squad_value, self.__money_itb, self.team_value] = self.__team_data_parser.get_funds()

        [self.__players_played, self.players_ids] = self.event_data_parser.get_players_ids(self.active_chip)

        self.all_players_ids = self.event_data_parser.get_all_players_ids()

    @staticmethod
    def cmp_gw_pts(left, right):
        # calculating each manager gw points by substracting hits points
        left_gw_points = left.__gw_points - left.gw_hits*4
        right_gw_points = right.__gw_points - right.gw_hits*4

        if left_gw_points < right_gw_points:
            return 1
        elif left_gw_points > right_gw_points:
            return -1
        else:
            if left.overall_rank < right.overall_rank:
                return -1
            elif left.overall_rank == right.overall_rank:
                return 0
            else:
                return 1

    def __repr__(self):
        print(self.manager_name)

        print(self.__total_points)
        print(self.overall_rank)
        print(self.__gw_points)

        print(self.gw_transfers)
        print(self.gw_hits)

        print(self.__squad_value)
        print(self.__money_itb)
        print(self.team_value)

        print(self.__players_played)
