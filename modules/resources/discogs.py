res = {
    'song': {
        #'song': ''
        #,
        #'song_list': []
    },
    
    'musicArtist': {
        
        'musicArtist': 'https://www.discogs.com/artist/{data_id}',
        
        'musicArtist_list': [f'https://www.discogs.com/search/?sort=want%2Cdesc&type=artist&page={i}' for i in range(1, 200)],

    },
},