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
import time
from pprint import pprint
import psutil
import os
import html
import logging
import inspect
import functools
import itertools
import time
from tools import *
import youtube_downloader



sftp = None


def Clear_duplicate_name(array):
    for i in range(len(array)):
        for j in range(i+1,len(array)):
                if array[i] == array[j]:
                    array.remove(array[j])
                    Clear_duplicate_name(array)
                    break


    return



def get_footballTeam_data_from_sofifa(attribute):
	def name(page):
		return re.search('(.*) \(.*', page.find('h1').text.strip()).group(1)

	def players(page):
		return [tag.find('a', {'href': re.compile('/player/[0-9]*')})['title'] for tag in page.find_all('tr',{'class' : 'starting'})+page.find_all('tr',{'class' : 'sub'})+page.find_all('tr',{'class' : 'res'})]

	def homeStadium(page):
		return re.search('.*?</label>(.*)</li>', str(page.find('label', text='Home Stadium').parent)).group(1).strip()

	def rivalTeam(page):
		return page.find('label', text='Rival Team').findNext().text

	def transferBudget(page):
		return re.search('.*?</label>(.*)</li>', str(page.find('label', text='Transfer Budget').parent)).group(1).strip().replace('\u20ac',' yoro ')

	def mainAverageAge(page):
		return re.search('.*?</label>(.*)</li>', str(page.find('label', text='Starting 11 Average Age').parent)).group(1).strip()

	def allAverageAge(page):
		return re.search('.*?</label>(.*)</li>', str(page.find('label', text='Whole Team Average Age').parent)).group(1).strip()

	def captain(page):
		return page.find('label', text='Captain').parent.find('a')['data-tooltip']

	def shortFreeKick(page):
		return page.find('label', text='Short Free Kick').parent.find('a')['data-tooltip']

	def longFreeKick(page):
		return page.find('label', text='Long Free Kick').parent.find('a')['data-tooltip']

	def penalty(page):
		return page.find('label', text='Penalties').parent.find('a')['data-tooltip']

	def leftCorner(page):
		return page.find('label', text='Left Corner').parent.find('a')['data-tooltip']

	def rightCorner(page):
		return page.find('label', text='Right Corner').parent.find('a')['data-tooltip']

	def sofifaLikes(page):
		return int(page.select('a.like-btn.btn')[0].find('span').text.strip())

	def homeKit(page):
		return [tag for tag in page.find_all('img', {'src': re.compile('.*?/kits/.*')}) if tag.parent.text.find('Home') != -1][0]['src']

	def awayKit(page):
		return [tag for tag in page.find_all('img', {'src': re.compile('.*?/kits/.*')}) if tag.parent.text.find('Away') != -1][0]['src']

	def thirdKit(page):
		return [tag for tag in page.find_all('img', {'src': re.compile('.*?/kits/.*')}) if tag.parent.text.find('Third') != -1][0]['src']

	def goalkeeperKit(page):
		return [tag for tag in page.find_all('img', {'src': re.compile('.*?/kits/.*')}) if tag.parent.text.find('Goalkeeper') != -1][0]['src']

	def picture(page):
		return page.find('img', {'data-src': re.compile('.*?/teams/.*')})['data-src']

	def country(page):
		return page.select('div.info')[0].find('a', {'href': re.compile('.*?/teams.*')})['title']

	def sofifaAttackRate(page):
		return int([tag for tag in page.select('div.card-body.stats')[0].find('div').select('div') if tag.text.find('Attack') != -1][0].find('span').text)

	def sofifaMidfieldRate(page):
		return int([tag for tag in page.select('div.card-body.stats')[0].find('div').select('div') if tag.text.find('Midfield') != -1][0].find('span').text)

	def sofifaOverallRate(page):
		return int([tag for tag in page.select('div.card-body.stats')[0].find('div').select('div') if tag.text.find('Overall') != -1][0].find('span').text)

	def sofifaDefenceRate(page):
		return int([tag for tag in page.select('div.card-body.stats')[0].find('div').select('div') if tag.text.find('Defence') != -1][0].find('span').text)

	def sofifaDefenceRate(page):
		return [tag for tag in page.select('div.card-body.stats')[0].find('div').select('div') if tag.text.find('Defence') != -1][0].find('span').text

	def country(page):
		return page.select('div.info')[0].find('a', {'href': re.compile('.*?/teams.*')})['title']

	def league(page):
		t = page.select('div.info')[0].find('a', {'href': re.compile('.*?/teams.*')}).findNext().findNext().text
		return re.sub(r' \([0-9]*\)','',t)

	if attribute ==  'get_locals': return list(locals().keys())

	return locals()[attribute] # return partial_function with page


def get_footballPlayer_data_from_sofifa(attribute):
	def name(page):
		return re.search(r'([A-Za-z -.].*)  .*?' ,page.find('div',{'class' : 'meta'}).text.strip()).group(1)

	def age(page):
		return re.search(r'.*?Age ([0-9]{2}) .*?', page.find('div',  {'class': 'info'}).decode_contents(formatter="html").strip()).group(1)

	def birthYear(page):
		return int(re.search(r'.*? \([a-zA-Z]*? [0-9,]*? ([0-9]*?)\) .*?', page.find('div',  {'class': 'info'}).decode_contents(formatter="html").strip().replace(',', '')).group(1))

	def foot(page):
		return re.search(r'.*?</label>.*?([a-zA-Z]{3,})', page.find('div',  {'class': 'teams'}).find_all('li')[0].decode_contents(formatter="html").strip()).group(1)

	def team(page):
		return page.find_all('a',  {'href': re.compile('/team.*?')})[1].decode_contents(formatter="html").strip()

	def natioalTeam(page):
		return page.find_all('a',  {'href': re.compile('/team.*?')})[2].decode_contents(formatter="html").strip()

	def country(page):
		return page.find('div', {'class': 'info'}).find('div', {'class': 'meta'}).find('a',  {'href': re.compile('/players.*?')})['title'].strip()

	def jerseyNumber(page):
		return re.search(r'.*?</label>([0-9]{1,3})<.*?', [str(tag) for tag in page.find_all('li') if str(tag).find('Jersey Number') != -1][0]).group(1)

	def jerseyNumberNational(page):
		return re.search(r'.*?</label>([0-9]{1,3})<.*?', [str(tag) for tag in page.find_all('li') if str(tag).find('Jersey Number') != -1][1]).group(1)

	def rate(page):
		return [tag for tag in page.find_all('div', {'class': 'column col-4 text-center'}) if str(tag).find('Overall Rating') != -1][0].find('span').decode_contents(formatter="html")

	def potential(page):
		return [tag for tag in page.find_all('div', {'class': 'column col-4 text-center'}) if str(tag).find('Potential') != -1][0].find('span').decode_contents(formatter="html")

	def value(page):
		return [tag for tag in page.find_all('div', {'class': 'column col-4 text-center'}) if str(tag).find('Value') != -1][0].find('span').decode_contents(formatter="html")

	def wage(page):
		return [tag for tag in page.find_all('div', {'class': 'column col-4 text-center'}) if str(tag).find('Wage') != -1][0].find('span').decode_contents(formatter="html")

	def position(page):
		return [tag for tag in page.find_all('li') if str(tag.find('label')).find('Position') != -1][0].find('span').decode_contents()

	def sofifaFollow(page):
		return [tag for tag in page.find_all('a') if str(tag).find('Follow') != -1 and tag.find('span')][0].find('span').decode_contents()

	def picture(page):
		return page.find('img', {'data-src': re.compile('https://cdn.sofifa.org/players.*?')})['data-src']


	if attribute ==  'get_locals': return list(locals().keys())

	return locals()[attribute] # return partial_function with page


