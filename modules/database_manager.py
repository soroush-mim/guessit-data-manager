import importlib
import json
import os
import re
import mistune
import time
import urllib
from pprint import pprint
from bs4 import BeautifulSoup
from modules.config.config import config, mongo_client
from modules.data_getters.__data_getters import *
from modules.resources.__handler import Resources
from modules import tools

import glob
import importlib
import re
import zlib

files = [re.search(r'.*?([A-Za-z_]*?).py', file).group(1) for file in
         glob.glob('./modules/data_getters/*.py') if not re.search(r'__[a-zA-Z_]*.py', file)]

for file in files:
    exec(f'from modules.data_getters.{file} import *')


class Resource():

    class DataGetterBaseClass:
        """ a parent class for all data getters classes that get page soup file for input """

        def __init__(self, page):
            self.page = page

        def get_all_data(self):
            """ a function for getting all data of a player and put it in a dictionary """
            data = {}
            for _property in [x for x in dir(self) if x.startswith('getter_')]:

                try:
                    data[_property.replace('getter_', '')] = getattr(self, _property)

                except Exception as error:
                    data[_property.replace('getter_', '')] = None
                    logger.error(f'{_property} : {error}')

            return data


        
    def __collect_data_id_from_resource(self , pages , pattern):
        """
        general finding ids from list pages

        :param pages:
        :param base:
        :param patterns:
        :return:
        """

        base = re.search(r'.*?\((.*?)\).*',pattern).group(1)
        pages_compressed_html = download_pages(pages)
        for page in pages:
            logger.debug(f'collecting ids from {page}')

            souped_page = soup(compressed_to_str(pages_compressed_html.pop(page)), features='lxml')

            new_pages = [tag['href'] for tag in souped_page.find_all('a', {'href': re.compile(f'{pattern}')})]

            new_pages = [base + page if page.find('http') == -1 else page for page in new_pages]

            new_pages = [page for page in new_pages if page[5:].find('http') == -1]

            new_pages = [re.sub(r'/?\?.*', '', page) for page in new_pages]


        return new_pages


    def find_ids(self , pages , pattern):

        resource = self.__class__.__name__.split('_')[1]

        logger.critical(f'getting ids for {resource} resource')
        
        id_list = list(set(self.__collect_data_id_from_resource(pages, pattern)))

        logger.critical(f'ids collected for {resource} resource')

        # logger.info(f'saving {self.db_name} to mongo ...')
        # mongo_client['datasets'][self.db_name].insert_many(db)
        # logger.info(f'saving {self.db_name}: done.')
        
        return id_list


class footballPlayer_sofifa(Resource):

    def __init__(self):
        self.type = 'wabpage'

    def find_ids(self):
        id_pages  = [f'https://sofifa.com/players?offset={i}' for i in range(0, 15000, 60)]
        pattern = f"({re.escape('https://sofifa.com')})?"+ r'(\/player\/[0-9]*).*?$'
        super(footballPlayer_sofifa , self ).find_ids(id_pages , pattern)

    class Getter_footballPlayer_sofifa(super.DataGetterBaseClass):
        """
        a class for getting footballPlayers data from sofifa 
        that get page soup file for input with 39 property
        """

        def __init__(self, page):

            super.DataGetterBaseClass.__init__(self, page)

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
        def getter_height_in_cm(self):
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
        def getter_contract_valid_until(self):
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
        
        @property
        def getter_popularity(self):
            return self.getter_International_Reputation * 10 + self.getter_likes_num  + self.getter_value_in_euro / (1000*1000)


    
    def get_data(self , id):
            getter = Getter_footballPlayer_sofifa(make_soup(id))
            return getter.get_all_data()



