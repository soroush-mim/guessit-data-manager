from modules.resources.__handler import Resources
from bs4 import BeautifulSoup as soup
from modules.config.config import logger

import modules.config.config as config
import requests
import base64
import asyncio
import aiohttp
import time
import os
import re


download_page_dir = f'{config.main_dir}/download/page'


def collect_data_id_from_resource(pages, base, patterns):
    """
    general finding ids from list pages

    :param pages:
    :param base:
    :param patterns:
    :return:
    """

    logger.info(f'start collecting ids from {base}')
    new_ids = []

    for page in pages:

        logger.debug(f'collecting ids from {page}')
        
        souped_page = make_soup(page)

        for pattern in patterns:

            new_pages = [tag['href'] for tag in souped_page.find_all('a', {'href': re.compile(f'({base})?{pattern}')})]

            new_pages = [base + page if page.find('http') == -1 else page for page in new_pages]

            new_pages = [page for page in new_pages if page[5:].find('http') == -1]

            new_pages = [re.sub(r'/?\?.*', '', page) for page in new_pages]

            new_ids += [re.search(f'{base}{pattern}', page).group(1) for page in new_pages]

    return new_ids

#
# def wait_to_connect(timeout=10, delay=2):
#     connected = False
#     while not connected:
#         try:
#             getPage('https://www.google.com', timeout=timeout)
#             connected = True
#         except:
#             connected = False
#             time.sleep(delay)
#             print('no internet connection')


def get_resource_from_url(url):
    """
    getting resource of a url

    :param url:
    :return:
    """


    resources = []
    for resource in get_resources().keys():
        for db in list(get_resources()[resource].keys()):
            if 'base' in get_resources()[resource][db]:
                if any([get_resources()[resource][db]['base'] in url]):
                    resources.append(resource)
    if len(resources) > 0:
        return resources[0]
    else:
        return None


def get_db_name_from_url(url):
    """
    getting db_name of a url

    :param url:
    :return:
    """

    db_name = []
    resource = get_resource_from_url(url)
    if not resource:
        return None
    for db in get_resources()[resource].keys():
        for key, pattern in get_resources()[resource][db].items():
            if 'pattern' in key:
                if any([re.search(pattern, url)]):
                    db_name.append(db)
    if len(db_name) > 0:
        return db_name[0]
    else:
        return None


def get_guessed_location(url):
    """
    getting guessed_location of file that we can find them

    :param url:
    :return:
    """

    resource = get_resource_from_url(url)
    db_name = get_db_name_from_url(url)

    if resource and db_name:
        return f'{download_page_dir}/{resource}/{db_name}'
    else:
        return f'{download_page_dir}/others'


def download(url, local_filename=None):
    """

    :param url:
    :param local_filename:
    :return:
    """

    if local_filename is None:
        local_filename = url.split('/')[-1]
    else:
        local_filename += '/' + url.split('/')[-1]

    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    return local_filename


def make_soup(urls):
    """
    get the BeautifulSoup object of this page

    :param
    url (str): the url of page that we want

    :returns
    BeautifulSoup object: content of page of given url
    """
    """
    1. load the page
        for new urls:
            download the html and save it as html file in downloaded pages

        for old urls:
            loads html for them from files to memory

    2. return page as soup object

    """
    logger.debug(f'start make_soup for url = {urls}')

    if not isinstance(urls, list):

        location = get_guessed_location(urls)
        file_address = f"{location}/{base64.b64encode(urls.encode()).decode().replace('/', '-')}.html"

        if os.path.isfile(file_address):
            page_source = open(file_address, encoding='utf-8').read()
        else:
            page_source = get_page(urls)
            try:
                open(file_address, 'w+', encoding='utf-8').write(page_source)
            except Exception as error:
                logger.error(error)

        return soup(page_source , 'html.parser')

    else:
        download_pages(urls)


def get_page(url, try_count=10, delay=0):
    """
    download the given url by GET

    :param
    url (str): url address that we must download
    try_count (int): how many times we want to try
    delay (int): delay time between two try

    :returns
    str: html content of page
    """

    logger.debug(f'get_page started with url={url}, try_count={try_count}, delay={delay}')

    proxies = [{
                "http": None,
                "https": None,
              }]

    content = ''
    for i in range(try_count):
        try:
            content = requests.get(url, proxies=proxies[i % len(proxies)]).text
            break
        except Exception as error :
            logger.error(f'{url} : {error}')
            logger.info(f'could not get the page. trying again for {i}th time...')
            time.sleep(delay)

    if not content:
        logger.error(f'get_page FAILED! , could not get the page at last after {try_count} times of trying!')

    return content


def make_id(data_id):
    """
    make id from url

    :param data_id:
    :return:
    """
    return base64.b32encode(str(data_id).encode()).decode()


def get_resources(data_name=None):
    """

    :param data_name:
    :return:
    """
    if data_name is None:
        return Resources
    else:
        return [resource for resource in Resources.keys() if data_name in Resources[resource]]


def download_pages(url_list, workers=50, try_count=10, delay=1):
    """
    download a list of the urls and save them if you want

    :param url_list: list of urls that we want to download
    :param workers:
    :param try_count:
    :param delay:
    :return: list of responses
    """

    async def webpage_downloader(url, try_count, delay):
        """
        download one page by send get request to the url
        save the page and return it as string
        """

        file_address = f"{get_guessed_location(url)}/{base64.b64encode(url.encode()).decode().replace('/', '-')}.html"

        try:
            return {url: open(file_address, 'r').read()}
        except Exception as error:
            logger.debug(error)
        
        for i in range(try_count):
            try:
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector()) as session:
                    async with session.get(url) as resp:
                        site_html = await resp.text()

                        f = open(file_address, 'w+', encoding='utf8')
                        f.write(site_html)
                        f.close()
                        return {url: site_html}

            except Exception as error:
                await asyncio.sleep(delay)
                logger.info(error)

    def split_list(input_list, step):
        return [input_list[i-step:i] for i in range(step, len(input_list) + step, step)]

    async def async_handler(url_list, workers, try_count, delay):
        urls_splited = split_list(url_list, workers)
        responses = {}
        
        for urls in urls_splited:
            tasks = [asyncio.ensure_future(webpage_downloader(url, try_count, delay)) for url in urls]
            res_list = await asyncio.gather(*tasks)
            responses.update({list(res.keys())[0]: list(res.values())[0] for res in res_list})
        
        return responses
    
    loop = asyncio.get_event_loop()
    response = loop.run_until_complete(async_handler(url_list, workers, try_count, delay))
    loop.close()

    return response