def get_actor_data_from_imdb(attribute):
	def name(page):
		return str(page.find('div',  {'id': 'name-overview-widget'}).find('h1').find('span', {'class': 'itemprop'}).decode_contents(formatter="html")).strip()

	def rank(page):
		return page.find('div', {'id' : 'meterHeaderBox'}).find('a').text

	def trivia(page):
		try:
			page = make_soup('https://imdb.com' + page.find('a', text = 'Biography')['href'])
			tag = page.find('a', {'name' : 'trivia'}).findNext()
			trivia = []
			count = int(re.search('.*?\(([0-9]*)\)', tag.text).group(1))
			tag = tag.findNext()
			i = 0
			while i < count:
				trivia.append(tag.text.strip())
				tag=tag.findNext('div')
				i+=1
			return trivia
		except:
			return []

	def quotes(page):
		try:
			page = make_soup('https://imdb.com' + page.find('a', text = 'Biography')['href'])
			tag = page.find('a', {'name' : 'trivia'}).findNext()
			quotes = []
			count = int(re.search('.*?\(([0-9]*)\)', tag.text).group(1))
			tag = tag.findNext()
			i = 0
			while i < count:
				quotes.append(tag.text.strip())
				tag=tag.findNext('div')
				i+=1
			return quotes
		except:
			return []

	def birthdate(page):
		try:
			return re.search('(.*?)-([0-9]*)-([0-9]*)', page.find('h4', text='Born:').parent.find('time')['datetime']).group(1)+ '_' + re.search('(.*?)-([0-9]*)-([0-9]*)', page.find('h4', text='Born:').parent.find('time')['datetime']).group(2)\
			+ '_' + re.search('(.*?)-([0-9]*)-([0-9]*)', page.find('h4', text='Born:').parent.find('time')['datetime']).group(3)
		except:return '##'

	def deathdate(page):
		try:
			return re.search('(.*?)-([0-9]*)-([0-9]*)', page.find('h4', text='Died:').parent.find('time')['datetime']).group(1)+ '_' + re.search('(.*?)-([0-9]*)-([0-9]*)', page.find('h4', text='Died:').parent.find('time')['datetime']).group(2)\
			+ '_' + re.search('(.*?)-([0-9]*)-([0-9]*)', page.find('h4', text='Died:').parent.find('time')['datetime']).group(3)
		except:
			return '##'

	def birth_year(page):
		try:
			return int(page.find('h4', text='Born:').parent.find('time')['datetime'][:4])
		except:
			return 0

	def death_year(page):
		try:
			return page.find('h4', text='Died:').parent.find('time')['datetime'][:4]
		except:
 			return 0

	def dead(page):
		return bool(page.find('h4', text='Died:'))

	def picture(page):
		try:
			return page.find('img', {'id': 'name-poster'})['src']
		except: return '##'

	def series(page):
		page = make_soup('https://imdb.com' + page.find('a', {'href': re.compile('/name/.*?/?nmdp=1&ref_=nm_ql_4#filmography')})['href'])
		return [tag.find('b').find('a').text for tag in page.find('div',{'id' : 'filmography'}).find('div',{'class' : 'filmo-category-section'}).find_all('div',{'class' : 'filmo-row odd'}) if tag.text.find('Series')\
				!= -1] + [tag.find('b').find('a').text for tag in page.find('div',{'id' : 'filmography'}).find('div',{'class' : 'filmo-category-section'}).find_all('div',{'class' : 'filmo-row even'}) if\
				tag.text.find('Series') != -1]

	def series_characters(page):
		page = make_soup('https://imdb.com' + page.find('a', {'href': re.compile('/name/.*?/?nmdp=1&ref_=nm_ql_4#filmography')})['href'])
		oddList = [tag.text.strip().replace('\n' , '') for tag in page.find('div',{'id' : 'filmography'}).find('div',{'class' : 'filmo-category-section'}).find_all('div',{'class' : 'filmo-row odd'}) if tag.text.find('Series')\
					!= -1]
		evenList =[tag.text.strip().replace('\n' , '') for tag in page.find('div',{'id' : 'filmography'}).find('div',{'class' : 'filmo-category-section'}).find_all('div',{'class' : 'filmo-row even'}) if tag.text.find('Series')\
					!= -1]
		return [re.search('.*?\(.*?\)(.*?)-.*?', i).group(1) for i in oddList if re.search('.*?\(.*?\)(.*?)-.*?', i)]+ [re.search('.*?\(.*?\)(.*?)-.*?', i).group(1) for i in evenList if re.search('.*?\(.*?\)(.*?)-.*?', i)]



	def movies_characters(page):
		page = make_soup('https://imdb.com' + page.find('a', {'href': re.compile('/name/.*?/?nmdp=1&ref_=nm_ql_4#filmography')})['href'])
		oddList = [tag.text.strip() for tag in page.find('div',{'id' : 'filmography'}).find('div',{'class' : 'filmo-category-section'}).find_all('div',{'class' : 'filmo-row odd'}) if not re.search('.*?\(.*?\)', tag.text)]
		evenList =[tag.text.strip() for tag in page.find('div',{'id' : 'filmography'}).find('div',{'class' : 'filmo-category-section'}).find_all('div',{'class' : 'filmo-row even'}) if not re.search('.*?\(.*?\)', tag.text)]
		return [re.search('.*?\\n\\n.*?\\n\\n(.*)', i).group(1) for i in oddList if re.search('.*?\\n\\n.*?\\n\\n(.*)', i)]+ [re.search('.*?\\n\\n.*?\\n\\n(.*)', i).group(1) for i in evenList if re.search('.*?\\n\\n.*?\\n\\n(.*)', i)]

	def bio(page):
		try:
			page = make_soup('https://imdb.com' + page.find('a', text = 'Biography')['href'])
			return re.search('(.*)\.- .*',[tag.findNext().text.strip().replace('\n','') for tag in page.find_all('h4', {'class' : 'li_group'}) if tag.text.find('Mini Bio') != -1][0]).group(1)
		except:
			return '##'

	def known_for(page):
		return [tag.find('a').text.strip() for tag in page.select('div.knownfor-title-role')]

	def movies(page):
		page = make_soup('https://imdb.com' + page.find('a', {'href': re.compile('/name/.*?/?nmdp=1&ref_=nm_ql_4#filmography')})['href'])
		return [tag.find('b').find('a').text for tag in page.find('div',{'id' : 'filmography'}).find('div',{'class' : 'filmo-category-section'}).find_all('div',{'class' : 'filmo-row odd'}) if not re.search('.*?\(.*?\)', tag.text)]\
				+[tag.find('b').find('a').text for tag in page.find('div',{'id' : 'filmography'}).find('div',{'class' : 'filmo-category-section'}).find_all('div',{'class' : 'filmo-row even'}) if not re.search('.*?\(.*?\)', tag.text)]

	def pictures(page):
		try:
			gallery_page = 'https://www.imdb.com' + page.find('a', text='Photo Gallery')['href']
			page = make_soup(gallery_page)
			pages = [gallery_page]
			if page.find_all('a', {'href': re.compile('.*?/mediaindex.page.*')}):
				pages += list(set(['https://www.imdb.com' + tag['href'] for tag in page.find_all('a', {'href': re.compile('.*?/mediaindex.page.*')})]))
			pages = [make_soup(page) for page in pages[0:1]]
			pic_pages = list(itertools.chain.from_iterable([['https://www.imdb.com' + tag['href'] for tag in page.find_all('a', {'href': re.compile('.*?/mediaviewer/.*')})] for page in pages]))
			#pic_pages = [make_soup(page) for page in pic_pages[0:1]]
			pic_page_text = str(make_soup(pic_pages[0]))
			pic_link = lambda pic_id: re.search(f'.*?"id":"{pic_id}".*?"src":"(.*?)".*', pic_page_text).group(1)
			pic_ids = [re.search('.*?/mediaviewer/(rm[0-9]*)', pic_page).group(1) for pic_page in pic_pages]
			#print(f'{len(pic_ids)} number of pic_ids founded')
			return [pic_link(pic_id) for pic_id in pic_ids]
		except:return []

	def height(page):
		try:
			return float(re.search('.*?"\((.*?)m\)',page.find('div', {'id' : 'details-height'}).text.strip().replace('\xa0','').replace('\n' , '')).group(1))
		except: return 0

	def spouse(page):
		page = make_soup('https://imdb.com' + page.find('a', text = 'Biography')['href'])
		if page.find('table',{'id' : 'tableSpouses'}):
			return re.search('(.*?)\(.*\).*',page.find('table',{'id' : 'tableSpouses'}).text.strip().replace('\n' , '').replace('  ', '')).group(1)
		else:
			return []

	def trademark(page):
		if page.find('div',{'id':'dyk-trademark'}):
			return page.find('div',{'id':'dyk-trademark'}).text.replace('\n','').replace('Trademark:' , '').replace('  ' , '')
		else:return '##'

	def starSign(page):
		if page.find('div',{'id':'dyk-star-sign'}):
			return page.find('div',{'id':'dyk-star-sign'}).text.replace('\n','').replace('Star Sign:' , '')
		else:return '##'

	if attribute ==  'get_locals': return list(locals().keys())

	return locals()[attribute] # return partial_function with page