class Dataset():

    def __init__(self):
        pass

    def load(self):
        """
        open the json file if that is created already
        else create it and open it for find db

        :param db_name:
        :return:
        """
        dataset_name = self.__class__.__name__
        logger.info(f'trying to load {dataset_name} dataset from hard disk...')
        # db = list(mongo_client['datasets'][self.db_name].find())
        try:
            db = json.load(open(f'{config.dir.dataset}/{data}db.json', 'r'), encoding='utf-8')
        except:
            logger.debug(f'there is no {dataset_name} file in dataset directory')
            logger.info(f'crating a new json file for {dataset_name} dataset')

            open(f'{config.dir.dataset}/{dataset_name}db.json', 'w+').write('[]')
            db = json.load(open(f'{config.dir.dataset}/{dataset_name}db.json', 'r'), encoding='utf-8')


        logger.info(f'loading {dataset_name} dataset from hard disk is done.')

        return db
    
    def save(self , db):
        """
        save objects on a json file for find db

        :param db:
        :param db_name:
        :return:
        """
        dataset_name = self.__class__.__name__
        logger.info('Writing to file ...')

        # mongo_client.datasets[self.db_name].update({}, {'$set': db}, upsert=True, multi=True)
        json.dump(db, open(f'{config.dir.dataset}/{dataset_name}db.json', 'w'), indent=4)

        logger.info('Writing to file is done.')
        return True


class footballPlayer(Dataset):
    def __init__(self):
        self.resources = ['sofifa']

    


    def find_new_data(self):
        dataset = []
        for resource in self.resources:
            res = globals()[f'footballPlayer_{resource}']()
            ids = res.find_ids()
            dataset += [{f'{resource}_id': _id} for _id in ids]
            Dataset.save(self , dataset)





    def update(self):
        dataset = Dataset.load(self )
        for item in dataset:
            res_name = [i.replace('_id' , '') for i in item.keys() if i.endswith('_id')][0]
            res = globals()[f'footballPlayer_{res_name}']()
            item.update(res.get_data(item[f'{res_name}_id']))

    def merge(self):
        pass
    
    def schema_test(self):
        pass


