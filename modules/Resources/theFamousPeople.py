theFamousPeople = {
    'celebrity': {
        
        'celebrity': 'https://www.thefamouspeople.com/profiles/{data_id}.php',
        
        'celebrity_list' :list(itertools.chain.from_iterable([[f'https://www.thefamouspeople.com/{type}.php?page={i}' for i in range(1,10)] for type in ["singers"]])),
    
    },
}