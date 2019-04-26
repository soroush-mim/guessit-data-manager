import logging

# --------------------------------------------------------------------
# project data config
# --------------------------------------------------------------------

main_dir			= './..'
project_dir			= f'{main_dir}/guessit-data-manager'
dataset_dir			= f'{main_dir}/datasets'
process_count	   	= 4
updating_step	   	= 10
finding_step	   	= 10
expiration_time	 	= 60 * 60 * 10
backup			  	= False
debug			   	= False
safe_mode		   	= False

sftp 				= None

local_save			= False
save_page_local		= True


# --------------------------------------------------------------------
# logger config
# --------------------------------------------------------------------

logging.basicConfig(
    # datefmt='%y-%b-%d %H:%M:%S',
    datefmt='%H:%M:%S',
    format='%(levelname)8s:[%(asctime)s][%(funcName)20s()]: %(message)s',

    level=logging.DEBUG,
    handlers=[
        logging.FileHandler(f'{project_dir}/log.log', mode='w+', encoding='utf8', delay=0),
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger('DataGeters')
