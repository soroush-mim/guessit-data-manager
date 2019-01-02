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
import math
import urllib

from tools import *

from DataGetters import *


class Monitoring:
	memuseme	= lambda : int(psutil.Process(os.getpid()).memory_info()[0] / 2. ** 30 * 1024)
	cpuuseme	= lambda : psutil.Process(os.getpid()).cpu_percent()
	cpuuse	  	= lambda : psutil.cpu_percent()
	memuse	  	= lambda : psutil.virtual_memory()[2]
	logMemory   = lambda : logger.info(f'memory usage : all = {memuse()} %  -  me = {memuseme()} MB')
	logCpu	  	= lambda : logger.info(f'cpu	usage : all = {cpuuse()} %  -  me = {cpuuseme()} % ')


def download_db_link(url):
	logger.critical(f'trying to download url : {url}')

	sftp = ftp_connect()

	new_url = url

	try:
		if re.search('.*?youtube\.com/watch.*', url):

			file_name = youtube_downloader.download_music(url, str(int(time.time())))

		else:

			file_name = download(url)


		file_address = f'{os.getcwd()}/{file_name}'

		sftp.put(file_address, f'guessit/download/{file_name}')

		new_url = f'http://51.255.213.191:3002/{file_name}'

		logger.critical(file_address)

		logger.critical('removing file ...')

		os.remove(file_address)

	except Exception as error:
		logger.critical('llll')
		logger.critical(error)

	return new_url


def download_db(db_name):
	db = load_db(db_name)

	for doc in db:

		for field in doc:
			logger.critical(field)
			new_data = []

			items = doc[field] if isinstance(doc[field], list) else [doc[field]]

			if not isinstance(items[0], str) or items[0].find('http') == -1 or items[0].find('87.236.209.215') != -1:
				continue

			for item in items:
				new_data += [download_db_link(item)]

			doc[field] = new_data if isinstance(doc[field], list) else new_data[0]

		save_db(db, db_name)

		#sleep(10)


def update_data(data_name, data):

	for resource in get_resources(data_name):

		data_id_name = f'{resource}ID'

		if data_id_name in data:

			data_id = data[f'{data_id_name}']

			page_link = get_page_link(resource, data_name).format(data_id=data_id)

			logger.info(f'trying to get info from link : {page_link}')

			page = make_soup(page_link)

			#logger.info(str(page)[:1000])

			new_data = {}

			#get_attributes(resource, data_name) + common_attributes

			getter_module = globals()[f'get_{data_name}_data_from_{resource}']

			modules = []

			for local_var in getter_module('get_locals'):
				if callable(getter_module(local_var)):
					modules += [getter_module(local_var)]

			for module in modules:
				try	 : new_data[module.__name__] = module(page)
				except Exception as error : logger.warning(f'no "{module.__name__}" from "{page_link}" becuase {error}')



			#def get_attribute_from_page(page, module):
			#		try:
			#			return (module.__name__, module(page), '')
			#		except Exception as error:
			#			return (module.__name__, '###', error)
			#
			#	attributes = pool.map_async(functools.partial(get_attribute_from_page, page), modules).get()
			#
			#	for attribute, value, error in attributes:
			#		if value != '###':
			#			new_data[attribute] = value
			#		else:
			#			logger.warning(f'no "{attribute}" from "{value}" becuase {error}')

			#logger.info(f'from "{page_link}" page got : {new_data}')

			#data.update(new_data)
			#pprint(new_data)
			for key in new_data: data[key] = new_data[key]
			#pprint(data)

	return data


def get_resources(data_name=None):
	return [resource for resource in resources.keys() if data_name in resources[resource]] if data_name else resources.keys()


def get_page_link(resource, data_name, attribute=None):
	attribute = data_name if attribute is None else attribute
	return resources[resource][data_name][attribute]


def load_db(db_name):

	try:
		logger.critical(f'trying to load {db_name} dataset from hard disk...')

		db = json.load(open(f'{dataset_dir}/{db_name}db.json', 'r'), encoding='utf-8')

		logger.critical(f'loading {db_name} dataset from hard disk is done.')

	except Exception as error:

		logger.error(error)

		logger.critical(f'could not open dataset from {dataset_dir}/ directory')

		logger.critical(f'trying to download {db_name} dataset from server...')

		db = json.loads(requests.get(f'{db_url}{db_name}db.json', 'r').text)

		logger.critical(f'loading {db_name} dataset from server is done.')


	if backup:

		logger.critical(f'taking backup from {db_name} dataset ...')

		json.dump(db, open(f"{dataset_dir}/{db_name}db {time.ctime().replace(':', '-')}.backup", 'w'), indent=4)

		logger.info(f'taking backup from {db_name} dataset is done.')

	return db