def get_director_data_from_imdb(attribute):
	def name(page):
		return str(page.find('div',  {'id': 'name-overview-widget'}).find('h1').find('span', {'class': 'itemprop'}).decode_contents(formatter="html")).strip()

	def rank(page):
		try:
			return page.find('div', {'id' : 'meterHeaderBox'}).find('a').text
		except:
			return 0

	def birthdate(page):
		try:
			return re.search('(.*?)-([0-9]*)-([0-9]*)', page.find('h4', text='Born:').parent.find('time')['datetime']).group(1)+ '_' + re.search('(.*?)-([0-9]*)-([0-9]*)', page.find('h4', text='Born:').parent.find('time')['datetime']).group(2)\
				+ '_' + re.search('(.*?)-([0-9]*)-([0-9]*)', page.find('h4', text='Born:').parent.find('time')['datetime']).group(3)
		except:
			return '0000_00_00'

	def deathdate(page):
		try:
			return re.search('(.*?)-([0-9]*)-([0-9]*)', page.find('h4', text='Died:').parent.find('time')['datetime']).group(1)+ '_' + re.search('(.*?)-([0-9]*)-([0-9]*)', page.find('h4', text='Died:').parent.find('time')['datetime']).group(2)\
					+ '_' + re.search('(.*?)-([0-9]*)-([0-9]*)', page.find('h4', text='Died:').parent.find('time')['datetime']).group(3)
		except:
			return '0000_00_00'

	def birth_year(page):
		try:
			return int(page.find('h4', text='Born:').parent.find('time')['datetime'][:4])
		except:
			return 0

	def death_year(page):
		try:
			return int(page.find('h4', text='Died:').parent.find('time')['datetime'][:4])
		except:
			return 0

	def dead(page):
		return bool(page.find('h4', text='Died:'))

	def picture(page):
		try:
			return page.find('img', {'id': 'name-poster'})['src']
		except:
			return '##'

	def trivia(page):
		try:
			page = make_soup('https://imdb.com' + page.find('a', text = 'Biography')['href'])
			tag = page.find('a', {'name' : 'trivia'}).findNext()
			trivia = []
			count = int(re.search('.*?\(([0-9]*)\)', tag.text).group(1))
			tag = tag.findNext()
			i = 0
			while i < count:
				trivia.append(tag.text.strip())
				tag=tag.findNext('div')
				i+=1
			return trivia
		except:
			return []

	def quotes(page):
		try:
			page = make_soup('https://imdb.com' + page.find('a', text = 'Biography')['href'])
			tag = page.find('a', {'name' : 'quotes'}).findNext()
			quotes = []
			count = int(re.search('.*?\(([0-9]*)\)', tag.text).group(1))
			tag = tag.findNext()
			i = 0
			while i < count:
				quotes.append(tag.text.strip())
				tag=tag.findNext('div')
				i+=1
			return quotes
		except:
			return []

	def trade_mark(page):
		try:
			page = make_soup('https://imdb.com' + page.find('a', text = 'Biography')['href'])
			tag = page.find('a', {'name' : 'trademark'}).findNext()
			trademark = []
			count = int(re.search('.*?\(([0-9]*)\)', tag.text).group(1))
			tag = tag.findNext()
			i = 0
			while i < count:
				trademark.append(tag.text.strip())
				tag=tag.findNext('div')
				i+=1
			return trademark
		except:
			return []

	def bio(page):
		try:
			page = make_soup('https://imdb.com' + page.find('a', text = 'Biography')['href'])
			bio = [tag for tag in page.find_all('h4', {'class' : 'li_group'}) if tag.text.find('Mini Bio') != -1][0]
			return bio.findNext().find('p').text.strip()
		except:
			return '##'

	def known_for(page):
		try:
			return [tag.find('a').text.strip() for tag in page.select('div.knownfor-title-role')]
		except:
			return []

	def movies(page):
		try:
			page = make_soup('https://imdb.com' + page.find('a', {'href': re.compile('/name/.*?/?nmdp=1&ref_=nm_ql_4#filmography')})['href'])
			page = page.find('a', {'name' : 'director'}).findNext().findNext()
			result = []
			while(1):
				if not re.search('director.*?', page['id']):
					break
				result.append(page.find('b').text)
				page=page.findNext('div',{'class' : re.compile('filmo-row .*?' )})
			return result
		except:
			return []

	def pictures(page):
		try:
			gallery_page = 'https://www.imdb.com' + page.find('a', text='Photo Gallery')['href']
			page = make_soup(gallery_page)
			pages = [gallery_page]
			if page.find_all('a', {'href': re.compile('.*?/mediaindex.page.*')}):
				pages += list(set(['https://www.imdb.com' + tag['href'] for tag in page.find_all('a', {'href': re.compile('.*?/mediaindex.page.*')})]))
			pages = [make_soup(page) for page in pages[0:1]]
			pic_pages = list(itertools.chain.from_iterable([['https://www.imdb.com' + tag['href'] for tag in page.find_all('a', {'href': re.compile('.*?/mediaviewer/.*')})] for page in pages]))
			#pic_pages = [make_soup(page) for page in pic_pages[0:1]]
			pic_page_text = str(make_soup(pic_pages[0]))
			pic_link = lambda pic_id: re.search(f'.*?"id":"{pic_id}".*?"src":"(.*?)".*', pic_page_text).group(1)
			pic_ids = [re.search('.*?/mediaviewer/(rm[0-9]*)', pic_page).group(1) for pic_page in pic_pages]
			#print(f'{len(pic_ids)} number of pic_ids founded')
			return [pic_link(pic_id) for pic_id in pic_ids]
		except:
			return []

	def nick_name(page):
		try:
			page = make_soup('https://imdb.com' + page.find('a', text = 'Biography')['href'])
			return [tag.findNext().text.strip() for tag in page.find_all('td', {'class' : 'label'}) if tag.text.find('Nickname') != -1]
		except:
			return '##'

	def height(page):
		try:
			page = make_soup('https://imdb.com' + page.find('a', text = 'Biography')['href'])
			return float(re.search('.*\((.*?)m\)',[tag.findNext().text.strip().replace('\xa0' , '') for tag in page.find_all('td', {'class' : 'label'}) if tag.text.find('Height') != -1][0]).group(1))
		except:
			return 0

	def spouse(page):
		try:
			page = make_soup('https://imdb.com' + page.find('a', text = 'Trivia ')['href'])
			spouse = [tag for tag in page.find_all('h4') if tag.text.find('Spouse') != -1][0]
			spouse = spouse.findNext()
			return [tag.find('td').text.strip() for tag in spouse.find_all('tr',{'class' : 'soda odd'}) + spouse.find_all('tr',{'class' : 'soda even'})]
		except:
			return []

	if attribute ==  'get_locals': return list(locals().keys())

	return locals()[attribute] # return partial_function with page


