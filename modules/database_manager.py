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

    def __init__(self,collection,resource):
        self.collection = collection
        self.resource = resource


class webpage_resource(Resource):

    def __init__(self,collection,resource):
        resource.__init__(self,collection,resource)

    def find_ids(self):
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

