from modules.data_getters.__baseClass import DataGetterBaseClass
import re
from modules.data_getters.__tools import money_value


class Getter_footballTeam_sofifa(DataGetterBaseClass):
    """
    a class for getting footballTeams data from sofifa 
    that get page soup file for input 
    """

    def __init__(self, page):
        DataGetterBaseClass.__init__(self, page)

        self.rightSide_page = page.select('div.columns')[2].select('ul.pl')[0].findAll('li')

        self.rating_row = page.select('div.columns')[1].select('div')

        self.infoDiv = page.select('div.info')[0]

        self.table_players_squad = \
            page.select('table.table-hover.persist-area')[0].select('tbody')[0].select('tr')

        if len(page.select('table.table-hover.persist-area')) > 1 :
            self.table_players_onLoan = \
                page.select('table.table-hover.persist-area')[1].select('tbody')[0].select('tr')
        else:
            self.table_players_onLoan = None
        
        self.kit_links = [i['src'] for i in page.find('aside').find_all('div' ,  {'class' : re.compile(r'card-body')})[-1].find_all('img')]


    def get_name_id_from_table(self,item):

        name = item.find_all('a' , {'href' : re.compile(r'\/player/\?*')})[0].text
        link = item.find_all('a' , {'href' : re.compile(r'\/player/\?*')})[0]['href']
        sofifa_id = int(re.search('r/\\d*' , link).group()[2:])
        return name , sofifa_id


    @property
    def getter_stadium(self):
        return self.rightSide_page[0].text.replace('Home Stadium', '').strip()

    @property
    def getter_rival(self):
        return self.rightSide_page[1].text.replace('Rival Team', '').strip()

    @property
    def getter_international_prestige(self):
        return self.rightSide_page[2].text.replace('International Prestige', '').strip()

    @property
    def getter_domestic_prestige(self):
        return self.rightSide_page[3].text.replace('Domestic Prestige', '').strip()

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
    def getter_attack(self):
        return self.rating_row[1].text.replace('Attack\xa0', '').strip()

    @property
    def getter_midfield(self):
        return self.rating_row[2].text.replace('Midfield\xa0', '').strip()

    @property
    def getter_defence(self):
        return self.rating_row[3].text.replace('Defence\xa0', '').strip()

    @property
    def getter_name(self):
        return re.sub(r'\(.*\)', '', self.infoDiv.find('h1').text).strip()

    @property
    def getter_team_id(self):
        return re.search(r'.*?\(ID: ([0-9]*?)\)', self.infoDiv.find('h1').text).group(1).strip()

    @property
    def getter_league(self):
        return self.infoDiv.select('a')[1].text.strip()

    @property
    def getter_league_link(self):
        return self.infoDiv.select('a')[1]['href']

    @property
    def getter_players(self):
        players = []
        for item in self.table_players_squad:
            players.append(self.get_name_id_from_table(item))
        return players

    @property
    def getter_players_on_loan(self):
        if self.table_players_onLoan:
            players = []  
            for item in self.table_players_onLoan:
                players.append(self.get_name_id_from_table(item))
            return players
        else: return None

    @property
    def getter_logo(self):
        return self.page.find('div' , {'class' : re.compile(r'card card-border player fixed-width')} ).find('img')['data-src'].strip()

    @property
    def getter_homekit(self):
        return self.kit_links[0]

    @property
    def getter_awaykit(self):
        return self.kit_links[1]

    @property
    def getter_thirdkit(self):
        return self.kit_links[2]

    @property
    def getter_gkkit(self):
        return self.kit_links[3]