def get_movie_data_from_imdb(attribute):

	# TODO: get all name of movie from aka page

	def name(page):
		# TODO: remove "the IMAX experience" from end of some movie names
		# TODO: some names are not in english
		# TODO: check if ": The Motion Picture" should be removed from name

		page2 = make_soup(page.find('link', {'rel': 'canonical'})['href'] + page.find('h2', text='Details').parent.find('a', {'href': re.compile('.*?releaseinfo.*')})['href'])
		try:
			result = [tag for tag in page2.find('table', {'id': 'akas'}).select('td') \
						if any([tag.text.find(x) != -1 for x in ['USA', 'World-wide', 'UK']]) and \
						all([tag.text.find(x) == -1 for x in ['alternative', 'informal']]) \
						][0].findNext('td').text.replace(': The IMAX Experience', '').strip()
		except:
			result = re.search('(.*?)\([^\(]*', page.select('div.title_wrapper')[0].find('h1').text).group(1)

		return result

	def release_day(page):
		try:
			return int(page.select('div.title_wrapper')[0].find('a', {'href': re.compile('.*?releaseinfo.*')}).text.split(' ')[0])
		except:
			return '##'

	def release_month(page):
		try:
			return {'January'	: 1 , 'February': 2	, 'March'		: 3,
					'April'		: 4 , 'May'		: 5	, 'June'		: 6,
					'July'		: 7 , 'August'	: 8	, 'September'	: 9,
					'October'	: 10, 'November': 11, 'December'	: 12
					}[page.select('div.title_wrapper')[0].find('a', {'href': re.compile('.*?releaseinfo.*')}).text.split(' ')[1]]
		except:
			return ''

	def release_year(page):
		try:
			return int(page.select('div.title_wrapper')[0].find('a', {'href': re.compile('.*?releaseinfo.*')}).text.split(' ')[2])
		except:
			return 0

	#def release_date(page):
	#	try:
	#		return f'{release_year(page)}_{release_month(page)}_{release_day(page)}'
	#	except:
	#		return '##'

	def imdb_rate(page):
		try:
			return float(page.find('span', {'itemprop': 'ratingValue'}).text)
		except:
			return 0

	def imdb_votes(page):
		try:
			return int(page.find('span', {'itemprop': 'ratingCount'}).text.replace(',', ''))
		except:
			return 0

	def imdb_popularity(page):
		popularity_tag = [tag for tag in page.select('div.titleReviewBar')[0].select('div') if tag.text.strip() == 'Popularity']
		if popularity_tag:
			return int(popularity_tag[0].findNext('div').text.replace(',', '').strip().split('\n')[0])
		else:
			return 0

	def imdb_rank(page):
		if page.select('div.titleAwardsRanks'):
			return re.search('.*?#([0-9]*).*?', page.select('div#titleAwardsRanks')[0].find('a', {'href': re.compile('/chart/top.*')}).text).group(1)
		else:
			return 10**10


	def imdb_user_reviews(page):
		try:
			return int(re.search(r'(.*?) .*?', page.find('div', {'class': 'titleReviewBarItem titleReviewbarItemBorder'}).find('a', {'href': re.compile('reviews.*?')}).text.strip().replace(',', '')).group(1))
		except:
			return 0

	def imdb_critic_reviews(page):
		try:
			return int(re.search(r'(.*?) .*?', page.find('div', {'class': 'titleReviewBarItem titleReviewbarItemBorder'}).find('a', {'href': re.compile('externalreviews.*?')}).decode_contents(formatter="html").strip().replace(',', '')).group(1))
		except:
			return 0

	def poster(page):
		try:
			return page.find('div', {'class': 'poster'}).find('img')['src']
		except:
			return '##'

	def storyline(page):
		try:
			return page.find('div', {'id': 'titleStoryLine'}).find('div').find('span').text.strip()
		except:
			return '##'

	def runtime(page):
		try:
			return int(page.select('div.titleBar')[0].find('time')['datetime'][2:-1])
		except:
			return 0

	def country(page):
		# TODO: it returns the released country, but should return the origin country
		return page.find('h4', text='Country:').parent.find('a').text

	def genres(page):
		return [tag.text.strip() for tag in page.find('h4', text='Genres:').parent.find_all('a')]

	def summaries(page):
		page = make_soup('https://www.imdb.com' + page.find('a', text = 'Plot Summary')['href'])
		return [tag.find('p').text.strip() for tag in page.find('ul', {'id' : 'plot-summaries-content'}).find_all('li', {'class' : 'ipl-zebra-list__item'})]

	def summary(page):
		page = make_soup('https://www.imdb.com' + page.find('a', text = 'Plot Summary')['href'])
		return [tag.find('p').text.strip() for tag in page.find('ul', {'id' : 'plot-summaries-content'}).find_all('li', {'class' : 'ipl-zebra-list__item'})][0]

	def directors(page):
		try:
			page = make_soup('https://www.imdb.com' + page.find('a', text = 'Full Cast and Crew')['href'])
			return list(set([tag.find('td').text.strip() for tag in [tag for tag in page.select('h4') if tag.text.strip() == 'Directed by'][0].findNext('table').find_all('tr') if tag.find('td').text.strip() != '']))
		except:
			return []

	def director(page):
		if page.find('h4', text='Director:'):
			return page.find('h4', text='Director:').parent.find('a').text.strip()
		else:
			return '##'

	def writers(page):
		# TODO: should be gotten from datails page of movie, main page is incomplete
		try:
			page = make_soup('https://www.imdb.com' + page.find('a', text = 'Full Cast and Crew')['href'])
			return list(set([tag.find('td').text.strip() for tag in [tag for tag in page.select('h4') if tag.text.strip() == 'Writing Credits'][0].findNext('table').find_all('tr') if tag.find('td').text.strip() != '']))
		except:
			return []

	def writer(page):
		if page.find('h4', text='Writer:'):
			return page.find('h4', text='Writer:').parent.find('a').text.strip()
		else:
			return '##'

	def stars(page):
		return [tag.text.strip() for tag in page.find('h4', text='Stars:').parent.find_all('a', {'href': re.compile('.*/name/.*')})]

	def cast(page):
		page = make_soup('https://www.imdb.com' + page.find('a', text = 'Full Cast and Crew')['href'])
		return [tag.text.strip().replace('\n' , '').replace('  ' , '') for tag in page.find('table', {'class' : 'cast_list'}).find_all('a') if tag.text != '']

	def characters(page):
		page = make_soup('https://www.imdb.com' + page.find('a', text = 'Full Cast and Crew')['href'])
		return [tag.text.strip().replace('\n' , '').replace('  ' , '') for tag in page.select('table.cast_list')[0].select('td.character')]


	#def soundtracks(page):
	#	page_id = re.search('/title/(.*?)/.*', page.select('a.quicklink')[0]['href']).group(1)
	#	page = make_soup(f'https://www.imdb.com/title/{page_id}/soundtrack')
	#
	#	return [re.search('(.*?) .*', tag.text.strip()).group(1) for tag in page.select('div.soundTrack')]

	#def soundtracks_file(page):
	#	playlist_page = make_soup(youtube_downloader.search_music(name, mode='soundtrack', _type='playlist', count=1)[0]['url'])
	#	return ['https://youtube.com' + tag['href'] for tag in playlist_page.select('table.pl-video-table')[0].select('a.pl-video-title-link.yt-uix-tile-link.yt-uix-sessionlink.spf-link')]

		#soundtracks = []
		#for tag in page.select('div.soundTrack'):
		#	soundtracks += [{
		#		'name': re.search('(.*?) .*', tag.text.strip()).group(1)
		#	}]

	def popularity(page):
		# TODO: should use a better formula for normalization

		try:
			popularity_rate = int(page.find('span', {'itemprop': 'ratingCount'}).text.replace(',', ''))
		except:
			popularity_rate = 0

		return popularity_rate# / (2 * 10**7)

	def photos(page):
		try:
			gallery_page = 'https://www.imdb.com' + page.find('a', text='Photo Gallery')['href']
			page = make_soup(gallery_page)
			pages = [gallery_page]
			if page.find_all('a', {'href': re.compile('.*?/mediaindex.page.*')}):
				pages += list(set(['https://www.imdb.com' + tag['href'] for tag in page.find_all('a', {'href': re.compile('.*?/mediaindex.page.*')})]))
			pages = [make_soup(page) for page in pages[0:1]]
			pic_pages = list(itertools.chain.from_iterable([['https://www.imdb.com' + tag['href'] for tag in page.find_all('a', {'href': re.compile('.*?/mediaviewer/.*')})] for page in pages]))
			#pic_pages = [make_soup(page) for page in pic_pages[0:1]]
			pic_page_text = str(make_soup(pic_pages[0]))
			pic_link = lambda pic_id: re.search(f'.*?"id":"{pic_id}".*?"src":"(.*?)".*', pic_page_text).group(1)
			pic_ids = [re.search('.*?/mediaviewer/(rm[0-9]*)', pic_page).group(1) for pic_page in pic_pages]
			#print(f'{len(pic_ids)} number of pic_ids founded')
			return [pic_link(pic_id) for pic_id in pic_ids]
		except:
			return []

	def videos(page):
		try:
			page_url = 'https://www.imdb.com' + page.find('a', text='Trailers and Videos')['href']
			page = make_soup(page_url)
			pages = [page_url]
			if page.find_all('a', {'href': re.compile('.*?/videogallery.page.*')}):
				pages += list(set(['https://www.imdb.com' + tag['href'] for tag in page.find_all('a', {'href': re.compile('.*?/videogallery.page.*')})]))
			pages = [make_soup(page) for page in pages[0:1]]
			video_pages = list(itertools.chain.from_iterable([['https://www.imdb.com' + tag['href'] for tag in page.find_all('a', {'href': re.compile('.*?/videoplayer/.*')})] for page in pages]))
			video_pages = [str(make_soup(video_page)) for video_page in video_pages]
			return [re.search('.*?"videoUrl":"(.*?)".*', video_page).group(1) for video_page in video_pages]
		except:
			return []

	def quotes(page):
		try:
			page = make_soup('https://imdb.com' + page.find('a', text = 'Quotes')['href'])
			return [tag.find('div').text.strip().replace('\n','') for tag in page.find_all('div',{'class' : 'quote soda sodavote odd'}) + page.find_all('div',{'class' : 'quote soda sodavote even'})]
		except:
			return []

	def filming_locations(page):
		try:
			x = 'https://www.imdb.com' + page.find('a', text = 'Filming & Production')['href']
			page = make_soup(x)
			return [tag.find('a').text.strip() for tag in page.find('section', {'id' : 'filming_locations'}).find_all('div',{'class' : 'soda sodavote odd'})+ page.find_all('div',{'class' : 'soda sodavote even'})]
		except:
			return []

	#def color(page):
	#	x = 'https://www.imdb.com' + page.find('a', text = 'Technical Specs')['href']
	#	page = make_soup(x)
	#	return [tag.findNext().text.strip() for tag in [tag.find('td', text = ' Color ') for tag in page.find('div', {'id' : 'technical_content'}).find_all('tr',{'class' : 'odd'})+
	#	 		page.find_all('tr',{'class' : 'even'}) if tag.find('td', text = ' Color ')]]

	#def sound_mix(page):
	#	x = 'https://www.imdb.com' + page.find('a', text = 'Technical Specs')['href']
	#	page = make_soup(x)
	#	return [tag.findNext().text.strip().replace('\n',"") for tag in [tag.find('td', text = ' Sound Mix ') for tag in page.find('div', {'id' : 'technical_content'}).find_all('tr',{'class' : 'odd'})+
	#	 		page.find_all('tr',{'class' : 'even'}) if tag.find('td', text = ' Sound Mix ')]]

	def tag_lines(page):
		try:
			x = 'https://www.imdb.com' + page.find('a', text = 'Taglines')['href']
			page = make_soup(x)
			return [tag.text.strip() for tag in page.find('div', {'id' : 'taglines_content'}).find_all('div', {'class' : 'soda odd'}) + page.find_all('div', {'class' : 'soda even'})]
		except:
			return []

	def keywords(page):
		try:
			x = 'https://www.imdb.com' + page.find('a', text = 'Plot Keywords')['href']
			page = make_soup(x)
			return list(itertools.chain.from_iterable( [[tag.text.strip() for tag in tag.find_all('div', {'class' : 'sodatext'})] for tag in page.find('div', {'id' : 'keywords_content'}).find_all('tr', {'class' : 'odd'})+page.find_all('tr', {'class' : 'even'})] ))
		except:
			return []

	def trivia(page):
		try:
			page = make_soup('https://imdb.com' + page.find('a', text = 'Trivia')['href'])
			return [tag.find('div').text.strip() for tag in page.find_all('div',{'class' : 'soda odd sodavote'}) + page.find_all('div',{'class' : 'soda even sodavote'})]
		except:
			return []

	if attribute ==  'get_locals': return list(locals().keys())

	return locals()[attribute] # return partial_function with page


