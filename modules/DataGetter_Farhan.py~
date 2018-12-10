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
import youtube_downloader



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



