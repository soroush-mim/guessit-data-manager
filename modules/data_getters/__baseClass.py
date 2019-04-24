from modules.config.config import logger
class DataGetter_BaseClass:
    """a parent class for all data getters classes that get page soup file for input"""
    def __init__(self , page):
        self.page = page
    
    def get_all_data(self):
        """a function for getting all data of a player and put it in a dictionary"""
        data = {}
        for _property in [x for x in dir(self) if x.startswith('getter_')]:

            try:
                data[_property.replace('getter_', '')] = getattr(self, _property)

            except Exception as error:
                data[_property.replace('getter_', '')] = None
                logger.error(error)
                
        return data    