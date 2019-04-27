from modules.data_getters.__baseClass import DataGetterBaseClass
import re
from modules.data_getters.__tools import money_value

class Getter_footballTeam_sofifa(DataGetterBaseClass):
    """
    a class for getting footballTeams data from sofifa 
    that get page soup file for input 
    """

    def __init__(self, homepage_soup):
        self.rightSide_page = homepage_soup.select('div.columns')[2].select('ul.pl')[0].findAll('li')

        self.rating_row = homepage_soup.select('div.columns')[1].select('div')

        self.infoDiv = homepage_soup.select('div.info')[0]

        get_player_table = lambda player: (
            re.search('/[^/]*/[^/]*', player.select('td')[1].select('a')[1]['href'])[0],
            player.select('td')[1].select('a')[1]['title'])

        self.table_players_squad = homepage_soup.select('table.table-hover.persist-area')[0].select('tbody')[0].select('tr')

        self.table_players_onLoan = homepage_soup.select('table.table-hover.persist-area')[1].select('tbody')[0].select('tr')

    @property
    def getter_home_stadium(self):
        return self.rightSide_page[0].text.replace('Home Stadium', '').strip()


    @property
    def getter_rival_team(self):
        return self.rightSide_page[1].text.replace('Rival Team', '').strip()

    @property
    def getter_international_prestige(self):
        return self.rightSide_page[2].text.replace('International Prestige', '').strip()

    @property
    def getter_domestic_prestige(self):
        return self.rightSide_page[3].text.replace('Domestic Prestige', '').strip()

    @property
    def getter_transfer_budget(self):
        return self.rightSide_page[4].text.replace('Transfer Budget', '').strip()

    @property
    def getter_transfer_budget(self):
        return money_value(self.rightSide_page[4].text.replace('Transfer Budget', '').strip())

    @property
    def getter_starting_xi_average_age(self):
        return self.rightSide_page[5].text.replace('Starting XI Average Age', '').strip()

    @property
    def getter_whole_team_average_age(self):
        return self.rightSide_page[6].text.replace('Whole Team Average Age', '').strip()

    @property
    def getter_captain(self):
        return self.rightSide_page[7].find('a')['data-tooltip']

    @property
    def getter_short_free_kick(self):
        return self.rightSide_page[8].find('a')['data-tooltip']

    @property
    def getter_long_free_kick(self):
        return self.rightSide_page[9].find('a')['data-tooltip']

    @property
    def getter_left_short_free_kick(self):
        return self.rightSide_page[10].find('a')['data-tooltip']

    @property
    def getter_right_short_free_kick(self):
        return self.rightSide_page[11].find('a')['data-tooltip']

    @property
    def getter_penalties(self):
        return self.rightSide_page[12].find('a')['data-tooltip']

    @property
    def getter_left_corner(self):
        return self.rightSide_page[13].find('a')['data-tooltip']

    @property
    def getter_right_corner(self):
        return self.rightSide_page[14].find('a')['data-tooltip']

    @property
    def getter_overall(self):
        return self.rating_row[0].text.replace('Overall\xa0', '').strip()

    @property
    def getter_atack(self):
        return self.rating_row[1].text.replace('Attack\xa0', '').strip()

    @property
    def getter_midfield(self):
        return self.rating_row[2].text.replace('Midfield\xa0', '').strip()

    @property
    def getter_defence(self):
        return self.rating_row[3].text.replace('Defence\xa0', '').strip()

    






