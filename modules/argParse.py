import argparse

import modules.DatabaseManager as dbManager

def arg_parse():
    '''
    command line interface
    '''

    parser = argparse.ArgumentParser(description='Process some integers.')
    
    parser.add_argument(
        '-dr', '--dlres',
        dest='dlres', default=None,
        type=str, nargs=2,
        help='run the download resource function\napp.py -dr <resource> <db_name>',
    )

    args = parser.parse_args()

    if args.dlres:
        dbManager.download_resources(args.dlres[0], args.dlres[1])

    # if there is any arg, return True
    if (len(sys.argv) == 1) or (len(sys.argv) == 2 and sys.argv[1] =='-log'):
        return False
    else:
        return True
