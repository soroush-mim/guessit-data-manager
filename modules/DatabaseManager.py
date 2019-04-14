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
import glob
import random
import argparse

import config
from tools import *
from DataGetters import *


class Monitoring:
	memuseme	= lambda : int(psutil.Process(os.getpid()).memory_info()[0] / 2. ** 30 * 1024)
	cpuuseme	= lambda : psutil.Process(os.getpid()).cpu_percent()
	cpuuse	  	= lambda : psutil.cpu_percent()
	memuse	  	= lambda : psutil.virtual_memory()[2]
	logMemory   = lambda : logger.info(f'memory usage : all = {Monitoring.memuse()} %  -  me = {Monitoring.memuseme()} MB')
	logCpu	  	= lambda : logger.info(f'cpu	usage : all = {Monitoring.cpuuse()} %  -  me = {Monitoring.cpuuseme()} % ')


def download_db_link(url):
	logger.critical(f'trying to download url : {url}')

	sftp = ftp_connect()

	new_url = url

	try:
		if re.search(r'.*?youtube\.com/watch.*', url):

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


			new_data = {}


			getter_module = globals()[f'get_{data_name}_data_from_{resource}']

			modules = []


			for key in new_data: data[key] = new_data[key]

	return data


def load_db(db_name):
	"""open the json file if that is created already else create it and open it for find db"""
	try:
		logger.critical(f'trying to load {db_name} dataset from hard disk...')

		db = json.load(open(f'{config.dataset_dir}/{db_name}db.json', 'r'), encoding='utf-8')

		logger.critical(f'loading {db_name} dataset from hard disk is done.')

	except Exception as error:

		logger.error(error)
		open(f'{config.dataset_dir}/{db_name}db.json', 'w+').write('[]')
		db = json.load(open(f'{config.dataset_dir}/{db_name}db.json', 'r'), encoding='utf-8')


	return db


def save_db(db, db_name):
	"""save objects on a json file for find db"""
	logger.critical('Writing to file ...')

	json.dump(db, open(f'{config.dataset_dir}/{db_name}db.json', 'w'), indent=4)

	logger.critical('Writing to file is done.')

	return True


def get_expired_data(db, begin, end):
	"""getting expired datas from begin to end by expiration_time in config"""
	old_data = []
	for j in range(begin, end):
		if not 'lastUpdate' in db[j] or not db[j]['lastUpdate'] or not isinstance(db[j]['lastUpdate'], str):
			db[j]['lastUpdate'] = str(time.strftime('%a %b %d %H:%M:%S %Y', time.gmtime(0)))

		if time.strptime(db[j]['lastUpdate'], '%a %b %d %H:%M:%S %Y') < time.localtime(time.time() - config.expiration_time):
			old_data += [db[j]]

	return old_data




def update_db(db_name, begin, end,updating_step = 1):
	
	db = load_db(db_name)
	begin = 0
	end = len(db)
	
	for i in range(begin, end, updating_step):

		old_data = get_expired_data(db, begin=i, end=min(i + updating_step, end))

		updated_items = pool.map_async(functools.partial(globals()['update_data'], db_name), old_data).get()

		db, changes = update_db_partial(db, updated_items, begin=i, end=min(i + updating_step, end))

		save_db(db, db_name)


def find_db(db_name):
	"""finding ids and saving them in a json file for each db"""
	db = load_db(db_name)

	for resource in get_resources(db_name):

		pages = get_resources()[resource][db_name][f'{db_name}_list']

		base = get_resources()[resource][db_name]['base']

		petterns = [get_resources()[resource][db_name][pattern] for pattern in get_resources()[resource][db_name] if pattern.endswith('pattern') ]

		db += [{f'{resource}_id': _id} for _id in collect_data_id_from_resource(pages , base , patterns)]

	save_db(db , db_name)




def init_db(db_name):
	open(f'{config.dataset_dir}/{db_name}db.json', 'w+').write('[]')


def save_pages(url, patterns):
	pass

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


def test_getter(data_name, resource, attributes=None, count=None, id_list=None, complete_report=True):
	getter_modules = globals()[f'get_{data_name}_data_from_{resource}']
	if attributes is None: attributes = getter_modules('get_locals')
	db = load_db(data_name)
	count = len(load_db(data_name)) if count is None else count
	sample_data = random.sample(db, count)
	data_ids = id_list if id_list else [new_data[f'{resource}ID'] for new_data in sample_data if f'{resource}ID' in new_data] #find_db(data_name, resources=[resource], save_to_db=False, max_find_all=count)

	test_results = []

	for attribute in attributes:
		
		failed_get_ids, failed_test_ids, all_datas = [], [], []

		for data_id in data_ids:
			page = make_soup(get_page_link(resource, data_name).format(data_id=data_id))
			
			try:
				new_data = getter_modules(attribute)(page, test=True)
				logger.info(f'id = "{data_id}" ------- {attribute} = "{new_data}"')
				if new_data is None: failed_test_ids += [new_data]
				else: all_datas += [new_data]

			except Exception as error:
				failed_get_ids += [data_id]
				logger.error(error)
 
		test_result = {
			'data_name'			: data_name,
			'attribute'			: attribute,
			'resource'			: resource,
			'failed_get_ids'	: failed_get_ids,
			'failed_tests_ids'	: failed_test_ids,
			
			'success_rate'		: str((count - len(failed_get_ids) - len(failed_test_ids)) / count * 100) + '%'
		}
		if complete_report: 
			test_result = dict(list(test_result.items()) + list({
				'all_datas'		: all_datas
			}.items()))

		test_results += [test_result]

	return test_results

