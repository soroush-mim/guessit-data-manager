# from modules.resources.imdb import imdb
# from modules.resources.sofifa import sofifa
# from modules.resources.goodreads import goodreads
# from modules.resources.cia import cia
# from modules.resources.biography import biography
# from modules.resources.myanimelist import myanimelist
# from modules.resources.discogs import discogs
# from modules.resources.merriam import merriam
# from modules.resources.volleyballWorld import volleyballWorld
# from modules.resources.theFamousPeople import theFamousPeople

import glob
import re
import importlib

files = [re.search('.*?([A-Za-z]*?).py', file).group(1) for file in 
            glob.glob('./modules/resources/*.py') if not re.search('__[a-zA-Z]*.py', file)]

Resources = {file: importlib.import_module(f'modules.resources.{file}').res for file in files}

# # from modules.resources import *

# Resources = {
#     'imdb'             : imdb,
#     'sofifa'           : sofifa,
#     'goodreads'        : goodreads,
#     'cia'              : cia,
#     'biography'        : biography,
#     'myanimelist'      : myanimelist,
#     'discogs'          : discogs,
#     'merriam'          : merriam,
#     'volleyballWorld'  : volleyballWorld,
#     'theFamousPeople'  : theFamousPeople,
# }
