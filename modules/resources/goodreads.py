import itertools

res = {
    'book': {

        'book': 'https://www.goodreads.com/book/show/{data_id}',
        
        'book_list': list(itertools.chain.from_iterable([[f'https://www.goodreads.com/book/popular_by_date/{i}/{j}' for j in range(1, 13)] for i in range(2010, 2018)])),

    },

    'author': {

        'author': 'https://www.goodreads.com/author/show/{data_id}',
        
        'author_list': list(itertools.chain.from_iterable([[f'https://www.goodreads.com/book/popular_by_date/{i}/{j}' for j in range(1, 13)] for i in range(2010, 2018)])),
    
    },
}