def save_db(db, db_name):
	logger.critical('Writing to file ...')

	json.dump(db, open(f'{dataset_dir}/{db_name}db.json', 'w'), indent=4)

	if safe_mode:
		json.dump(db, open(f'{dataset_dir}/{db_name}dbLastUpdate.json', 'w'), indent=4)

	logger.critical('Writing to file is done.')

	return True


def get_expired_data(db, begin, end):
	old_data = []
	for j in range(begin, end):
		if not 'lastUpdate' in db[j] or not db[j]['lastUpdate'] or not isinstance(db[j]['lastUpdate'], str):
			db[j]['lastUpdate'] = str(time.strftime('%a %b %d %H:%M:%S %Y', time.gmtime(0)))

		if time.strptime(db[j]['lastUpdate'], '%a %b %d %H:%M:%S %Y') < time.localtime(time.time() - expiration_time):
			old_data += [db[j]]

	return old_data


def update_db_partial(db, updated_items, begin=0, end=None):
	if end is None:
		end = len(db)

	changes = 0
	for j in range(begin, end):
		updated_data = [data for data in updated_items if data['id'] == db[j]['id']]

		if updated_data:
			updated_data = updated_data[0]
			updated_data['lastUpdate'] = time.ctime()

			for key in updated_data:
				if (key not in db[j] or db[j][key] != updated_data[key]):
					db[j][key] = updated_data[key]
					changes += 1

	return db, changes


def update_db(db_name, begin=0, end=None, timeout=10**4):

	db = load_db(db_name)
	if end is None:
		end = len(db)
	else:
		end = min(end, len(db))

	with mp.Pool() as pool:

		for i in range(begin, end, updating_step):

			Monitoring.logMemory()
			Monitoring.logCpu()
			logger.critical(f'Updating {db_name} dataset from {i} to {i + updating_step} ...')

			old_data = get_expired_data(db, begin=i, end=min(i + updating_step, end))

			logger.critical('Retrieving data ...')

			updated_items = pool.map_async(functools.partial(globals()['update_data'], db_name), old_data).get()

			logger.critical('Retrieving data is done.')

			db, changes = update_db_partial(db, updated_items, begin=i, end=min(i + updating_step, end))

			if changes > 0:
				save_db(db, db_name)

	logger.critical(f'{db_name} dataset updated successfully :)')


def find_db(db_name, max_find_new=10**4, max_find_all=10**4, max_db_all=10**6, timeout=10**5, save_to_db=True, resources=None):

	start_time = time.time()

	db = load_db(db_name)

	count_find_new, count_find_all = 0, 0

	logger.critical('trying to find new data...')

	changes = 0

	with mp.Pool(process_count) as pool:

		for resource in get_resources(db_name) if resources is None else resources:

			logger.critical(f'trying to find {db_name} data from {resource}.')

			data_id_name = f'{resource}ID'

			datas = [data[data_id_name] for data in db if data_id_name in data]

			resource_links = get_page_link(resource, db_name, f'{db_name}_list')

			logger.critical(f"resource links : {resource_links if len(resource_links) < 3 else str(resource_links[:3]) + '...'} ")

			new_datas, new_datas_all, checked_pages = [], [], []

			if f'collect_{db_name}_id_from_{resource}' not in globals(): break

			while len(db) < max_db_all and count_find_all < max_find_all and count_find_new < max_find_new:

				#print([x[f'{resource}ID'] for x in new_datas_all])

				new_datas, resource_links, checked_pages = zip(*pool.map(functools.partial(globals()[f'collect_{db_name}_id_from_{resource}'], checked_id=[x[f'{resource}ID'] for x in db], checked_pages=checked_pages, timeout=start_time - time.time() + timeout), [resource_links]))

				checked_pages = list(itertools.chain.from_iterable(list(checked_pages)))

				resource_links = list(itertools.chain.from_iterable(list(resource_links)))

				#print(new_datas)

				new_datas = set(list(itertools.chain.from_iterable(list(new_datas))))

				logger.info(new_datas)

				count_find_all += len(new_datas)

				new_datas -= set([x[f'{resource}ID'] for x in db])

				logger.info(new_datas)

				count_find_new += len(new_datas)

				logger.critical(f'finding {db_name} data is done.')

				changes = len(new_datas)

				if save_to_db and changes > 0:
					db +=  [{'id': make_id(data_id), f'{resource}ID': data_id} for data_id in new_datas]
					save_db(db, db_name)



	#logger.critical(f"all new datas {new_datas if len(new_datas) < 3 else str(new_datas[:3]) + '...'}")


	logger.critical(f'{changes} number of new items added to {db_name} dataset successfully :)')

	return new_datas


def init_db(db_name):
	open(f'{dataset_dir}/{db_name}db.json', 'w+').write('[]')


def save_pages(url, patterns):
	return

