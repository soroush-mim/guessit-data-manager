import re
import requests
from modules.data_getters.__baseClass import DataGetterBaseClass
from bs4 import BeautifulSoup


class Getter_footballLeague_soccerway(DataGetterBaseClass):
    """
    a class for getting footballleagues data from soccer way 
    that get page soup file for input 
    """
    def __init__(self , page):
        
        DataGetterBaseClass.__init__(self, page)
        self.subheading = page.find('div' , {'id' : re.compile(r'subheading')})
        self.table = page.find('div' , class_ = 'block_competition_league_table block block-nomb clearfix')
        self.scorers_table = page.find('table' , class_ = 'playerstats table')
        self.last_week_table = page.find('table' , {'class' : re.compile(r'matches(.)*')})
        self.archive_link = page.find('div' , {'id' : re.compile(r'subheading')}).find('div',{'class' : re.compile(r'clearfix')}).find_all('a')[-2]['href']

    @property
    def getter_league_name(self):
        return self.subheading.find('h1').text.strip()

    @property
    def getter_league_table(self):
        rows = self.table.find_all('tr' , {'class' : re.compile(r'team_rank(.)*')})
        ranks = []
        for i in rows:
            inf = {}
            inf['name'] = str(i.find('td' , class_ = 'text team large-link').text)
            inf['rank'] = int(i.find('td' , {'class' : re.compile(r'rank(.)*')}).text)
            inf['mp'] = int(i.find('td' , {'class' : re.compile(r'number total mp')}).text)
            inf['wins'] = int(i.find('td' , {'class' : re.compile(r'number total won(.)*')}).text)
            inf['draws'] = int(i.find('td' , {'class' : re.compile(r'number total drawn(.)*')}).text)
            inf['losts'] = int(i.find('td' , {'class' : re.compile(r'number total lost(.)*')}).text)
            inf['gf'] = int(i.find('td' , {'class' : re.compile(r'number total gf(.)*')}).text)
            inf['ga'] = int(i.find('td' , {'class' : re.compile(r'number total ga(.)*')}).text)
            inf['gd'] = int(i.find('td' , {'class' : re.compile(r'number gd')}).text)
            inf['points'] = int(i.find('td' , {'class' : re.compile(r'number points')}).text)
            l5=[]
            for j in i.find('td' , {'class' : re.compile(r'form')}).find_all('a'):
                game={}
                game['WDL'] = j.text
                game['title'] = j['title']
                game['link'] = j['href']
                l5.append(game)
            inf['last5'] = [l for l in l5]
            ranks.append(inf)
        return ranks

    @property
    def getter_scorers_table(self):
        scorers = []
        for i in self.scorers_table.find_all('tr' ,{'class' : re.compile(r'odd|even')} ):
            player = {}
            player['name'] = i.find('td' , {'class' : re.compile(r'player large-link')}).text
            player['link'] = i.find('td' , {'class' : re.compile(r'player large-link')}).find('a')['href']
            player['team'] = i.find('td' , {'class' : re.compile(r'team large-link')}).text
            player['team_link'] = i.find('td' , {'class' : re.compile(r'team large-link')}).find('a')['href']
            player['goals'] = int(i.find('td' , {'class' : re.compile(r'number goals')}).text)
            player['pnalties'] = int(i.find('td' , {'class' : re.compile(r'number penalties')}).text)
            scorers.append(player)
        return scorers

    @property
    def getter_last_week_table(self):
        last_week=[]
        for i in self.last_week_table.find_all('tr' )[1:]:
            game={}
            game['date'] = i.find('td' , {'class' : re.compile(r'date no-repetition')}).text
            game['teama'] = re.search(r'[A-Z]((.)*)[a-z]',i.find('td' , {'class' : re.compile(r'team team-a ')}).text.strip()).group()
            game['teama_link'] = i.find('td' , {'class' : re.compile(r'team team-a ')}).find('a')['href']
            game['teamb'] = i.find('td' , {'class' : re.compile(r'team team-b ')}).text.strip()
            game['teamb_link'] = i.find('td' , {'class' : re.compile(r'team team-b ')}).find('a')['href']
            game['resualt'] = i.find('td' , {'class' : re.compile(r'score-time score')}).text.strip()
            game['match_link'] = i.find('td' , {'class' : re.compile(r'score-time score')}).find('a')['href']
            last_week.append(game)
        
        return last_week

    @property
    def getter_league_archive(self):
        link = 'https://us.soccerway.com' + self.archive_link

        r = requests.get(link)
        archive_soup = BeautifulSoup( r.text , 'lxml')
        archive_table = archive_soup.find('table' , {'class' : re.compile(r'table')})
        archive = []
        for i in archive_table.find('tbody').find_all('tr'):
            l = {}
            l['year'] = i.find('td' , {'class' : re.compile(r'season')}).text.strip()
            try:
                l['year_link'] = i.find('td' , {'class' : re.compile(r'season')}).find('a')['href']
            except Exception as error:
                l['year_link'] = None
            l['winner'] = i.find('td' , {'class' : re.compile(r'text winner large-link')}).text.strip()
            l['winner'] = i.find('td' , {'class' : re.compile(r'text winner large-link')}).find('a')['href']
            l['Runner_up'] = i.find('td' , {'class' : re.compile(r'text runnerup large-link')}).text.strip()
            l['Runner_up_link'] = i.find('td' , {'class' : re.compile(r'text runnerup large-link')}).find('a')['href']
            archive.append(l)
        return archive
    