def get_book_data_from_goodreads(attribute):
	def book_list(page):
		page = make_soup(page)
		return list(set([re.search(r'.*?/book/show/(.*)', tag['href']).group(1) for tag in page.find_all('a', {'href': re.compile('.*?/book/show/(.*)')})]))

	def title(page):
		return page.find('h1', {'id': 'bookTitle'}).text.strip()

	def author(page):
		return page.select('div.authorName__container')[0].find('span').text

	def picture(page):
		return page.find('img', {'id': 'coverImage'})['src']

	def goodreadsRate(page):
		return float(page.select('span.value.rating')[0].find('span').text.strip())

	def goodreadsVotes(page):
		 return int(page.select('span.votes.value-title')[0]['title'])

	def goodreadsReviews(page):
		 return int(page.select('span.count.value-title')[0]['title'])

	def description(page):
		 return page.select('div#description')[0].text.strip()[:-9]

	def pages(page):
		 return re.search('([0-9]*) pages', page.find('span', {'itemprop': 'numberOfPages'}).text).group(1)

	def publishYear(page):
		 return int(re.search('.*?([0-9]{3,4}).*', page.select('div#details')[0].select('div.row')[1].text).group(1))

	def relatedBooks(page):
		 return [tag['alt'] for tag in page.select('div.bookCarousel')[0].select('img')]

	def publishYear(page):
		 return int(re.search('.*?([0-9]{3,4}).*', page.select('div#details')[0].select('div.row')[1].text).group(1))

	def popularity(page):
		return int(page.select('span.votes.value-title')[0]['title'])

	def related(page):
		return [tag.find('img')['alt'] for tag in page.find_all('a',{'href' : re.compile('/list/show/.*')}) if tag.find('img')]


	return


def get_author_data_from_goodreads(attribute):
	def author_list(page):
		page = make_soup(page)
		return list(set([re.search(r'.*?/author/show/(.*)', tag['href']).group(1) for tag in page.find_all('a', {'href': re.compile('.*?/author/show/(.*)')})]))

	def name(page):
		return page.select('div.mainContent ')[0].find('span', {'itemprop': 'name'}).text.strip()

	def picture(page):
		return page.select('div.mainContent ')[0].find('img')['src']

	def goodreadsRate(page):
		return float(re.search('.*:([0-9.])', page.select('a.js-ratingDistTooltip')[0].text).group(1))

	def goodreadsVotes(page):
		 return int(re.search('.*?([0-9]*).*', page.find('a', {'href': re.compile('/review/list/.*sort.rating.view.reviews')}).text.strip()).group(1))

	def goodreadsReviews(page):
		 return int(re.search('.*?([0-9]*).*', page.find('a', {'href': re.compile('/review/list/.*sort.review.view.reviews')}).text.strip()).group(1))

	def books(page):
		 page = make_soup('https://www.goodreads.com' + [tag['href'] for tag in page.find_all('a', {'class' : 'actionLink'}) if tag.text.find('More books by ') != -1][0])
		 return [tag.text.strip() for tag in page.find('table', {'class' : 'tableList'}).find_all('a',{'class' : 'bookTitle'})]

	def bio(page):
		 return page.select('div.aboutAuthorInfo')[0].find('span').text.strip()

	def goodreadsFolowers(page):
		return int(re.search('.*?\(([0-9,]*)\).*?', page.find('a', {'href': re.compile('/author_followings.id..*.method.get')}).text).group(1).replace(',', ''))

	def relatedAuthors(page):
		page = make_soup('https://goodreads.com' + page.find('a', {'href': re.compile('/author/similar/.*')})['href'])
		return [tag.find('a', {'href': re.compile('/author/show/.*')}).text.strip() for tag in page.select('ul.list')[1].select('div.readable.description')]

	def popularity(page):
		return page.find('a', {'href': re.compile('/review/.*')}).text.strip()

	def favoriteBooks(page):
		page = make_soup('https://www.goodreads.com' + [tag['href'] for tag in page.find_all('a', {'class' : 'actionLink right'}) if tag.text.find('More of ') != -1][0])
		return [tag.find('td',{'class' : 'field title'}).find('a').text.strip() for tag in page.find_all('tr', {'class' : 'bookalike review'})]


def get_country_data_from_cia(attribute, page):
	def name(page):
		return page.find('span', {'class': 'region_name1 countryName '}).text.strip().lower()

	def flag(page):
		return 'https://www.cia.gov/library/publications/the-world-factbook/' + page.find('img', {'src': re.compile('.*?/graphics/flags/large/.*?.gif')})['src'][3:]

	def pictures(page):
		return ['https://www.cia.gov/library/publications/the-world-factbook/' + tag['href'][3:] for tag in page.find_all('a', {'href': re.compile('.*?/photo_gallery/[a-z]{2}/images/large/.*?\.jpg')})]

	def location_picture(page):
		return 'https://www.cia.gov/library/publications/the-world-factbook/' + page.find('img', {'src': re.compile('.*?/graphics/locator/.*?/.*?_large_locator.gif')})['src'][3:]

	def map(page):
		return 'https://www.cia.gov/library/publications/the-world-factbook/' + page.find('img', {'src': re.compile('.*?/graphics/maps/[a-z]{2}-map.gif')})['src'][3:]

	def location_description(page):
		return [tag.parent.find_next_sibling("div").text.strip() for tag in page.find_all('a') if tag.text.strip() == 'Location:'][0]

	def area(page):
		return [re.search('([0-9]*) .*', tag.find_next_sibling('div').find('span', {'class': 'category_data'}).text.strip().replace(',', '')).group(1) for tag in page.find_all('div') if tag.text.strip() == 'Area:'][0]

	def population(page):
		return [re.search('([0-9]*) .*', tag.parent.find_next_sibling("div").text.strip().replace(',', '')).group(1) for tag in page.find_all('a') if tag.text.strip() == 'Population:'][0]

	def borderCountreis(page):
		return [tag.findNext().text for tag in page.find_all('span', {'class' : 'category'}) if tag.text.find('border countries') != -1]

	def climate(page):
		return [tag.findNext().findNext().findNext().text for tag in page.find_all('a', text = 'Climate:')]

	def terrain(page):
		return [tag.findNext().findNext().findNext().text for tag in page.find_all('a', text = 'Terrain:')]
	def lowestPoint(page):
		return	[tag.findNext().text.replace('lowest point:','') for tag in page.find_all('span',{'class' : 'category'}) if tag.text.find('elevation extremes: ') != -1]
	def highestPoint(page):
		return [tag.findNext().findNext().text.replace('highest point: ','') for tag in page.find_all('span',{'class' : 'category'}) if tag.text.find('elevation extremes: ') != -1]
	def naturalResources(page):
		return [tag.findNext().findNext().findNext().text for tag in page.find_all('a', text = 'Natural resources:')]
	def naturalHazards(page):
		return [tag.findNext().findNext().findNext().text for tag in page.find_all('a', text = 'Natural hazards:')]
	def geography(page):
		return [tag.findNext().findNext().findNext().text for tag in page.find_all('a', text = 'Geography - note:')]
	def ethnicGroups(page):
		return page.find('a', text = 'Ethnic groups:').findNext().findNext().findNext().text
	def languages(page):
		return page.find('a', text = 'Languages:').findNext().findNext().findNext().text
	def religions(page):
		return	page.find('a', text = 'Religions:').findNext().findNext().findNext().text
	def populationGrowthRate(page):
		return re.search('(.*?)%.*', page.find('a', text = 'Population growth rate:').findNext().findNext().findNext().text).group(1)
	def birthRate(page):
		return page.find('a', text = 'Birth rate:').findNext().findNext().findNext().text
	def deathRate(page):
		return page.find('a', text = 'Death rate:').findNext().findNext().findNext().text
	def netMigrationRate(page):
		return page.find('a', text = 'Net migration rate:').findNext().findNext().findNext().text
	def majorUrbanAreas_population(page):
		return page.find('a', text = 'Major urban areas - population:').findNext().findNext().findNext().text
	def sexRatio(page):
		return float(re.search('([0-9.]*) .*',page.find('span', text = 'total population: ').findNext().text).group(1))
	def maternalMortalityRatio(page):
		return page.find('a', text = 'Maternal mortality ratio:').findNext().findNext().findNext().text
	def physiciansDensity(page):
		return page.find('a', text = 'Physicians density:').findNext().findNext().findNext().text
	def terrain(page):
		return
	def terrain(page):
		return
	def terrain(page):
		return
	def terrain(page):
		return
	def terrain(page):
		return

	return


