import modules.database_manager as dbManager
import argparse
import sys

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


def old_arg_parse():
    """
    """

    parser = argparse.ArgumentParser()

    parser.add_argument('--test_getter', action='store_true', dest='test_getter',
                        default=False, help='test getter modules')

    parser.add_argument('--download_resources', action='store_true', dest='download_resources',
                        default=False, help='download resources')

    parser.add_argument('--update_db', action='store_true', dest='update_db',
                        default=False, help='updating database')

    parser.add_argument('--find_db', action='store_true', dest='find_db',
                        default=False, help='finding database id')

    parser.add_argument('--init_db', action='store_true', dest='init_db',
                        default=False, help='initializing database')

    parser.add_argument('-resource', type=str, dest='resource',
                        help='resource of test data')

    parser.add_argument('-db', type=str, dest='db',
                        help='db of test data')

    parser.add_argument('-attributes', type=str, nargs='+', dest='attributes', default=None,
                        help='attribute of test data')

    parser.add_argument('-count', type=int, dest='count', default=None,
                        help='number of test datas')

    parser.add_argument('-id', type=str, nargs='+', dest='id',
                        help='data id s to be tested')

    parser.add_argument('-resume', action='store_true', dest='resume', default=False,
                        help='specify the resume arg in download_resources function')

    parser.add_argument('-dont_use_local_save', action='store_true', dest='dont_use_local_save', default=False,
                        help='specify whether should use local saved pages in make_spup funtion or not')

    parser.add_argument('-dont_save_page_local', action='store_true', dest='dont_save_page_local', default=False,
                        help='specify whether should use local saved pages in make_spup funtion or not')

    parser.add_argument('-complete_report', action='store_true', dest='complete_report', default=False,
                        help='gives complete eport of task')

    args = parser.parse_args()

    config.use_local_save = not args.dont_use_local_save
    config.save_page_local = not args.dont_save_page_local

    if args.test_getter:
        logger.critical('test results : ')
        pprint(test_getter(args.db, args.resource, args.attributes, count=args.count, id_list=args.id,
                           complete_report=args.complete_report))

    elif args.download_resources:
        download_resources(args.resource, args.db, count=args.count, resume=args.resume)

    elif args.update_db:
        update_db(args.db)

    elif args.find_db:
        find_db(args.db)

    elif args.init_db:
        init_db(args.db)
