import argparse
import sys
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
        help='run the download resource function\n app.py -dr <resource> <db_name>',
    )
    parser.add_argument(
        '-fd', '--finddb',
        dest='finddb', default=None,
        type=str, nargs=1,
        help='Createss dataset with only id\n app.py -fd <db_name>',
    )
    parser.add_argument(
        '-ud', '--updatedb',
        dest='updatedb', default=None,
        type=str, nargs=1,
        help='Update all fields of dataset using data getterds\n app.py -ud <db_name>',
    )
    parser.add_argument(
        '-inpr', '--initproject',
        dest='initproject', default=None,
        type=str, nargs='*',
        help='initialize project and prepare folder structure\n app.py -inpr <db_name>',
    )

    args = parser.parse_args()

    if args.dlres:
        dbManager.download_resources(args.dlres[0], args.dlres[1])

    if args.finddb:
        dbManager.find_db(args.finddb[0])
    
    if args.updatedb:
        dbManager.update_db(args.updatedb[0])
    
    if args.initproject:
        dbManager.init_project()

    # if there is any arg, return True
    if (len(sys.argv) == 1) or (len(sys.argv) == 2 and sys.argv[1] =='-log'):
        return False
    else:
        return True
