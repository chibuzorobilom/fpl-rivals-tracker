import time

from operator import methodcaller
from tabulate import tabulate

from managers.Rival import Rival
from menus.RivalsMenu import RivalsMenu

from parsers.LiveDataParser import LiveDataParser
from parsers.TeamDataParser import TeamDataParser


class ClassicAnalyzer:
    __LAST_EVENT = 38

    def __init__(self, path):
        start_time = time.time()

        self.__ids = ClassicAnalyzer.read_ids_from_file(path)

        # Create an object from TeamDataParser class to get current gw's number
        tmp_obj = TeamDataParser(1)
        self.__curr_event = tmp_obj.get_current_event()
        self.__is_dgw = self.__curr_event in tmp_obj.DGW
        self.__ldp = LiveDataParser(self.__curr_event, self.__is_dgw)

        self.__managers = self.__init_managers()
        self.__init_each_manager_players_played()

        execution_time = time.time() - start_time
        print("Data was collected for {:.2f} seconds".format(execution_time))

    def print_table(self):
        """
        menu returns an integer which indicates how the data is going to be sorted by:
        1: total points
        2: gameweek points
        """
        comparator = RivalsMenu.menu()

        # sort the data
        if comparator[0] == 1:
            self.__managers.sort(key=methodcaller(comparator[1]), reverse=False)
        else:
            self.__managers.sort(key=methodcaller(comparator[1]), reverse=True)

        row_num = 1

        # format some of its columns
        for manager in self.__managers:
            manager.format_total_points_and_overall_rank()
            manager.format_gw_points()

            manager.row_num = row_num
            row_num += 1

        # tabulate requires a list of lists, so that's why it's needed
        list_of_lists = [manager.to_list() for manager in self.__managers]

        headers = ["No", "Manager", "OR", "OP", "Used Chips",
                   "GW{} P".format(self.__curr_event),
                   "C".format(self.__curr_event),
                   "VC".format(self.__curr_event),
                   "Chip".format(self.__curr_event),
                   "PP",
                   "GW{} TM".format(self.__curr_event),
                   "GW{} H".format(self.__curr_event),
                   "SV", "Bank"]

        if self.__is_dgw:
            index = 10
            headers.insert(index, "PP II")

        print("\n> Legend: ")
        print("OR = Overall Rank, OP = Overall Points, P = Points, C = Captain, VC = Vice Captain, "
              "PP = Players Played, TM = Transfers Made, H = Hit(s), SV = *Squad* Value\n")

        # tablefmt="fancy_grid"
        print(tabulate(list_of_lists,
                       headers=headers,
                       tablefmt="orgtbl", floatfmt=".1f",
                       numalign="center", stralign="center"))

        formatter = "entry" if len(self.__managers) < 2 else "entries"
        print("\n{} {} were loaded successfully.".format(len(self.__managers), formatter))

    def print_stats(self):
        rivals_menu = RivalsMenu(self.__managers, self.__curr_event)
        rivals_menu.stats_menu()

    @staticmethod
    def read_ids_from_file(path, my_id=-1):
        with open(path, "r") as input_file:
            lines = input_file.readlines()
            ids = {line.rstrip('\n') for line in lines}

            """
            - this is used in HthAnalyzer class when you want to compare your team to some others
            - the point is to remove your id (if it exists) from the given file with ids
              because it's pointless to compare your team to itself 
            """
            ids.discard(my_id)

        return ids

    def __init_managers(self):
        threads = list(map(lambda id_: Rival(id_, self.__curr_event, self.__is_dgw), self.__ids))

        [thread.start() for thread in threads]
        [thread.join() for thread in threads]

        return threads

    def __init_each_manager_players_played(self):
        for manager in self.__managers:
            (sgw_players_count, dgw_players_info) = self.__ldp.count_players_played(manager.players_ids)
            manager.format_players_played(sgw_players_count)

            if self.__is_dgw:
                manager.format_dgw_players_played(*dgw_players_info)