def get_people_data_from_biography(attribute):
	def people_list(page):
		page = make_soup(page)
		return list(set([re.search(r'.*/people/(.*)', tag['href']).group(1) for tag in page.find_all('a', {'href': re.compile('.*/people/.*')})]))

	def name(page):
		return page.find('dd', {'itemprop':'name'}).text

	def picture(page):
		return page.find('div', {'class': 'l-person--rail'}).find('img')['src']

	def jobs(page):
		return [tag.text for tag in bp.find('dd', {'itemprop':'jobTitle'}).find_all('a')]

	def birthYear(page):
		return int(page.find('dd', {'itemprop':'birthDate'}).find_all('a')[1].text)

	def birthPlace(page):
		return [tag.find_next_sibling('dd').text for tag in page.find_all('dt') if tag.text == 'Place of Birth'][0]


def get_anime_data_from_myanimelist(attribute, page):
	def anime_list(page):
		page = make_soup(page)
		return list(set([re.search(r'.*/anime/([0-9]*?/[^/]*)', tag['href']).group(1) for tag in page.find_all('a', {'href': re.compile('.*/anime/([0-9]*?/[^/]*)')})]))

	def name(page):
		return page.find('span', {'itemprop':'name'}).text.strip()

	def nameJapanese(page):
		return [re.search('<span.*</span>(.*)', str(tag.parent)).group(1) for tag in page.find_all('span') if tag.text.strip() == 'Japanese:'][0].strip()

	def nameEnglish(page):
		return [re.search('<span.*</span>(.*)', str(tag.parent)).group(1) for tag in page.find_all('span') if tag.text.strip() == 'English:'][0].strip()

	def picture(page):
		return page.find('img', {'itemprop': 'image'})['src']


def get_word_data_from_merriam(attribute, page):
	if attribute == 'word_list':
		page = make_soup(page)
		return list(set([re.search(r'/dictionary/(.*)', tag['href']).group(1) for tag in page.find_all('a', {'href': re.compile(r'/dictionary/(.*)')})]))
	if attribute == 'word':
		return page.find('h1', {'class' : 'hword'}).text
	if attribute == 'language':
		return "english"
	if attribute == 'frequency':
		return  "bayad dorost shavad"
	if attribute == 'type':
		return  re.search('([a-z ]*)\n?.*',page.find('div', {'class' : 'entry-attr'}).text.strip() ).group(1)
	if attribute == 'pronunciation':
		return [tag.text for tag in page.find_all('span', {'class' : 'mw'})]
	if attribute == 'otherTenses':
		type =  re.search('([a-z ]*)\n?.*',page.find('div', {'class' : 'entry-attr'}).text.strip() ).group(1)
		if  type == 'verb':
			return [tag.text for tag in page.find('div', {'class' : 'vg'}).find_all('span', {'class' : 'if'})]
	if attribute == 'transitiveVerb':
		type =  re.search('([a-z ]*)\n?.*',page.find('div', {'class' : 'entry-attr'}).text.strip() ).group(1)
		if  type == 'verb':
			return
			#return [tag.text for tag in page.find('div', {'class' : 'toggle-box card-box def-text another-def def-text'}).find_all('span', {'class' : 'dt'})]
	if attribute == 'intransitiveVerb':
		type = re.search('([a-z ]*)\n?.*',page.find('div', {'class' : 'entry-attr'}).text.strip() ).group(1)
		if type == 'verb':
			return
			#return [tag.text for tag in page.find_all('span', {'class' : 'dt'})]
	if attribute == 'examples':
		return [tag.text for tag in page.find('div', {'class' : 'card-primary-content def-text'}).find_all('p', {'class' : 'definition-inner-item'})]

	return


def get_volleyballTeam_data_from_volleyballWorld(attribute, page):
	if attribute == 'volleyballTeam_list':
		page = make_soup(page)
		return list(set([re.search(r'/en/men/teams/(.*)', tag['href']).group(1) for tag in page.find_all('a', {'href': re.compile(r'/en/men/teams/(.*)')})]))
	if attribute == 'coach':
		return [tag.text for tag in page.find('div', {'class' : 'details'}).find_all('h4')]
	if attribute == 'teamManager':
		return [tag.parent.find('strong').text for tag in page.find('ul', {'class' : 'line-list'}).find_all('span', {'class' : 'role'}) if tag.text.find('Team Manager') != -1]
	if attribute == 'assistantCoach':
		return [tag.parent.find('strong').text for tag in page.find('ul', {'class' : 'line-list'}).find_all('span', {'class' : 'role'}) if tag.text.find('Assistant coach') != -1]

	if attribute == 'secondAssistantCoach':
		return [tag.parent.find('strong').text for tag in page.find('ul', {'class' : 'line-list'}).find_all('span', {'class' : 'role'}) if tag.text.find('Second Assistant Coach') != -1]

	if attribute == 'Doctor':
		return [tag.parent.find('strong').text for tag in page.find('ul', {'class' : 'line-list'}).find_all('span', {'class' : 'role'}) if tag.text.find('Doctor') != -1]

	if attribute == 'players':
		page = make_soup('http://www.volleyball.world/' + page.find('a', {'href' : re.compile('/en/men/teams/.*?/players')})['href'])
		return [tag.text.strip() for tag in page.find_all('a',{'href' : re.compile('/en/men/teams/.*?/players.*')})][5::3]
	if attribute == 'mostAge':
		x = 'http://www.volleyball.world' + page.find('a', {'href' : re.compile('en/men/teams/.*/facts_and_figures')})['href']
		page = make_soup(x)
		return [tag.text.strip()[:2] for tag in page.find_all('span', {'class' : 'value'})][0]
	if attribute == 'lessAge':
		x = 'http://www.volleyball.world' + page.find('a', {'href' : re.compile('en/men/teams/.*/facts_and_figures')})['href']
		page = make_soup(x)
		return [tag.text.strip()[:2] for tag in page.find_all('span', {'class' : 'value'})][1]
	if attribute == 'averageAge':
		x = 'http://www.volleyball.world' + page.find('a', {'href' : re.compile('en/men/teams/.*/facts_and_figures')})['href']
		page = make_soup(x)
		return [tag.text.strip()[:2] for tag in page.find_all('span', {'class' : 'average'})][0]
	if attribute == 'mostHeight':
		x = 'http://www.volleyball.world' + page.find('a', {'href' : re.compile('en/men/teams/.*/facts_and_figures')})['href']
		page = make_soup(x)
		return [tag.text.strip()[:2] for tag in page.find_all('span', {'class' : 'value'})][2]
	if attribute == 'lessHeight':
		x = 'http://www.volleyball.world' + page.find('a', {'href' : re.compile('en/men/teams/.*/facts_and_figures')})['href']
		page = make_soup(x)
		return [tag.text.strip()[:2] for tag in page.find_all('span', {'class' : 'value'})][3]
	if attribute == 'averageHeight':
		x = 'http://www.volleyball.world' + page.find('a', {'href' : re.compile('en/men/teams/.*/facts_and_figures')})['href']
		page = make_soup(x)
		return [tag.text.strip()[:2] for tag in page.find_all('span', {'class' : 'average'})][1]
	if attribute == 'mostSpike':
		x = 'http://www.volleyball.world' + page.find('a', {'href' : re.compile('en/men/teams/.*/facts_and_figures')})['href']
		page = make_soup(x)
		return [tag.text.strip()[:2] for tag in page.find_all('span', {'class' : 'value'})][4]
	if attribute == 'lessSpike':
		x = 'http://www.volleyball.world' + page.find('a', {'href' : re.compile('en/men/teams/.*/facts_and_figures')})['href']
		page = make_soup(x)
		return [tag.text.strip()[:2] for tag in page.find_all('span', {'class' : 'value'})][5]
	if attribute == 'averageSpike':
		x = 'http://www.volleyball.world' + page.find('a', {'href' : re.compile('en/men/teams/.*/facts_and_figures')})['href']
		page = make_soup(x)
		return [tag.text.strip()[:2] for tag in page.find_all('span', {'class' : 'average'})][2]
	if attribute == 'mostBlock':
		x = 'http://www.volleyball.world' + page.find('a', {'href' : re.compile('en/men/teams/.*/facts_and_figures')})['href']
		page = make_soup(x)
		return [tag.text.strip()[:2] for tag in page.find_all('span', {'class' : 'value'})][6]
	if attribute == 'lessBlock':
		x = 'http://www.volleyball.world' + page.find('a', {'href' : re.compile('en/men/teams/.*/facts_and_figures')})['href']
		page = make_soup(x)
		return [tag.text.strip()[:2] for tag in page.find_all('span', {'class' : 'value'})][7]
	if attribute == 'averageBlock':
		x = 'http://www.volleyball.world' + page.find('a', {'href' : re.compile('en/men/teams/.*/facts_and_figures')})['href']
		page = make_soup(x)
		return [tag.text.strip()[:2] for tag in page.find_all('span', {'class' : 'average'})][3]
	if attribute == 'mostCaps':
		x = 'http://www.volleyball.world' + page.find('a', {'href' : re.compile('en/men/teams/.*/facts_and_figures')})['href']
		page = make_soup(x)
		return [tag.text.strip()[:2] for tag in page.find_all('span', {'class' : 'value'})][8]
	if attribute == 'lessCaps':
		x = 'http://www.volleyball.world' + page.find('a', {'href' : re.compile('en/men/teams/.*/facts_and_figures')})['href']
		page = make_soup(x)
		return [tag.text.strip()[:2] for tag in page.find_all('span', {'class' : 'value'})][9]
	if attribute == 'averageCaps':
		x = 'http://www.volleyball.world' + page.find('a', {'href' : re.compile('en/men/teams/.*/facts_and_figures')})['href']
		page = make_soup(x)
		return [tag.text.strip()[:2] for tag in page.find_all('span', {'class' : 'average'})][4]
	if attribute == 'ranking':
		return
	if attribute == 'photos':
		x = 'http://www.volleyball.world' + page.find('a', {'href' : re.compile('/en/men/teams/.*?')})['href']
		page = make_soup(x)
		return [tag['src'] for tag in page.find('section', {'id' : 'photos'}).select('img')]
	if attribute == 'name':
		return page.find('h2',{'id' :'currentTeam'}).text
	if attribute == 'teamPhoto':
		return page.find('div', {'class' : 'results nohistory'}).find('img')['src']

	return
	

