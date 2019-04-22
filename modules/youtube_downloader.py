from __future__ import unicode_literals
from modules.tools import *
from pprint import pprint



import multiprocessing as mp
import youtube_dl
import re



class MyLogger(object):
	def debug(self, msg):
		pass

	def warning(self, msg):
		pass

	def error(self, msg):
		print(msg)


def my_hook(d):
	if d['status'] == 'finished':
		print('Done downloading, now converting ...')


def search(query, _type='video'):
	items = []
	
	type_key = {
		'video'		: 'EgIQAQ%253D%253D',
		'playlist'	: 'EgIQAw%253D%253D'
	}
	
	url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}&sp={type_key[_type]}"

	page = make_soup(url)
	
	tags = {
		'video': page.select('div.yt-lockup.yt-lockup-tile.yt-lockup-video.vve-check.clearfix'),
		'playlist': page.select('div.yt-lockup.yt-lockup-tile.yt-lockup-playlist.vve-check.clearfix')
	}
	
	for tag in tags[_type]:
		if _type == 'video':
			item = {
				'title': tag.select('h3.yt-lockup-title')[0].find('a').text,
				'url': 'https://www.youtube.com' + tag.find('a')['href'],
				'length': sum([int(t) * (60 ** i) for i, t in enumerate(tag.select('span.video-time')[0].text.split(':'))])
			}
		
		if _type == 'playlist':
			item = {
				'title': tag.select('h3.yt-lockup-title')[0].find('a').text,
				'url': 'https://www.youtube.com' + tag.find('a', {'href': re.compile('.*?playlist.*?')})['href'],
				'count': re.search('(.*?) .*', tag.select('span.formatted-video-count-label')[0].text).group(1)
			}
		
		#pprint(item)
		
		items.append(item)
		
	return items


def search_music(name, mode='song', _type='video', count=1):
	if mode == 'song':
		items = search(name + ' lyric', _type=_type)

	if mode == 'soundtrack':
		items = search(name + 'soundtrack', _type=_type)
	
	if _type == 'video':
		items = [item for item in items if 0.5 * 60 < item['length'] < 4 * 60]
	
	if _type == 'playlist':
		pass
	
	
	return items[:count]
	

def download_music(page, output=None):
	
	if output:
		if output[-4:] != '.mp3':
			output += '.mp3'
	else:
		pass
	output = '%(title)s-%(id)s.%(ext)s'

	ydl_opts = {
		'format': 'bestaudio',
		'postprocessors': [{
		    'key': 'FFmpegExtractAudio',
		    'preferredcodec': 'mp3',
		    'preferredquality': '192'
		}],
		#'logger': MyLogger(),
		'progress_hooks': [my_hook],
		'outtmpl': output,
		'noplaylist' : True
	}
	
	ydl = youtube_dl.YoutubeDL(ydl_opts)
	
	info_dict = ydl.extract_info(page, download=True)
	
	file_name = re.search('(.*)\..*', ydl.prepare_filename(info_dict)).group(1) + '.mp3'
	
	print('/'*50, file_name)

	return file_name
	
	
		
def download(**args):
	pages = []
	
	if args['mode'] in ['song', 'soundtrack']:
		pages = search_music(**args)
		
		pprint(pages)
		
		with mp.Pool() as pool:
			musics = pool.map(download_music, [page['url'] for page in pages])
		
		return musics
		


if __name__ == '__main__':
	
	
	download_music('https://www.youtube.com/watch?v=lbjhxiI5V_E&index=2&t=0s&list=PLSbaCD6mVGhe0S9tSlClE3ZyMZEQDtAgV', 'kjn')
	
	print('hh')
	#music = download_music('https://www.youtube.com/watch?v=TAtORG6H-Z0')
	
	#download(name='rick and morty', mode='soundtrack', _type='playlist', count=1)
	
