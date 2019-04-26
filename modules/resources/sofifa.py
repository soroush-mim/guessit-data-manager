res = {
    'footballPlayer': {

        'footballPlayer_list': [f'https://sofifa.com/players?offset={i}' for i in range(0, 15000, 60)],

        'footballPlayer': 'https://sofifa.com/player/{data_id}',

        'base': 'https://sofifa.com',

        'footballPlayer_pattern': r'(\/player\/[0-9]*).*?$',

    },

    'footballTeam': {

        'footballTeam_list': [f'https://sofifa.com/teams?offset={i}' for i in range(0, 700, 60)],

        'footballTeam': 'https://sofifa.com/team/{data_id}',

        'base': 'https://sofifa.com',

        'footballTeam_pattern': r'(\/team\/[0-9]*).*?$',

    },
}