"""
def download_resouce_page(resource, db_name):
	with mp.Pool(10) as pool:
		while 1:
				try:
					page_queue = json.load(open(f'{main_dir}/download/page/{resource}/{db_name}/statics.json'))['page_queue']
					break
				except: pass
		step = 10
		for i in range(0, len(page_queue), step):
			while 1:
				try:
					page_queue = json.load(open(f'{main_dir}/download/page/{resource}/{db_name}/statics.json'))['page_queue']
					break
				except: pass
			pool.map(make_soup, page_queue[i:i+step])
"""

def download_resources(resource , db_name):
    """downloading wanted pages for a specific pair of resource and ab and saving them with make_soup"""
    location = f'{main_dir}/download/page/{resource}/{db_name}'
    base = get_page_link(resource , db_name , 'base')
    page_queue = get_page_link(resource , db_name , f'{db_name}_list')
    patterns = [get_resources()[resource][db_name][x] for x in get_resources()[resource][db_name] if x.endswith('_pattern')]
    for page in page_queue:
        souped_page = make_soup(page)
        for pattern in patterns:
            for url in [tag['href'] for tag in souped_page.find_all('a' , {'href':re.compile(pattern)})]:
                make_soup(urllib.parse.urljoin(base ,re.search(pattern,url).group(1)))            
                


def init_project():
	"""create needed folders for project and pages that will be downloaded"""
	for resource in get_resources():
		for db_name in get_resources()[resource]:
			directory = f'{main_dir}/download/page/{resource}/{db_name}/'
			if os.path.exists(directory): continue
			try: os.makedirs(directory)
			except Exception as error: logger.error(error)



def arg_parse():
	"""
	"""

	parser = argparse.ArgumentParser()

	parser.add_argument('--test_getter', action='store_true', dest='test_getter',
		            	default=False, help='test getter modules')

	parser.add_argument('--download_resources', action='store_true', dest='download_resources',
		            	default=False, help='download resources')

	parser.add_argument('--update_db', action='store_true', dest='update_db',
		            	default=False, help='updating database')

	parser.add_argument('--find_db', action='store_true', dest='find_db',
		            	default=False, help='finding database id')

	parser.add_argument('--init_db', action='store_true', dest='init_db',
		            	default=False, help='initializing database')

	parser.add_argument('-resource', type=str, dest='resource',
		            	help='resource of test data')

	parser.add_argument('-db', type=str, dest='db',
		            	help='db of test data')

	parser.add_argument('-attributes', type=str, nargs='+', dest='attributes', default=None,
		            	help='attribute of test data')

	parser.add_argument('-count', type=int, dest='count', default=None,
		            	help='number of test datas')

	parser.add_argument('-id', type=str, nargs='+', dest='id',
		            	help='data id s to be tested')

	parser.add_argument('-resume', action='store_true', dest='resume', default=False,
		            	help='specify the resume arg in download_resources function')

	parser.add_argument('-dont_use_local_save', action='store_true', dest='dont_use_local_save', default=False,
		            	help='specify whether should use local saved pages in make_spup funtion or not')

	parser.add_argument('-dont_save_page_local', action='store_true', dest='dont_save_page_local', default=False,
		            	help='specify whether should use local saved pages in make_spup funtion or not')

	parser.add_argument('-complete_report', action='store_true', dest='complete_report', default=False,
		            	help='gives complete eport of task')

	args = parser.parse_args()

	config.use_local_save = not args.dont_use_local_save
	config.save_page_local = not args.dont_save_page_local

	if args.test_getter:
		logger.critical('test results : ')
		pprint(test_getter(args.db, args.resource, args.attributes, count=args.count, id_list=args.id, complete_report=args.complete_report))
	
	elif args.download_resources:
		download_resources(args.resource, args.db, count=args.count, resume=args.resume)

	elif args.update_db:
		update_db(args.db)

	elif args.find_db:
		find_db(args.db)

	elif args.init_db:
		init_db(args.db)


if __name__ == '__main__':
	arg_parse()
	#init_project()