class dataset():


    def __init__(self , db_name):
        
        
        self.db_name = db_name
        logger.debug(f'an instance from dataset class with db_name = {db_name} has been created')

    def download_resources(self):
        """
        download all the data from web

        downloading wanted pages for
        a specific pair of resource and db
        and saving them with make_soup

        :param

        resource (str): name of site.
            - example: 'sofifa', 'imdb'

        db_name (str): data name. example:
            - example: 'footballdb', 'playerdb'

        :returns
        None: function has no return

        """
        for resource in [resource for resource in Resources.keys() if self.db_name in Resources[resource]]:
            logger.critical(f'downloading resources for {self.db_name} dataset from {resource} resource')

            base_url = Resources[resource][self.db_name]['base']
            page_queue_urls = Resources[resource][self.db_name][f'{self.db_name}_list']

            patterns = [Resources[resource][self.db_name][x] for x in Resources[resource][self.db_name] if
                        x.endswith('_pattern')]

            page_queue_compressed_htmls = download_pages(page_queue_urls)
            urls_for_download = []
            for page_url in page_queue_urls:
                logger.debug(f'go for find links in {page_url}')
                souped_page = soup(tools.compressed_to_str(page_queue_compressed_htmls.pop(page_url)), features='lxml')

                for pattern in patterns:
                    urls = list(map(lambda tag: tag['href'],
                                    souped_page.find_all('a', {'href': re.compile(pattern)})))
                    for url in urls:
                        urls_for_download.append(urllib.parse.urljoin(base_url, re.search(pattern, url).group(1)))

            download_pages(urls_for_download, return_bool=False)

            logger.critical(f'resources for {self.db_name} dataset from {resource} resource downloaded')

    def update(self, begin=None, end=None, updating_step=1):
        """
        update all data of one db

        :param db_name:
        :param begin:
        :param end:
        :param updating_step:
        :return:
        """
        logger.critical(f'update db for db_name={self.db_name} started.')
        try:
            db = self.__load()

        except Exception as error:
            raise FileExistsError(f'there is no {self.db_name} file in dataset directory, please first run "python app.py -r fd -db {self.db_name}"')
        
        begin = begin if begin is not None else 0
        end = end if end is not None else len(db)

        for i in range(begin, end, updating_step):
            db[i].update(self.__update_data(db[i]))


        logger.critical(f'update db for db_name={self.db_name} finished.')
        self.__save(db)

    def __update_data(self, data):
        """
        use dataGetters classes for collecting data
        using it's resource_id

        :param db_name:
        :param data:
        :return:
        """

        new_data = {}
        for resource in get_resources(self.db_name):
            data_id_name = f'{resource}_id'
            logger.info(f'updating data => db_name:"{self.db_name}" {data_id_name}="{data[data_id_name]}" fields_len="{len(data)}"')

            if data_id_name in data:

                data_id = data[f'{data_id_name}']
                page_link = Resources[resource][self.db_name][self.db_name].format(data_id=data_id)
                page = make_soup(page_link)

                getter_obj = globals()[f'Getter_{self.db_name}_{resource}'](page)
                new_data.update(getter_obj.get_all_data())

            # logger.info(f'"{db_name}" data from "{resource}" resource updated successfully')

        return new_data

    def __load(self):
        """
        open the json file if that is created already
        else create it and open it for find db

        :param db_name:
        :return:
        """

        logger.info(f'trying to load {self.db_name} dataset from hard disk...')
        # db = list(mongo_client['datasets'][self.db_name].find())
        db = json.load(open(f'{config.dir.dataset}/{self.db_name}db.json', 'r'), encoding='utf-8')

        logger.info(f'loading {self.db_name} dataset from hard disk is done.')

        # except Exception as error:

        #     logger.error(f'cant load {db_name}dataset from hard disk , error = {error}')
        #     logger.info(f'opening a new json file for {db_name} dataset')

        #     open(f'{config.dir.dataset}/{db_name}db.json', 'w+').write('[]')
        #     db = json.load(open(f'{config.dir.dataset}/{db_name}db.json', 'r'), encoding='utf-8')

        return db
    
    def __save(self , db):
        """
        save objects on a json file for find db

        :param db:
        :param db_name:
        :return:
        """

        logger.info('Writing to file ...')

        # mongo_client.datasets[self.db_name].update({}, {'$set': db}, upsert=True, multi=True)
        json.dump(db, open(f'{config.dir.dataset}/{self.db_name}db.json', 'w'), indent=4)

        logger.info('Writing to file is done.')
        return True

    def find_ids(self):
        """
        finding ids and saving them in a json file for each db

        :param db_name:
        :return:
        """

        try:
            db = self.__load()
        except:
            logger.debug(f'there is no {self.db_name} file in dataset directory, please first run "python app.py -r fd -db {self.db_name}"')
            logger.info(f'crating a new json file for {self.db_name} dataset')

            open(f'{config.dir.dataset}/{self.db_name}db.json', 'w+').write('[]')
            db = json.load(open(f'{config.dir.dataset}/{self.db_name}db.json', 'r'), encoding='utf-8')


        for resource in get_resources(self.db_name):
            logger.critical(f'getting ids for {resource} resource')

            pages = get_resources()[resource][self.db_name][f'{self.db_name}_list']
            base = get_resources()[resource][self.db_name]['base']

            patterns = [get_resources()[resource][self.db_name][pattern] for pattern in get_resources()[resource][self.db_name] if
                        pattern.endswith('pattern')]

            id_list = list(set(collect_data_id_from_resource(pages, base, patterns)))
            db += [{f'{resource}_id': _id} for _id in id_list]

            logger.critical(f'ids collected for {resource} resource')

        # logger.info(f'saving {self.db_name} to mongo ...')
        # mongo_client['datasets'][self.db_name].insert_many(db)
        # logger.info(f'saving {self.db_name}: done.')
        
        self.__save(db)

    def start(self):

        logger.debug(f'starting start func from class dataset with db_name = {self.db_name}')
        self.download_resources()
        self.find_ids()
        self.update()
        self.schema_test()

    def schema_test(self):
        db = self.__load()
        items = {}

        logger.info(f'reading data catalog for db = {self.db_name}')
        with open(f'/root/guessit/guessit-question-manager/data_catalogs/{self.db_name}.md', "r") as reg_file :
            reg_soup = BeautifulSoup(mistune.markdown(reg_file.read()) , 'lxml')
            rows = reg_soup.find_all('tr')

            for item in rows[1:]:
                temp = item.find_all('td')
                item = temp[0].text
                typee = temp[1].text
                reg = temp[2].text
                items[item] = (typee , reg)
        
        logger.info(f'reading data catalog for db = {self.db_name} is done')

        logger.info(f'cheking formats for db = {self.db_name}')
        for data in db:

                data['validation'] = True

                for key in list(data.keys())[:]:
                    if key in items.keys():
                        if ((items[key][0] == 'int' and type(data[key]) == type(1)) or (items[key][0] == 'string' and type(data[key]) == type('aa'))) and bool(re.compile(items[key][1]).match(str(data[key]))):
                            data[f'__{key}'] = True
                        else:
                            data[f'__{key}'] = False
                            data['validation'] = False
        logger.info(f'cheking formats for db = {self.db_name} is done')
        self.__save(db)



