import itertools

res = {
    'word': {
        
        'word' : 'https://www.merriam-webster.com/dictionary/{data_id}',
        
        'word_list' : list(itertools.chain.from_iterable([[f'https://www.merriam-webster.com/browse/dictionary/{char}/{i}' for i in range(1,100)] for char in "qwertyuiopasdfghjklzxcvbnm"])),

    },
}
