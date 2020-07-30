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


def get_svn_command(configitem):
    addopt = []
    addopt += ['--revision', configitem['revision']] if 'revision' in configitem else []
    return ['checkout', '--non-interactive', '--depth', 'infinity'] + addopt + [configitem['url'], configitem['path']]


def get_git_command(configitem):
    addopt = ['clone']
    addopt += ['--branch', configitem['branch']] if 'branch' in configitem else []
    return addopt + [configitem['url'], configitem['path']]


def parse_configuration(configlist, rootpath):
    assert isinstance(configlist, list), 'configuration is not a list'
    assert all([isinstance(item, dict) for item in configlist]), 'configuration contains items which are not a dict'
    for key in ['url', 'path']:
        assert all([key in item for item in configlist]), 'configuration contains items with no {key}'.format(key=key)
    scmtypelist = ('git', 'svn')
    for item in configlist:
        # check or determine scm type
        if 'scmtype' in item:
            assert item['scmtype'] in scmtypelist, 'invalid value for scmtype: {!r}'.format(item['scmtype'])
        else:
            po = urlparse(item['url'])
            if po.path.endswith('.git') or po.netloc.startswith('dettgit'):
                item['scmtype'] = 'git'
            elif po.path.startswith('/svn') or po.netloc.startswith('dettsvn'):
                item['scmtype'] = 'svn'
            else:
                raise AssertionError('unable to determine scm type from url')
        # replace '(root)' occurences in path with the actual root path and normalize path
        item['path'] = os.path.abspath(item['path'].replace('(root)', rootpath))
        # add command if not already existing
        if 'command' not in item:
            item['command'] = [get_git_command, get_svn_command][scmtypelist.index(item['scmtype'])](item)
        else:
            assert isinstance(item['command'], list), 'command is not a list'
            for index, _ in enumerate(item['command']):
                item['command'][index] = item['command'][index].replace('(root)', rootpath)
                item['command'][index] = item['command'][index].replace('(url)', item['url'])


def write_output(configlist, platform):
    for item in configlist:
        print("{} {}".format(item['scmtype'], ' '.join([str(_) for _ in item['command']])))


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


