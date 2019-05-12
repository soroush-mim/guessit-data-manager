import re

from modules.data_getters.__baseClass import DataGetterBaseClass

class Getter_footballLeague_soccerway(DataGetterBaseClass):
    
    def __init__(self , page):
        
        DataGetterBaseClass.__init__(self, page)