def init_project():
    """
    create needed folders for project
    and pages that will be downloaded

    :return:
    """

    logger.critical('starting init_project')

    for resource in get_resources():
        for db_name in get_resources()[resource]:

            directory = f'{config.dir.main}/download/page/{resource}/{db_name}/'
            if os.path.exists(directory):
                continue

            try:
                os.makedirs(directory)
            except Exception as error:
                logger.error(error)

    if not os.path.exists(f'{config.dir.dataset}'):
        os.makedirs(f'{config.dir.dataset}')
    if not os.path.exists(f'{config.dir.download_page}/others'):
        os.makedirs(f'{config.dir.download_page}/others')


def get_expired_data(db, begin, end):
    """
    getting expired data from begin to end
    by expiration_time in config

    :param db:
    :param begin:
    :param end:
    :return:
    """

    old_data = []

    for j in range(begin, end):
        if 'lastUpdate' not in db[j] or \
                not db[j]['lastUpdate'] or \
                not isinstance(db[j]['lastUpdate'], str):
            db[j]['lastUpdate'] = str(time.strftime('%a %b %d %H:%M:%S %Y', time.gmtime(0)))

        if time.strptime(db[j]['lastUpdate'], '%a %b %d %H:%M:%S %Y') < time.localtime(
                time.time() - config.expiration_time):
            old_data += [db[j]]

    return old_data


def init_db(db_name):
    """

    :param db_name:
    :return:
    """
    open(f'{config.dir.dataset}/{db_name}db.json', 'w+').write('[]')


"""def check_get_function(data_name, resource, page_link):
    
    "
    :param data_name:
    :param resource:
    :param page_link:
    :return:
    "

    page = make_soup(page_link)

    getter_module = globals()[f'get_{data_name}_data_from_{resource}']

    modules = []
    new_data = {}
    for local_var in getter_module('get_locals'):
        if callable(getter_module(local_var)):
            modules += [getter_module(local_var)]

    for module in modules:
        try:
            new_data[module.__name__] = module(page)
        except Exception as error:
            logger.warning(f'no "{module.__name__}" from "{page_link}" becuase {error}')

    pprint(new_data)"""


