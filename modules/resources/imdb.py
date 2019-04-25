res = {
    'movie': {

        'movie_list': [f'https://www.imdb.com/search/title?title_type=feature&count={250}&start={i + 1}' for i in range(0, 10000, 250)]
                    + [f'https://www.imdb.com/search/title?title_type=feature&sort=num_votes,desc&count={250}&start={i + 1}' for i in range(0, 10000, 250)],

        'movie': 'https://www.imdb.com/title/{data_id}',

        'base': 'https://www.imdb.com',

        'movie_pattern': r'(title\/[a-z0-9]*).*?$',

        'summaries_pattern': r'(\/title\/[a-z0-9]*\/plotsummary).*?$',

        'mediaindex_pattern': r'(\/title\/[a-z0-9]*\/mediaindex).*?$',

        'videogallery_pattern': r'(\/title\/[a-z0-9]*\/videogallery).*?$',

        'quotes_pattern': r'(\/title\/[a-z0-9]*\/quotes).*?$',

        'taglines_pattern': r'(\/title\/[a-z0-9]*\/taglines).*?$',

        'keywords_pattern': r'(\/title\/[a-z0-9]*\/keywords).*?$',

        'trivia_pattern': r'(\/title\/[a-z0-9]*\/trivia).*?$'
    
    },
    
    'actor': {

        'actor_list': [f'https://www.imdb.com/search/title?title_type=feature&count={250}&page={int((i+1)/250 + 1)}' for i in range(0, 10000, 250)]
                    + [f'https://www.imdb.com/search/title?title_type=feature&sort=num_votes,desc&count={250}&page={int((i+1)/250 + 1)}' for i in range(0, 10000, 250)],

        'actor': 'https://www.imdb.com/name/{data_id}',

        'base': 'https://www.imdb.com',

        'actor_pattern': r'',
        
    },
    
    'director': {

        'director_list': [f'https://www.imdb.com/search/title?title_type=feature&count={250}&page={int((i+1)/250 + 1)}' for i in range(0, 10000, 250)]
                       + [f'https://www.imdb.com/search/title?title_type=feature&sort=num_votes,desc&count={250}&page={int((i+1)/250 + 1)}' for i in range(0, 10000, 250)],
        
        'director': 'https://www.imdb.com/name/{data_id}',

    },
}