# does not work yet
def load_modules():
	names = ['Amirabbas', 'Kiarash', 'Mohammad']
	for name in names:
		download(f'http://51.255.213.191/guessit/database/DataGetter_{name}.py')
		module_file = importlib.import_module(f'DataGetter_{name}')

		for module in [module for module in dir(module_file) if re.match('get.*', module)]:
			print(module, name)
			globals()[module] = getattr(module_file, module)


def check_get_function(data_name, resource, page_link):
	page = make_soup(page_link)

	getter_module = globals()[f'get_{data_name}_data_from_{resource}']

	modules = []
	new_data = {}
	for local_var in getter_module('get_locals'):
		if callable(getter_module(local_var)):
			modules += [getter_module(local_var)]

	for module in modules:
		try	 : new_data[module.__name__] = module(page)
		except Exception as error : logger.warning(f'no "{module.__name__}" from "{page_link}" becuase {error}')

	pprint(new_data)


def test_getter(data_name, resource, attr=None, test_count=20):
	getter_module = globals()[f'get_{data_name}_data_from_{resource}']
	module = getter_module(attr)
	data_ids = [new_data[f'{resource}ID'] for new_data in find_db(data_name, resources=[resource], save_to_db=False, max_find_all=test_count)]

	failed_data_ids = []

	for data_id in data_ids:
		page_link = make_soup(get_page_link(resource, data_name).format(data_id=data_id))
		try:
			print(module(page_link))
		except Exception as error:
			failed_data_ids += [data_id]
			print(error)

	test_result = {
		'data_name'			: data_name,
		'attr'				: attr,
		'resource'			: resource,
		'failed_data_ids'	: failed_data_ids,
		'success_rate'		: str((test_count - len(failed_data_ids)) / test_count * 100) + '%',

	}

	return test_result


def download_resources(resource, db_name, count_saves=float('Inf'), count_founds=float('Inf'), timeout=float('Inf'), page_queue=None, start=0):
	start_time = time.time()
	location = f'{main_dir}/download/page/{resource}/{db_name}/'
	base = get_page_link(resource, db_name, 'base')
	page_queue = get_page_link(resource, db_name, f'{db_name}_list') if page_queue is None else page_queue
	i = start
	while i < len(page_queue):
		page = page_queue[i]
		logger.info(f'Founded pages: {len(page_queue)} ------ Saved pages: {i}')
		souped_page = make_soup(page, location=location)
		patterns = [get_page_link(resource, db_name, f'{db_name}_pattern')]
		for pattern in patterns:
			for url in [tag['href'] for tag in souped_page.find_all('a', {'href': re.compile(pattern)})]:
				absolute_url = urllib.parse.urljoin(base, re.search(pattern, url).group(1))
				if absolute_url not in page_queue:
					page_queue += [absolute_url]
					if i >= count_saves or len(page_queue) >= count_founds or time.time() - start_time >= timeout:
						print(f'Donwloaded pages: {i}')
						return page_queue, i
		i += 1


def init_project():
	for resource in get_resources():
		for db_name in get_resources(resource):
			try: os.makedirs(f'{main_dir}/download/page/{resource}/{db_name}/');print(f'{main_dir}/download/page/{resource}/{db_name}/')
			except Exception as error: print(error)


