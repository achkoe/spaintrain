#!/usr/bin/env python3

"""Create a script to check out or export files and paths from git or Subversion to certain locations.

Fill me
"""

import argparse
import os
import pprint
from urllib.parse import urlparse
import sys
import yaml


def parse_configuration(configlist, rootpath):
    assert isinstance(configlist, list), 'configuration is not a list'
    assert all([isinstance(item, dict) for item in configlist]), 'configuration contains items which are not a dict'
    assert all(['command' in item for item in configlist]), 'configuration contains items with no command'

    for item in configlist:
        print(item['command'])
        if not isinstance(item['command'], list):
            item['command'] = [item['command']]
        for index, _ in enumerate(item['command']):
            for key in ['path', 'url', 'revision']:
                if key not in item:
                    continue
                # replace (<key>) occurences in command with the actual value
                item['command'][index] = item['command'][index].replace("({})".format(key), str(item[key]))
            item['command'][index] = item['command'][index].replace('(root)', rootpath)


def write_output(configlist, platform):
    for item in configlist:
        print('\n'.join([str(_) for _ in item['command']]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        epilog="\n".join(__doc__.splitlines()[1:]),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-c', '--config', dest='configfile', default='config.yaml', help='configuration file, default %(default)s')
    parser.add_argument('-r', '--root', dest='rootpath', default=os.getcwd(), help='root path the check out to, default %(default)s')
    parser.add_argument('-p', '--platform', choices=['win32', 'linux'], default=sys.platform, help='create a script for platform, default %(default)s')
    argobj = parser.parse_args()
    with open(argobj.configfile) as fh:
        config = yaml.load(fh, Loader=yaml.FullLoader)
    parse_configuration(config, argobj.rootpath)
    pprint.pprint(config)
    write_output(config, argobj.platform)