def get_celebrity_data_from_theFamousPeople(attribute, page):
	if attribute == 'celebrity_list':
		page = make_soup(page)
		return list(set([re.search(r'/profiles/(.*).php', tag['href']).group(1) for tag in page.find_all('a', {'href': re.compile(r'/profiles/(.*).php')})]))
	if attribute == 'name':
		return page.find('h1').text.replace(' Biography', '')
	if attribute == 'birthDay':
		return [tag for tag in page.find('div', {'class' : 'fps-desc fpf-block'}).find_all('p', {'class' : 'quickfactsdata'}) if tag.text.find('Birthday') != -1][0].text.replace('Birthday: ','')

	if attribute == 'nationality':
		return [tag for tag in page.find('div', {'class' : 'fps-desc fpf-block'}).find_all('p', {'class' : 'quickfactsdata'}) if tag.text.find('Nationality') != -1][0].find('a').text

	if attribute == 'sunSing':
		return [tag for tag in page.find('div', {'class' : 'fps-desc fpf-block'}).find_all('span', {'class' : 'quickfactstitle'}) if tag.text.find('Sun Sing') != -1][0].parent.text.replace('Sun Sign: ', '')
	if attribute == 'deathdate':
		return [tag for tag in page.find('div', {'class' : 'fps-desc fpf-block'}).find_all('p', {'class' : 'quickfactsdata'}) if tag.text.find('Died on') != -1][0].text.replace('Died on: ','')
	if attribute == 'bornIn':
		return [tag for tag in page.find('div', {'class' : 'fps-desc fpf-block'}).find_all('span', {'class' : 'quickfactstitle'}) if tag.text.find('Born') != -1][0].parent.text.replace('Born in: ', '')
	if attribute == 'deathYear':
		return int([tag for tag in page.find('div', {'class' : 'fps-desc fpf-block'}).find_all('p', {'class' : 'quickfactsdata'}) if tag.text.find('Died on') != -1][0].text.replace('Died on: ', '')[-4:])
	if attribute == 'birthyear':
		return int([tag for tag in page.find('div', {'class' : 'fps-desc fpf-block'}).find_all('p', {'class' : 'quickfactsdata'}) if tag.text.find('Birthday') != -1][0].text.replace('Birthday: ', '')[-4:])
	if attribute == 'famousAs':
		return [tag for tag in page.find('div', {'class' : 'fps-desc fpf-block'}).find_all('span', {'class' : 'quickfactstitle'}) if tag.text.find('Famous as') != -1][0].parent.text.replace('Famous as: ', '')
	if attribute == 'spouse':
		return [tag for tag in page.find('div', {'class' : 'fps-desc fpf-block'}).find_all('span', {'class' : 'quickfactstitle'}) if tag.text.find('Spouse/Ex') != -1][0].parent.text.replace('Spouse/Ex-: ', '')
	if attribute == 'father':
		return [tag for tag in page.find('div', {'class' : 'fps-desc fpf-block'}).find_all('span', {'class' : 'quickfactstitle'}) if tag.text.find('father') != -1][0].parent.text.replace('father: ', '')
	if attribute == 'mother':
		return [tag for tag in page.find('div', {'class' : 'fps-desc fpf-block'}).find_all('span', {'class' : 'quickfactstitle'}) if tag.text.find('mother') != -1][0].parent.text.replace('mother: ', '')
	if attribute == 'siblings':
		return [tag for tag in page.find('div', {'class' : 'fps-desc fpf-block'}).find_all('span', {'class' : 'quickfactstitle'}) if tag.text.find('siblings') != -1][0].parent.text.replace('siblings: ', '')
	if attribute == 'childrens':
		return [tag for tag in page.find('div', {'class' : 'fps-desc fpf-block'}).find_all('span', {'class' : 'quickfactstitle'}) if tag.text.find('children') != -1][0].parent.text.replace('children: ', '')
	if attribute == 'religion':
		return [tag for tag in page.find('div', {'class' : 'fps-desc fpf-block'}).find_all('span', {'class' : 'quickfactstitle'}) if tag.text.find('religion') != -1][0].parent.text.replace('religion: ', '')
	if attribute == 'deathAge':
		return [tag for tag in page.find('div', {'class' : 'fps-desc fpf-block'}).find_all('span', {'class' : 'quickfactstitle'}) if tag.text.find('Died At Age') != -1][0].parent.text.replace('Died At Age: ', '')
	if attribute == 'age':
		return [tag for tag in page.find('div', {'class' : 'fps-desc fpf-block'}).find_all('p', {'class' : 'quickfactsdata'}) if tag.text.find('Age') != -1][0].find('a').text[:2]
	if attribute == 'deathPlace':
		return [tag for tag in page.find('div', {'class' : 'fps-desc fpf-block'}).find_all('span', {'class' : 'quickfactstitle'}) if tag.text.find('place of death') != -1][0].parent.text.replace('place of death: ', '')
	if attribute == 'personality':
		return [tag for tag in page.find('div', {'class' : 'fps-desc fpf-block'}).find_all('p', {'class' : 'quickfactsdata'}) if tag.text.find('Personality') != -1][0].text.replace('Personality: ', '')
	if attribute == 'deathCause':
		return [tag for tag in page.find('div', {'class' : 'fps-desc fpf-block'}).find_all('p', {'class' : 'quickfactsdata'}) if tag.text.find('Cause of Death') != -1][0].find('a',{'class' : ''}).text
	if attribute == 'netWorth':
		return [tag for tag in page.find('div', {'class' : 'fps-desc fpf-block'}).find_all('span', {'class' : 'quickfactstitle'}) if tag.text.find('Net worth') != -1][0].parent.text.replace('Net worth: ', '')
	if attribute == 'photos':
		return [tag['src'] for tag in page.find('div', {'class' : 'carousel-inner '}).find_all('img',{'class' : 'carousel-desktop img-responsive hide_on_mobile'})]
	
	
	return