resources	=   {
				'imdb': {
					'movie': {
						'movie_list': [f'https://www.imdb.com/search/title?title_type=feature&count={250}&start={i + 1}' for i in range(0, 10000, 250)]
									+ [f'https://www.imdb.com/search/title?title_type=feature&sort=num_votes,desc&count={250}&start={i + 1}' for i in range(0, 10000, 250)]
						,
						'movie': 'https://www.imdb.com/title/{data_id}'
						,
						'base': 'https://www.imdb.com'
						,
						'movie_pattern': f"({re.escape('title/')}[a-z0-9]*)/?.*?$"
					}
					,
					'actor': {
						'actor_list': [f'https://www.imdb.com/search/title?title_type=feature&count={250}&page={int((i+1)/250 + 1)}' for i in range(0, 10000, 250)]
									+ [f'https://www.imdb.com/search/title?title_type=feature&sort=num_votes,desc&count={250}&page={int((i+1)/250 + 1)}' for i in range(0, 10000, 250)]
						,
						'actor': 'https://www.imdb.com/name/{data_id}'
					}
					,
					'director': {
						'director_list': [f'https://www.imdb.com/search/title?title_type=feature&count={250}&page={int((i+1)/250 + 1)}' for i in range(0, 10000, 250)]
										+ [f'https://www.imdb.com/search/title?title_type=feature&sort=num_votes,desc&count={250}&page={int((i+1)/250 + 1)}' for i in range(0, 10000, 250)]
						,
						'director': 'https://www.imdb.com/name/{data_id}'
					}
				},
				'sofifa': {
					'footballPlayer': {
						'footballPlayer_list': [f'https://sofifa.com/players?offset={i}' for i in range(0, 15000, 60)]
						,
						'footballPlayer': 'https://sofifa.com/player/{data_id}'
					}
					,
					'footballTeam': {
						'footballTeam_list': [f'https://sofifa.com/teams?offset={i}' for i in range(0, 700, 60)]
						,
						'footballTeam': 'https://sofifa.com/team/{data_id}'
					}
				},
				'goodreads': {
					'book': {
						'book': 'https://www.goodreads.com/book/show/{data_id}'
						,
						'book_list': list(itertools.chain.from_iterable([[f'https://www.goodreads.com/book/popular_by_date/{i}/{j}' for j in range(1, 13)] for i in range(2010, 2018)]))
					}
					,
					'author': {
						'author': 'https://www.goodreads.com/author/show/{data_id}'
						,
						'author_list': list(itertools.chain.from_iterable([[f'https://www.goodreads.com/book/popular_by_date/{i}/{j}' for j in range(1, 13)] for i in range(2010, 2018)]))
					}
				},
				'cia': {
					'country': {
						'country': 'https://www.cia.gov/library/publications/the-world-factbook/geos/{data_id}.html'
						,
						'country_list': ['https://www.cia.gov/library/publications/the-world-factbook/docs/flagsoftheworld.html']
					}
				},
				'biography': {
					'people': {
						'people': 'https://www.biography.com/people/{data_id}'
						,
						'people_list': ['https://www.biography.com/people']
					}
				},
				'myanimelist': {
					'anime': {
						'anime': 'https://www.myanimelist.net/anime/{data_id}'
						,
						'anime_list': [f'https://myanimelist.net/topanime.php?limit={i}' for i in range(0, 20000, 50)]
					}
				},
				'discogs': {
					'song': {
						#'song': ''
						#,
						#'song_list': []
					}
					,
					'musicArtist': {
						'musicArtist': 'https://www.discogs.com/artist/{data_id}'
						,
						'musicArtist_list': [f'https://www.discogs.com/search/?sort=want%2Cdesc&type=artist&page={i}' for i in range(1, 200)]
					}
				},
				'merriam': {
					'word': {
						'word' : 'https://www.merriam-webster.com/dictionary/{data_id}'
						,
						'word_list' : list(itertools.chain.from_iterable([[f'https://www.merriam-webster.com/browse/dictionary/{char}/{i}' for i in range(1,100)] for char in "qwertyuiopasdfghjklzxcvbnm"]))
					}
				},
				'volleyballWorld': {
					'volleyballTeam': {
						'volleyballTeam': 'http://www.volleyball.world/en/men/teams/{data_id}'
						,
						'volleyballTeam_list': ['http://www.volleyball.world/en/men/teams']
					}
				},
				'theFamousPeople': {
					'celebrity': {
						'celebrity': 'https://www.thefamouspeople.com/profiles/{data_id}.php'
						,
						'celebrity_list' :list(itertools.chain.from_iterable([[f'https://www.thefamouspeople.com/{type}.php?page={i}' for i in range(1,10)] for type in ["singers"]]))
					}
				}
			}

main_dir			= '/home/flc/guessit'
project_dir			= f'{main_dir}/guessit_data_manager'
dataset_dir			= f'{project_dir}/data_manager/modules/datasets'
process_count	   	= 4
updating_step	   	= 10
finding_step	   	= 10
expiration_time	 	= 60 * 60 * 10
backup			  	= False
debug			   	= False
safe_mode		   	= False

sftp 				= None

if __name__ == '__main__':
	#init_db('movie')
	#find_db('movie')
	#update_db('movie')
	#download_db('movie')

	#for dataset in ['musicArtist']:
	#	init_db(dataset)
	#	find_db(dataset)
	#	update_db(dataset)

	#download_db('movie')

	#update_db('movie')

	#check_get_function('movie', 'imdb', 'https://www.imdb.com/title/tt2674426')

	#check_get_function('actor', 'imdb', 'https://www.imdb.com/name/nm0488953')

	#check_get_function('book', 'goodreads', 'https://www.goodreads.com/book/show/341879.Just_Kids')

	#check_get_function('author', 'goodreads', 'https://www.goodreads.com/author/show/196092.Patti_Smith')

	#sleep(100)

	#for dataset in datasets: init_db(dataset)

	#pprint(test_getter(data_name='director', resource='imdb', attr='birthdate', test_count=2))


	for dataset in []:
		init_db(dataset)
		find_db(dataset)
		update_db(dataset)
	
	init_project()
	
	download_resources('imdb', 'movie', count_saves=10**1 * 2)
#test_getter('footballTeam', 'sofifa')
