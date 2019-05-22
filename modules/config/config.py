import logging
import yaml
import attrdict
from log4mongo.handlers import MongoHandler
from pymongo import MongoClient


with open("./modules/config/config.yml" , 'r') as yamlfileobj:
    config = attrdict.AttrDict(yaml.safe_load(yamlfileobj))


logging.basicConfig(
    # datefmt='%y-%b-%d %H:%M:%S',
    datefmt='%H:%M:%S',
    format='%(levelname)8s:[%(asctime)s][%(funcName)20s()][%(lineno)4s]: %(message)s',

    level=logging.DEBUG,
    handlers=[
        # logging.FileHandler(f'{config.dir.project}/log.log', mode='w+', encoding='utf8', delay=0),
        logging.StreamHandler(),
        MongoHandler(host=config.mongo.ip, port=config.mongo.port,
                     username=config.mongo.username, password=config.mongo.password,
                     authentication_db=config.mongo.authentication_db, database_name='DataManager', collection='log')
    ]
)

logger = logging.getLogger('DataGeters')

mongo_client = MongoClient(
    f'mongodb://{config.mongo.username}:{config.mongo.password}@{config.mongo.ip}:{config.mongo.port}'
    f'/?authSource={config.mongo.authentication_db}')
