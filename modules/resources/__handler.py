import glob
import re
import importlib

files = [re.search('.*?([A-Za-z]*?).py', file).group(1) for file in 
            glob.glob('./modules/resources/*.py') if not re.search('__[a-zA-Z]*.py', file)]

Resources = {file: importlib.import_module(f'modules.resources.{file}').res for file in files}
