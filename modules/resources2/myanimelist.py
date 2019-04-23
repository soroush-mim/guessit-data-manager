myanimelist = {
    'anime': {
        
        'anime': 'https://www.myanimelist.net/anime/{data_id}',
        
        'anime_list': [f'https://myanimelist.net/topanime.php?limit={i}' for i in range(0, 20000, 50)],

    },
},