def get_musicArtist_data_from_discogs(attribute, page):
	if attribute == 'musicArtist_list':
		page = make_soup(page)
		return list(set([re.search(r'/artist/(.*)', tag['href']).group(1) for tag in page.find_all('a', {'href': re.compile(r'/artist/(.*)')})]))
	if attribute == 'name':
		return page.find('div', {'class' : 'profile'}).find('h1', {'class' : 'hide_mobile'}).text
	if attribute == 'realName':
		return page.find('div', {'class' : 'profile'}).find('div', {'class' : 'content'}).text
	if attribute == 'profile':
		return page.find('div', {'class' : 'profile'}).find('div', {'id' : 'profile'}).text.strip()
	if attribute == 'aliases':
		return [tag for tag in page.find('div', {'class' : 'profile'}).find_all('div', {'class' : 'head'}) if tag.text.find('Aliases') != -1][0].findNext().text.strip().replace(' \n                ', '')
	if attribute == 'inGroups':
		return [tag.findNext().text.strip().replace(' \n               ', '') for tag in page.find('div', {'class' : 'profile'}).find_all('div', {'class' : 'head'}) if tag.text.find('In Groups') != -1][0]
	if attribute == 'variations':
		return page.find('div', {'id' : 'anvs'}).text.strip()
	if attribute == 'members':
		return [tag.findNext().text.strip().replace(' \n                   ', '') for tag in page.find('div', {'class' : 'profile'}).find_all('div', {'class' : 'head'}) if tag.text.find('Members') != -1][0]
	if attribute == 'photos':
		x = 'https://www.discogs.com' + page.find('a', {'href' : re.compile('/artist/.*/images')})['href']
		x=make_soup(x)
		[tag['src'] for tag in x.find('div', {'id' : 'view_images'}).select('img')]


	return


def collect_data_id_from_resource(pages, base, pattern, timeout=10**3, debug=False):
	start_time 		= time()
	checked_id 		= []
	
	for i, page in enumerate(pages):
		
		souped_page = make_soup(page, delay=0)
		
		new_pages = [tag['href'] for tag in souped_page.find_all('a', {'href': re.compile('({base})?/.*')})] + [page]
		
		new_pages =  [base + page if page.find('http') == -1 else page for page in new_pages]

		new_pages =  [page for page in new_pages if page[5:].find('http') == -1]
		
		new_pages = list(set(new_pages) - set(pages))
		
		for new_page in new_pages:
		
			if debug:
				try: print(i, new_page)
				except Exception as error: print(error)
				sleep(0.1)
				
			new_id_re = re.search(f'({base})?{pattern}', new_page)
			
			if new_id_re and new_id_re.group(2) not in checked_id:
						
				if debug:
					try: print(new_page)
					except Exception as error: print(error)
					
				
				yield new_id_re.group(2)
				checked_id += [new_id_re.group(2)]
				
			if re.search(f'{base}.*', new_page) and new_page not in pages: pages += [new_page]
			
			
			if time() - start_time > timeout:
				return


def collect_volleyballTeam_id_from_volleyballWorld(pages, timeout=10**3):
	return collect_data_id_from_resource(pages, 'https://volleyball.world', '/en/men/teams/(.*)', timeout) 


def collect_word_id_from_merriam(pages, timeout=10**3):
	return collect_data_id_from_resource(pages, 'https://www.merriam-webster.com', '/dictionary/(.*)', timeout) 


def collect_celebrity_id_from_theFamousPeople(pages, timeout=10**3):
	return collect_data_id_from_resource(pages, 'https://www.thefamouspeople.com', '/profiles/(.*).php', timeout) 


def collect_musicArtist_id_from_discogs(pages, timeout=10**3):
	return collect_data_id_from_resource(pages, 'https://www.discogs.com', '/artist/(.*)', timeout) 


def collect_footballTeam_id_from_sofifa(pages, data_count=700, timeout=10 ** 3, checked_id=[], checked_pages=[]):
	return collect_data_id_from_resource(pages, 'https://sofifa.com', '/team/([^/]*).*?', data_count=data_count, timeout=timeout, checked_id=checked_id, checked_pages=checked_pages, recursive=False)


def collect_footballPlayer_id_from_sofifa(pages, data_count=15000, timeout=10**3 , checked_id=[], checked_pages=[]):
	return collect_data_id_from_resource(pages, 'https://sofifa.com', '/player/([^/]*).*?', data_count=data_count, timeout=timeout, checked_id=checked_id, checked_pages=checked_pages, recursive=False)


def collect_author_id_from_goodreads(pages, data_count=10, timeout=10**3 , checked_id=[], checked_pages=[]):
	return collect_data_id_from_resource(pages, 'https://www.goodreads.com', '/author/show/([^/]*)$', data_count=data_count, timeout=timeout, checked_id=checked_id, checked_pages=checked_pages)


def collect_book_id_from_goodreads(pages, data_count=10, timeout=10**3 , checked_id=[], checked_pages=[]):
	return collect_data_id_from_resource(pages, 'https://www.goodreads.com', '/book/show/([0-9]*?-[^/]*)$', data_count=data_count, timeout=timeout, checked_id=checked_id, checked_pages=checked_pages)


def collect_country_id_from_cia(pages, data_count=10, timeout=10**3 , checked_id=[], checked_pages=[]):
	return collect_data_id_from_resource(pages, 'https://www.cia.gov/library/publications/the-world-factbook/geos', '/(.*?).html', data_count=data_count, timeout=timeout, checked_id=checked_id, checked_pages=checked_pages)


def collect_people_id_from_biography(pages, data_count=10, timeout=10**3 , checked_id=[], checked_pages=[]):
	return collect_data_id_from_resource(pages, 'https://biography.com', '/people/([^/]*).*?', data_count=data_count, timeout=timeout, checked_id=checked_id, checked_pages=checked_pages)


def collect_anime_id_from_myanimelist(pages, data_count=10, timeout=10**3 , checked_id=[], checked_pages=[]):
	return collect_data_id_from_resource(pages, 'https://myanimelist.net', '/anime/([^/]*).*?', data_count=data_count, timeout=timeout, checked_id=checked_id, checked_pages=checked_pages)


def collect_movie_id_from_imdb(pages, data_count=10, timeout=10**3 , checked_id=[], checked_pages=[]):

	for page in pages:
		checked_id += [re.search('/title/(tt[0-9]*).*?', tag['href']).group(1) for tag in make_soup(page).find_all('a', {'href': re.compile('/title/.*?')})]

	return checked_id, pages, pages

	#def check_page(page):
	#	try: return page.select('div.title_wrapper')[0].text.find('TV Series') == -1
	#	except: return False
	#
	#return collect_data_id_from_resource(pages, 'https://imdb.com', '/title/(tt[0-9]*)(/[?][^/]*)?$', data_name='movie', data_check_module=check_page, data_count=data_count, timeout=timeout, checked_id=checked_id, checked_pages=checked_pages)


def collect_actor_id_from_imdb(pages, data_count=10, timeout=10**3 , checked_id=[], checked_pages=[]):

	for page in pages:
		checked_id += [re.search('/name/(nm[0-9]*)/.*?', tag['href']).group(1) for tag in make_soup(page).find_all('a', {'href': re.compile('/name/.*?st.*?')})]

	return checked_id, pages, pages

	#def check_page(page):
	#	try: return bool('#actor' in [tag['href'] for tag in page.select('div#name-job-categories')[0].find_all('a', {'href': re.compile('#.*?')})])
	#	except: return False
	#
	#return collect_data_id_from_resource(pages, 'https://imdb.com', '/name/(nm[0-9]*)(/[?][^/]*)?$', data_name='director', data_count=data_count, data_check_module=check_page, timeout=timeout, checked_id=checked_id, checked_pages=checked_pages)


def collect_director_id_from_imdb(pages, data_count=10, timeout=10**3, checked_id=[], checked_pages=[]):

	for page in pages:
		checked_id += [re.search('/name/(nm[0-9]*)/.*?', tag['href']).group(1) for tag in make_soup(page).find_all('a', {'href': re.compile('/name/.*?dr.*?')})]

	return checked_id, pages, pages

	#def check_page(page):
	#	try: return bool('#director' in [tag['href'] for tag in page.select('div#name-job-categories')[0].find_all('a', {'href': re.compile('#.*?')})])
	#	except: return False
	#
	#return collect_data_id_from_resource(pages, 'https://imdb.com', '/name/(nm[0-9]*)(/[?][^/]*)?$', data_name='director', data_count=data_count, data_check_module=check_page, timeout=timeout, checked_id=checked_id, checked_pages=checked_pages)





if __name__ == '__main__':
	print(collect_footballPlayer_id_from_sofifa([f'https://sofifa.com/players?offset={i}' for i in range(0, 6000, 60)]))
