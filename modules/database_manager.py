import importlib
import json
import os
import re
import time
import urllib
from pprint import pprint

import modules.config.config as config
from modules.data_getters.__data_getters import *
from modules.resources.__handler import Resources

import glob
import importlib
import re

files = [re.search(r'.*?([A-Za-z_]*?).py', file).group(1) for file in
         glob.glob('./modules/data_getters/*.py') if not re.search(r'__[a-zA-Z_]*.py', file)]

for file in files:
    exec(f'from modules.data_getters.{file} import *')


def init_project():
    """
    create needed folders for project
    and pages that will be downloaded

    :return:
    """

    logger.critical('starting init_project')

    for resource in get_resources():
        for db_name in get_resources()[resource]:

            directory = f'{config.main_dir}/download/page/{resource}/{db_name}/'
            if os.path.exists(directory):
                continue

            try:
                os.makedirs(directory)
            except Exception as error:
                logger.error(error)

    if not os.path.exists(f'{config.dataset_dir}'):
        os.makedirs(f'{config.dataset_dir}')
    if not os.path.exists(f'{config.download_page_dir}/others'):
        os.makedirs(f'{config.download_page_dir}/others')


def download_resources(resource, db_name):
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
    logger.critical(f'downloading resources for {db_name} dataset from {resource} resource')

    base_url = Resources[resource][db_name]['base']
    page_queue_urls = Resources[resource][db_name][f'{db_name}_list']

    patterns = [get_resources()[resource][db_name][x] for x in get_resources()[resource][db_name] if
                x.endswith('_pattern')]

    page_queue_htmls = download_pages(page_queue_urls)

    urls_for_download = []
    for page_url in page_queue_urls:
        logger.debug(f'go for find links in {page_url}')
        souped_page = soup(page_queue_htmls[page_url], features='html.parser')

        for pattern in patterns:
            urls = list(map(lambda tag: tag['href'],
                            souped_page.find_all('a', {'href': re.compile(pattern)})))
            for url in urls:
                urls_for_download.append(urllib.parse.urljoin(base_url, re.search(pattern, url).group(1)))

    download_pages(urls_for_download, return_bool=False)

    logger.critical(f'resources for {db_name} dataset from {resource} resource downloaded')


def update_db(db_name, begin=None, end=None, updating_step=1):
    """
    update all data of one db

    :param db_name:
    :param begin:
    :param end:
    :param updating_step:
    :return:
    """
    db = load_db(db_name)

    begin = begin if begin is not None else 0
    end = end if end is not None else len(db)

    for i in range(begin, end, updating_step):
        logger.critical(f'updating data number {i} in {db_name} dataset')

        db[i].update(update_data(db_name, db[i]))

        logger.critical(f'data number {i} in {db_name} dataset updated successfully')

    save_db(db, db_name)


def update_data(db_name, data):
    """
    use dataGetters classes for collecting data
    using it's resource_id

    :param db_name:
    :param data:
    :return:
    """

    logger.info(f'update_data started with data_name={db_name},  data={data}')
    new_data = {}
    for resource in get_resources(db_name):
        logger.info(f'starting to updating "{db_name}" data from "{resource}" resource')

        data_id_name = f'{resource}_id'
        if data_id_name in data:

            data_id = data[f'{data_id_name}']

            page_link = Resources[resource][db_name][db_name].format(data_id=data_id)

            page = make_soup(page_link)

            getter_module = globals()[f'Getter_{db_name}_{resource}'](page)

            new_data.update(getter_module.get_all_data())

        logger.info(f'"{db_name}" data from "{resource}" resource updated successfully')

    return new_data


def load_db(db_name):
    """
    open the json file if that is created already
    else create it and open it for find db

    :param db_name:
    :return:
    """

    try:
        logger.info(f'trying to load {db_name} dataset from hard disk...')

        db = json.load(open(f'{config.dataset_dir}/{db_name}db.json', 'r'), encoding='utf-8')

        logger.info(f'loading {db_name} dataset from hard disk is done.')

    except Exception as error:

        logger.error(f'cant load {db_name}dataset from hard disk , error = {error}')

        logger.info(f'opening a new json file for {db_name} dataset')

        open(f'{config.dataset_dir}/{db_name}db.json', 'w+').write('[]')

        db = json.load(open(f'{config.dataset_dir}/{db_name}db.json', 'r'), encoding='utf-8')

    return db


def save_db(db, db_name):
    """
    save objects on a json file for find db

    :param db:
    :param db_name:
    :return:
    """

    logger.info('Writing to file ...')

    json.dump(db, open(f'{config.dataset_dir}/{db_name}db.json', 'w'), indent=4)

    logger.info('Writing to file is done.')
    return True


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


def find_db(db_name):
    """
    finding ids and saving them in a json file for each db

    :param db_name:
    :return:
    """

    db = load_db(db_name)

    for resource in get_resources(db_name):
        logger.critical(f'getting ids for {resource} resource')

        pages = get_resources()[resource][db_name][f'{db_name}_list']
        base = get_resources()[resource][db_name]['base']

        patterns = [get_resources()[resource][db_name][pattern] for pattern in get_resources()[resource][db_name] if
                    pattern.endswith('pattern')]

        id_list = list(set(collect_data_id_from_resource(pages, base, patterns)))
        db += [{f'{resource}_id': _id} for _id in id_list]

        logger.critical(f'ids collected for {resource} resource')

    save_db(db, db_name)


def init_db(db_name):
    """

    :param db_name:
    :return:
    """
    open(f'{config.dataset_dir}/{db_name}db.json', 'w+').write('[]')


def check_get_function(data_name, resource, page_link):
    """

    :param data_name:
    :param resource:
    :param page_link:
    :return:
    """

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

    pprint(new_data)


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

