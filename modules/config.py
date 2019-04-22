import itertools
import logging

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
						'movie_pattern': r'(title\/[a-z0-9]*).*?$'
						,
						'summaries_pattern': r'(\/title\/[a-z0-9]*\/plotsummary).*?$'
						,
						'mediaindex_pattern': r'(\/title\/[a-z0-9]*\/mediaindex).*?$'
						,
						'videogallery_pattern': r'(\/title\/[a-z0-9]*\/videogallery).*?$'
						,
						'quotes_pattern': r'(\/title\/[a-z0-9]*\/quotes).*?$'
						,
						'taglines_pattern': r'(\/title\/[a-z0-9]*\/taglines).*?$'
						,
						'keywords_pattern': r'(\/title\/[a-z0-9]*\/keywords).*?$'
						,
						'trivia_pattern': r'(\/title\/[a-z0-9]*\/trivia).*?$'
					}
					,
					'actor': {
						'actor_list': [f'https://www.imdb.com/search/title?title_type=feature&count={250}&page={int((i+1)/250 + 1)}' for i in range(0, 10000, 250)]
									+ [f'https://www.imdb.com/search/title?title_type=feature&sort=num_votes,desc&count={250}&page={int((i+1)/250 + 1)}' for i in range(0, 10000, 250)]
						,
						'actor': 'https://www.imdb.com/name/{data_id}'
						,
						'base': 'https://www.imdb.com'
						,
						'actor_pattern': r''
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
						,
						'base': 'https://sofifa.com'
						,
						'footballPlayer_pattern': r'(\/player\/[0-9]*).*?$'
						
					}
					,
					'footballTeam': {
						'footballTeam_list': [f'https://sofifa.com/teams?offset={i}' for i in range(0, 700, 60)]
						,
						'footballTeam': 'https://sofifa.com/team/{data_id}'
						,
						'base': 'https://sofifa.com'
						,
						'footballTeam_pattern': r'(\/team\/[0-9]*).*?$'
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


# --------------------------------------------------------------------
# project data config
# --------------------------------------------------------------------

main_dir			= './..'
project_dir			= f'{main_dir}/guessit-data-manager'
dataset_dir			= f'{main_dir}/datasets'
process_count	   	= 4
updating_step	   	= 10
finding_step	   	= 10
expiration_time	 	= 60 * 60 * 10
backup			  	= False
debug			   	= False
safe_mode		   	= False

sftp 				= None

local_save			= False
save_page_local		= True


# --------------------------------------------------------------------
# logger config
# --------------------------------------------------------------------

logging.basicConfig(
    datefmt='%y-%b-%d %H:%M:%S',
    format='%(levelname)8s:[%(asctime)s][%(filename)20s:%(lineno)4s -%(funcName)20s() ]: %(message)s',

    # datefmt='%H:%M:%S',
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler(f'{project_dir}/log.log', mode='w+', encoding='utf8', delay=0),
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger('DataManager')