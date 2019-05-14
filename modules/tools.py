import asyncio
import hashlib
import os
import re
import time
import zlib

import aiohttp
import requests
from bs4 import BeautifulSoup as soup

from modules.config.config import config
from modules.config.config import logger
from modules.resources.__handler import Resources


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

    pages_html = download_pages(pages)
    for page in pages:

        logger.debug(f'collecting ids from {page}')

        souped_page = soup(zlib.decompress(pages_html.pop(page)), features='lxml')

        for pattern in patterns:
            new_pages = [tag['href'] for tag in souped_page.find_all('a', {'href': re.compile(f'({base})?{pattern}')})]

            new_pages = [base + page if page.find('http') == -1 else page for page in new_pages]

            new_pages = [page for page in new_pages if page[5:].find('http') == -1]

            new_pages = [re.sub(r'/?\?.*', '', page) for page in new_pages]

            new_ids += [re.search(f'{base}{pattern}', page).group(1) for page in new_pages]

    return new_ids


def get_guessed_file_address(url):
    """
    getting guessed_location of file that we can find them

    :param url:
    :return:
    """

    def get_db_name_from_url(_url, _resource):

        if not _resource:
            return None

        _db_name = []
        for db in get_resources()[_resource].keys():
            for key, pattern in get_resources()[_resource][db].items():
                if 'pattern' in key:
                    if any([re.search(pattern, _url)]):
                        _db_name.append(db)

        return _db_name[0] if len(_db_name) > 0 else None

    def get_resource_from_url(_url):

        resources = []
        for _resource in get_resources().keys():
            for db in list(get_resources()[_resource].keys()):
                if 'base' in get_resources()[_resource][db]:
                    if any([get_resources()[_resource][db]['base'] in _url]):
                        resources.append(_resource)

        return resources[0] if len(resources) > 0 else None

    def get_guessed_directory(_url):

        resource = get_resource_from_url(_url)
        db_name = get_db_name_from_url(_url, resource)

        if resource and db_name:
            return f'{config.dir.download_page}/{resource}/{db_name}'
        else:
            return f'{config.dir.download_page}/others'

    def md5_encode(text):
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    # main function
    return f"{get_guessed_directory(url)}/{md5_encode(url)}.html"


def make_soup(url):
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

    if isinstance(url, list):
        raise MemoryError('to avoid memory overflow please use download_pages function for download list of pages')

    file_address = get_guessed_file_address(url)

    if os.path.isfile(file_address):
        logger.debug(f'already downloaded {url}')
        page_source = open(file_address, encoding='utf-8').read()
    else:
        logger.debug(f'start downloading {url}')
        page_source = get_page(url)
        try:
            open(file_address, 'w+', encoding='utf-8').write(page_source)
        except Exception as error:
            logger.error(error)

    return soup(zlib.decompress(page_source), features='lxml')


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
    logger.critical(f'some page is not downloaded before here. url= {url}')

    proxies = [{
        "http": None,
        "https": None,
    }]

    content = ''
    for i in range(try_count):
        try:
            content = zlib.compress(requests.get(url, proxies=proxies[i % len(proxies)]).text.encode('utf-8'))
            break
        except Exception as error:
            logger.error(f'error in downloading {url} : {error}')
            time.sleep(delay)

    if not content:
        logger.error(f'download FAILED! , could not get the page after {try_count} times of trying!')

    return content


def get_resources(data_name=None):
    """

    :param data_name:
    :return:
    """
    if data_name is None:
        return Resources
    else:
        return [resource for resource in Resources.keys() if data_name in Resources[resource]]


def download_pages(url_list, workers=50, try_count=10, delay=1, return_bool=True):
    """
    download a list of the urls and save them if you want

    :param url_list: list of urls that we want to download
    :param workers:
    :param try_count:
    :param delay:
    :param return_bool:
    :return: list of responses
    """

    def split_list(input_list, step):
        return [input_list[i - step:i] for i in range(step, len(input_list) + step, step)]

    async def single_page_downloader(url, try_count, delay):
        """
        download one page by send get request to the url
        save the page and return it as string
        """

        file_address = get_guessed_file_address(url)

        try:
            output = {url: open(file_address, 'r').read()}
            logger.info(f'already downloaded {url}')
            return output if return_bool else None
        except FileNotFoundError as error:
            logger.info(f'start downloading {url}')

        for i in range(try_count):
            try:
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector()) as session:
                    async with session.get(url) as resp:
                        text = await resp.text()
                        text = text.encode('utf-8')
                        site_html = zlib.compress(text)

                        f = open(file_address, 'w+', encoding='utf8')
                        f.write(site_html)
                        f.close()
                        output = {url: site_html}
                        return output if return_bool else None

            except Exception as error:
                logger.error(f'try_time: {i}/{try_count}, when downloading {url}: {error}')
                await asyncio.sleep(delay)

        # urls that not downloaded
        # comes to here
        logger.error(f'download FAILED! , could not get the page after {try_count} times of trying!')

    async def async_handler(url_list, workers, try_count, delay, return_bool):
        """
        make tasks and run them in a queue
        :return dict of {url: html_page}
        """
        logger.debug(f'input urls for download are: {len(url_list)}')
        url_list = list(set(url_list))

        logger.debug(f'len the url_list after delete duplicates = {len(url_list)}')

        urls_splited = split_list(url_list, workers)

        responses = {}

        for urls in urls_splited:
            tasks = [asyncio.ensure_future(single_page_downloader(url, try_count, delay)) for url in urls]
            res_list = await asyncio.gather(*tasks)
            if return_bool:
                responses.update({list(res.keys())[0]: list(res.values())[0] for res in res_list})

        return responses if return_bool else None

    # main function

    logger.debug(f'start make_soup for url = '
                 f'{url_list if len(url_list) < 2 else str(url_list[:2]).replace("]", ", ...]")} len={len(url_list)}')

    loop = asyncio.new_event_loop()
    task = loop.create_task(async_handler(url_list, workers, try_count, delay, return_bool))
    response = loop.run_until_complete(task)
    loop.close()

    return response if return_bool else None
