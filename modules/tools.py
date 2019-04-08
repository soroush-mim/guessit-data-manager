from pymongo import MongoClient
import gzip
import shutil
import requests
from bs4 import BeautifulSoup as soup
import multiprocessing as mp
import datetime
import re
import pandas as pd
import json
from pprint import pprint
import psutil
import os
import html
import logging
import inspect
import functools
import itertools
import importlib
import pkgutil
import base64
import pysftp
import time
import glob

import config

download_page_dir 	= f'{config.main_dir}/download/page'

logging.basicConfig(format='### %(asctime)s - %(levelname)-8s : %(message)s \n',
					datefmt='%H:%M:%S',
					level=logging.INFO,
					handlers=[
						logging.FileHandler(f'{config.main_dir}/guessit_data_manager/modules/data_manager.log', mode='w+', encoding='utf8', delay=0),
						logging.StreamHandler()
					])

logger = logging.getLogger('DatabaseManager')


def collect_data_id_from_resource(pages, base, pattern, data_name=None, data_count=10, data_check_module=None, timeout=10**3, debug=False, checked_id=[], checked_pages=[], recursive=True):
	start_time 		= time.time()

	#print(pages, checked_id, data_count, checked_pages)

	for i, page in enumerate(list(set(pages) - set(checked_pages))):

		souped_page = make_soup(page)

		new_pages = [tag['href'] for tag in souped_page.find_all('a', {'href': re.compile(f'({base})?{pattern}')})] + [page]

		new_pages =  [base + page if page.find('http') == -1 else page for page in new_pages]

		new_pages =  [page for page in new_pages if page[5:].find('http') == -1]

		#print(new_pages)

		new_pages =  [re.sub(r'/?\?.*', '', page) for page in new_pages]

		new_pages = list(set(new_pages) - set(pages))

		#print(new_pages)

		for new_page in new_pages:

			if debug:
				try: print(i, new_page)
				except Exception as error: print(error)
				time.sleep(0.1)

			new_id_re = re.search(f'{base}{pattern}', new_page)
			#print('===')
			if new_id_re and new_id_re.group(1) not in checked_id and \
				not (data_name and data_check_module and not data_check_module(make_soup(new_page))):

				if debug or 1:
					try: print(new_page)
					except Exception as error: print(error)

				#yield new_id_re.group(1)

				checked_id = list(set(checked_id + [new_id_re.group(1)]))

				
				if data_count <= len(checked_id):
					logger.info('*****')
					logger.info(set(pages))
					logger.info(set(checked_pages))
					logger.info(set(checked_id))
					logger.info((data_count))
					return checked_id, pages, checked_pages


			else:
				#print('---')
				pass
			if recursive and re.search(f'{base}{pattern}', new_page) and new_page not in pages:
				pages += [new_page]


		if time.time() - start_time > timeout:
			return checked_id, pages, checked_pages


		checked_pages += [page]
	
	
	return checked_id, pages, checked_pages


def wait_to_connect(timeout=10, delay=2):
	connected = False
	while not connected:
		try:
			getPage('https://www.google.com', timeout=timeout)
			connected = True
		except:
			connected = False
			time.sleep(delay)
			print('no internet connection')


def ftp_connect(timeout=10):
	while timeout > 0:
		if 'sftp' in globals() and globals()['sftp'] and globals()['sftp'].pwd == '/root':
			break
		else:
			globals()['sftp'] = None

		cnopts = pysftp.CnOpts()

		cnopts.hostkeys = None

		globals()['sftp'] = pysftp.Connection(host='51.255.213.191', username='root', password='b7uxrE8ugOeiTHEl', cnopts=cnopts)

		timeout -= 1

	if globals()['sftp']:
		return globals()['sftp']

	else:
		raise NameError('sFTP connection failed')
		return


def download(url, local_filename=None):
	if local_filename is None:
		local_filename = url.split('/')[-1]
	else:
		local_filename += '/' + url.split('/')[-1]

	r = requests.get(url, stream=True)
	with open(local_filename, 'wb') as f:
		for chunk in r.iter_content(chunk_size=1024):
			if chunk:
				f.write(chunk)
				#f.flush() commented by recommendation from J.F.Sebastian
	return local_filename


def make_soup(url):
	try:
		resource = [resource for resource in get_resources().keys() if any([get_resources()[resource][db]['base'] in url for db in list(get_resources()[resource].keys()) if 'base' in get_resources()[resource][db]])][0] 
		db_name = [db for db in get_resources()[resource].keys() if any([re.search(pattern, url) for key, pattern in get_resources()[resource][db].items() if 'pattern' in key])][0]
		guessed_location = f'{download_page_dir}/{resource}/{db_name}'
	except Exception as error:
		logging.critical(f'function make_soup() {error}')
		guessed_location = download_page_dir

	location = guessed_location if location is None else location

	#url = re.sub('#.*?', '', url)
	#url = re.sub('ref[_]?=[a-zA-Z0-9_]*', '', url)
	#url = re.sub('[?]$', '', url)

		#sftp = ftp_connect()

	for file_address in glob.glob(f"{location}/{base64.b64encode(url.encode()).decode().replace('/', '-')}.html"):
		if os.path.isfile(file_address):# and os.access(file_address, os.R_OK):
			page_source = open(file_address, encoding='utf-8').read()

			logger.info(f'{(time.time() - start_time):.3f}s - reading page source from file ... {url}')

	if 'page_source' not in locals():

		page_source = get_page(url)

		file_address = f"{location}/{base64.b64encode(url.encode()).decode().replace('/', '-')}.html"
		try: open(file_address, 'w+', encoding='utf-8').write(page_source)
		except Exception as error: logger.error(f'could not save the page because {error} occured')

		if logger: logger.info(f'{(time.time() - start_time):.3f}s - downloding page source ... {url}')

		#sftp.open(file_address, 'w+').write(page_source)
	if return_local_save: return soup(page_source, 'html.parser'), use_local_save
	else: return soup(page_source, 'html.parser') 


def get_page(url, try_count=10, delay=0, **args):
	proxies = [{
				"http": None,
				"https": None,
			  }, {

			  }]

	content = ''
	for i in range(try_count):
		try	 :
			content = requests.get(url, proxies=proxies[i % len(proxies)], **args).text
			break
		except Exception as error :
			if logger: logging.error(f'{url} : {error}')
			if logger: logging.info(f'could not get the page. trying again for {i}th time...')
			time.sleep(delay)

	if not content:
		if logger: logging.error(f'could not get the page at last after {try_count} times of trying!')

	return content


def make_id(data_id):

	return base64.b32encode(str(data_id).encode()).decode()



def get_resources(data_name=None):
	return [resource for resource in config.resources.keys() if data_name in config.resources[resource]] if data_name else config.resources


def get_page_link(resource, data_name, attribute=None):
	"""gitting pages links from resources in config"""
	attribute = data_name if attribute is None else attribute
	return config.resources[resource][data_name][attribute]


"""
if __name__ == '__main__':

	url = 'https://sofifa.com/team/245716'
	try:

		resource = [resource for resource in get_resources().keys() if any([get_resources()[resource][db]['base'] in url for db in list(get_resources()[resource].keys()) if 'base' in get_resources()[resource][db]])][0] 
		print(resource)

		db_name = [db for db in get_resources()[resource].keys() if any([re.search(pattern, url) for key, pattern in get_resources()[resource][db].items() if 'pattern' in key])][0]
		guessed_location = f'{download_page_dir}/{resource}/{db_name}'
		print(guessed_location, db_name)
	except Exception as error:
		guessed_location = download_page_dir
		print(error)
"""