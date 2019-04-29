import re

from modules.data_getters.__baseClass import DataGetterBaseClass
from modules.data_getters.__tools import date_value, money_value


class Getter_footballPlayer_sofifa(DataGetterBaseClass):
    """
    a class for getting footballPlayers data from sofifa 
    that get page soup file for input with 38 property
    """

    def __init__(self, page):

        DataGetterBaseClass.__init__(self, page)

        self.main_table = page.find('div', class_='card card-border player fixed-width')

        self.top_row = self.main_table.find('div', class_='meta')

        self.columns = self.main_table.find_all('div', class_='columns')[1].find_all('div', class_='column col-4')

        self.left_column_elements = self.columns[0].find_all('li')

        self.third_column = []
        
        if len(self.columns) > 2:
            self.third_column = self.columns[2].find_all('li')

        self.forth_column = []

        self.hashtags_table = self.main_table.find('div', class_='mt-2').find_all('a')

        self.like_table = self.main_table.find('div', class_='operation mt-2')

        if len(self.columns) > 3:
            self.forth_column = self.columns[3].find_all('li')

        if len(self.third_column) < 5:
            self.third_column, self.forth_column = self.forth_column, self.third_column

    @property
    def getter_shirt_name(self):
        return re.search(r'.*\(', self.main_table.find('div', class_='info').text.strip()).group()[:-1]

    @property
    def getter_name(self):
        return re.search(r'((.*?)  )', self.top_row.text.strip()).group()[:-2].strip()

    @property
    def getter_age(self):
        return int(re.search(r'\d\d\d?', self.top_row.text.strip()).group().strip())

    @property
    def getter_nationality(self):
        return self.top_row.find('a', {'href': re.compile(r'\/players\?na.*')})['title']

    @property
    def getter_photo_link(self):
        return self.main_table.find('img')['data-src']

    @property
    def getter_id(self):
        return int(re.search(r'\d+', self.main_table.find('div', class_='info').find('h1').text.strip()).group())

    @property
    def getter_positions(self):
        positions_str = re.search(r'  .*A', self.top_row.text.strip()).group()[2:-1].strip()
        return positions_str.split()

    @property
    def getter_birth_date(self):
        birth_date = re.search(r'\d \(.*, \d\d\d\d\)', self.top_row.text.strip()).group()[3:-1]
        date = ''
        for item in date_value(birth_date):
            date += str(item) + '/'
        return date[:-1]

    @property
    def getter_weight_in_pond(self):
        return int(re.search(r'\d?\d\d\dlbs', self.top_row.text.strip()).group().strip()[:-3])

    @property
    def getter_weight_in_kg(self):
        return self.getter_weight_in_pond * 0.453592

    @property
    def getter_height_in_cnm(self):
        dirty_height = re.search(r'\d\d?.\d\d?\"', self.top_row.text.strip()).group().strip()
        return int(dirty_height[0]) * 30.28 + int(re.search(r'\'.*"', dirty_height).group().strip()[1:-1]) * 2.54

    @property
    def getter_value_in_euro(self):
        value = \
            self.main_table.find('div', class_='card-body stats').find_all('div', class_='column col-4 text-center')[
                2].find('span').text.strip()
        return money_value(value)

    @property
    def getter_wage(self):
        value = \
            self.main_table.find('div', class_='card-body stats').find_all('div', class_='column col-4 text-center')[
                3].find('span').text.strip()
        return money_value(value)

    @property
    def getter_overall_rating(self):
        return int(
            self.main_table.find('div', class_='card-body stats').find_all('div', class_='column col-4 text-center')[
                0].find('span').text.strip())

    @property
    def getter_potential(self):
        return int(
            self.main_table.find('div', class_='card-body stats').find_all('div', class_='column col-4 text-center')[
                1].find('span').text.strip())

    @property
    def getter_foot(self):
        return re.search(r'(Left)|(Right)', self.left_column_elements[0].text).group().strip()

    @property
    def getter_International_Reputation(self):
        return int(self.left_column_elements[1].text.strip()[-1])

    @property
    def getter_weak_foot_star(self):
        return int(self.left_column_elements[2].text.strip()[-1])

    @property
    def getter_skill_moves(self):
        return int(self.left_column_elements[3].text.strip()[-1])

    @property
    def getter_work_rate(self):
        return self.left_column_elements[4].text.strip()[9:]

    @property
    def getter_body_type(self):
        return self.left_column_elements[5].text.strip()[9:]

    @property
    def getter_real_face(self):
        return self.left_column_elements[6].text.strip()[9:]

    @property
    def getter_release_clause(self):
        try:
            release_clause = self.left_column_elements[7].text.strip()[14:]
        except Exception as error:
            return None
        return money_value(release_clause)

    @property
    def getter_club_team(self):
        return self.third_column[0].text.strip()

    @property
    def getter_club_team_id_sofifa(self):
        return int(re.search(r'\/\d*\/', self.third_column[0].find('a', {'href': re.compile(r'\/team\/.*')})[
            'href']).group().strip()[1:-1])

    @property
    def getter_power_in_club(self):
        return int(self.third_column[1].text.strip())

    @property
    def getter_Position_in_club(self):
        return self.third_column[2].text.strip()[-2:]

    @property
    def getter_Jersey_Number_in_club(self):
        return int(self.third_column[3].text.strip()[13:])

    @property
    def getter_club_join_date(self):
        join_date = self.third_column[4].text.strip()[6:]
        date = ''
        for item in date_value(join_date):
            date += str(item) + '/'
        return date[:-1]

    @property
    def getter_Contract_Valid_Until(self):
        return int(self.third_column[5].text.strip()[-4:])

    @property
    def getter_national_team(self):
        if len(self.forth_column) > 0:
            return self.forth_column[0].text.strip()
        else:
            return None

    @property
    def getter_national_team_id(self):
        if len(self.forth_column) > 0:
            return int(re.search(r'\/\d*\/', self.forth_column[0].find('a', {'href': re.compile(r'\/team\/.*')})[
                'href']).group().strip()[1:-1])
        else:
            return None

    @property
    def getter_power_in_national(self):
        if len(self.forth_column) > 0:
            return int(self.forth_column[1].text.strip())
        else:
            return None

    @property
    def getter_Position_in_national(self):
        if len(self.forth_column) > 0:
            return self.forth_column[2].text.strip()[-2:]
        else:
            return None

    @property
    def getter_Jersey_Number_in_national(self):
        if len(self.forth_column) > 0:
            return int(self.forth_column[3].text.strip()[13:])
        else:
            return None

    @property
    def getter_abilities_hashtags(self):
        return [i.text for i in self.hashtags_table]

    @property
    def getter_followers_num(self):
        return int(self.like_table.find('a', class_="follow-btn btn").find('span').text.strip())

    @property
    def getter_likes_num(self):
        return int(self.like_table.find('a', class_="like-btn btn").find('span').text.strip())

    @property
    def getter_dislikes_num(self):
        return int(self.like_table.find('a', class_="dislike-btn btn").find('span').text.strip())
