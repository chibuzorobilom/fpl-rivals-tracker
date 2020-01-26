from managers.Manager import Manager
from parsers.EventDataParser import EventDataParser
from parsers.TeamDataParser import TeamDataParser
from parsers.TransfersParser import TransfersParser


class TransfersManager(Manager):
    def __init__(self, id_, current_event, live_data_parser=None):
        super().__init__(id_, current_event)
        self.__live_data_parser = live_data_parser

        self.row_num = 0

    def run(self):
        self.__init_all_properties()

    # This method is used a list of managers to get sorted by 'outcome' field
    def outcome(self):
        return self.__outcome

    def format_outcome(self):
        sign = ""
        if self.__outcome > 0:
            sign = "+"

        self.__outcome = "{}{}".format(sign, self.__outcome)

    def to_list(self):
        if self.event_data_parser.get_active_chip() == "WC":
            self.sold_players = self.bought_players = "WC ACTIVE"

        result = [self.row_num, self.manager_name,
                  self.sold_players, self.bought_players,
                  self.gw_transfers, self.gw_hits,
                  self.__outcome, self.gw_points_string,
                  self.squad_value, self.money_itb, self.team_value]

        return result

    def to_list_gw(self):
        if self.active_chip == "WC" or self.active_chip == "FH":
            self.sold_players = self.bought_players = "{} ACTIVE".format(self.active_chip)

        result = [self.current_event, self.team_data_parser.get_overall_rank_in_specific_gw(self.current_event),
                  self.sold_players, self.bought_players,
                  self.gw_transfers, self.gw_hits,
                  self.__outcome]

        return result

    def get_wc_info(self):
        return self.__wc_info

    def __init_all_properties(self):
        self.team_data_parser = TeamDataParser(self.id_)
        self.event_data_parser = EventDataParser(self.id_, self.current_event)
        self.transfers_data_parser = TransfersParser(self.id_, self.current_event,
                                                     self.event_data_parser, self.__live_data_parser)

        self.manager_name = self.team_data_parser.get_manager_name()
        self.overall_rank = "{:,}".format(self.team_data_parser.get_ranks_and_points()[1])
        self.active_chip = self.event_data_parser.get_active_chip()

        transfers_ids = self.__init_transfers_ids()

        (self.sold_players, self.bought_players,
         self.sold_players_points, self.bought_players_points) = self.transfers_data_parser.get_transfers(transfers_ids)

        (self.gw_transfers, self.gw_hits) = self.team_data_parser.get_transfers_gw(self.current_event)
        self.__outcome = self.bought_players_points - self.sold_players_points - self.gw_hits*4

        self.gw_points_string = str(self.team_data_parser.get_ranks_and_points()[2])

        self.__wc_info = self.__init_wc_info()

        if self.gw_hits != 0:
            self.gw_points_string += "(-" + str(self.gw_hits * 4) + ")"

        (self.squad_value, self.money_itb, self.team_value) = self.team_data_parser.get_funds()

    def __init_wc_transfers_ids(self):
        players_ids_previous_gw = EventDataParser(self.id_, self.current_event - 1).get_players_ids("BB")[1]
        players_ids_current_gw = self.event_data_parser.get_players_ids("BB")[1]

        unique_players_prev_gw = players_ids_previous_gw - players_ids_current_gw
        self.__unique_players_curr_gw = players_ids_current_gw - players_ids_previous_gw

        transfers_ids = []
        for i in range(0, len(unique_players_prev_gw)):
            pair = (unique_players_prev_gw[i], self.__unique_players_curr_gw[i])
            transfers_ids.append(pair)

        return transfers_ids

    """
    transfers_ids are going to be set
    IF the active chip is WC or FH
    ELSE -> None
    """
    def __init_transfers_ids(self):
        transfers_ids = None

        if self.active_chip == "WC":
            self.gw_hits = "WC1" if self.current_event < 21 else "WC2"
            transfers_ids = self.__init_wc_transfers_ids()
        elif self.active_chip == "FH":
            self.gw_hits = "FH"
            transfers_ids = self.__init_wc_transfers_ids()

        return transfers_ids

    """
    That method handles the FH chip as well,
    which is actually a single GW wildcard
    """
    def __init_wc_info(self):
        if self.active_chip == "WC" or self.active_chip == "FH":
            self.gw_transfers = len(self.sold_players.split(','))

            sign = ""
            if self.__outcome > 0:
                sign = "+"

            return "[{} {}:]\nGW: {}\nTransfers Out: {}\nTransfers In: {}\nOutcome: {}{}"\
                   .format(self.manager_name, self.active_chip, self.current_event,
                           self.sold_players, self.bought_players,
                           sign, self.__outcome)
        else:
            return None