# def download_db_link(url):
#     logger.critical(f'trying to download url : {url}')
#
#     sftp = ftp_connect()
#
#     new_url = url
#
#     try:
#         if re.search(r'.*?youtube\.com/watch.*', url):
#
#             file_name = youtube_downloader.download_music(url, str(int(time.time())))
#
#         else:
#
#             file_name = download(url)
#
#
#         file_address = f'{os.getcwd()}/{file_name}'
#
#         sftp.put(file_address, f'guessit/download/{file_name}')
#
#         new_url = f'http://51.255.213.191:3002/{file_name}'
#
#         logger.critical(file_address)
#
#         logger.critical('removing file ...')
#
#         os.remove(file_address)
#
#     except Exception as error:
#         logger.critical('llll')
#         logger.critical(error)
#
#     return new_url

#
# def download_db(db_name):
#     db = load_db(db_name)
#
#     for doc in db:
#
#         for field in doc:
#             logger.critical(field)
#             new_data = []
#
#             items = doc[field] if isinstance(doc[field], list) else [doc[field]]
#
#             if not isinstance(items[0], str) or items[0].find('http') == -1 or items[0].find('87.236.209.215') != -1:
#                 continue
#
#             for item in items:
#                 new_data += [download_db_link(item)]
#
#             doc[field] = new_data if isinstance(doc[field], list) else new_data[0]
#
#         save_db(db, db_name)
#
#         #sleep(10)


# # does not work yet
# def load_modules():
#     names = ['Amirabbas', 'Kiarash', 'Mohammad']
#     for name in names:
#         download(f'http://51.255.213.191/guessit/database/DataGetter_{name}.py')
#         module_file = importlib.import_module(f'DataGetter_{name}')
#
#         for module in [module for module in dir(module_file) if re.match('get.*', module)]:
#             print(module, name)
#             globals()[module] = getattr(module_file, module)


# def test_getter(data_name, resource, attributes=None,
#                   count=None, id_list=None, complete_report=True):
#     getter_modules = globals()[f'get_{data_name}_data_from_{resource}']
#     if attributes is None: attributes = getter_modules('get_locals')
#     db = load_db(data_name)
#     count = len(load_db(data_name)) if count is None else count
#     sample_data = random.sample(db, count)
#     data_ids = id_list if id_list else [new_data[f'{resource}ID'] for new_data in sample_data if
#       f'{resource}ID' in new_data] #find_db(data_name, resources=[resource], save_to_db=False, max_find_all=count)
#
#     test_results = []
#
#     for attribute in attributes:
#
#         failed_get_ids, failed_test_ids, all_datas = [], [], []
#
#         for data_id in data_ids:
#             page = make_soup(Resources[resource][db_name][db_name].format(data_id=data_id))
#
#             try:
#                 new_data = getter_modules(attribute)(page, test=True)
#                 logger.info(f'id = "{data_id}" ------- {attribute} = "{new_data}"')
#                 if new_data is None: failed_test_ids += [new_data]
#                 else: all_datas += [new_data]
#
#             except Exception as error:
#                 failed_get_ids += [data_id]
#                 logger.error(error)
#
#         test_result = {
#             'data_name'			: data_name,
#             'attribute'			: attribute,
#             'resource'			: resource,
#             'failed_get_ids'	: failed_get_ids,
#             'failed_tests_ids'	: failed_test_ids,
#
#             'success_rate'		: str((count - len(failed_get_ids) - len(failed_test_ids)) / count * 100) + '%'
#         }
#         if complete_report:
#             test_result = dict(list(test_result.items()) + list({
#                 'all_datas'		: all_datas
#             }.items()))
#
#         test_results += [test_result]
#
#     return test_results


# def download_resouce_page(resource, db_name):
#     with mp.Pool(10) as pool:
#         while 1:
#                 try:
#                     page_queue =
#                       json.load(open(f'{main_dir}/download/page/{resource}/{db_name}/statics.json'))['page_queue']
#                     break
#                 except: pass
#         step = 10
#         for i in range(0, len(page_queue), step):
#             while 1:
#                 try:
#                     page_queue =
#                       json.load(open(f'{main_dir}/download/page/{resource}/{db_name}/statics.json'))['page_queue']
#                     break
#                 except: pass
#             pool.map(make_soup, page_queue[i:i+step])

