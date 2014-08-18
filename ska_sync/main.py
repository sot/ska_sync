"""
Synchronize data files for Ska runtime environment

Examples
========

Arguments
=========
"""
import os
import re

import yaml

from .version import __version__
from ska_path import ska_path

PACKAGE_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'ska_sync_config')
SKA_CONFIG_PATH = os.path.join(ska_path(), 'ska_sync_config')  # `None` if path doesn't exist

def get_opt():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--user',
                        help='User name for remote host')

    parser.add_argument('--install',
                        action='store_true',
                        help='Install sync config file in default location')

    parser.add_argument('--force',
                        action='store_true',
                        help='Force overwrite of sync config file')

    opt = parser.parse_args()
    return opt


def install(opt):
    import shutil
    in_path = PACKAGE_CONFIG_PATH
    out_path = SKA_CONFIG_PATH
    if os.path.exists(out_path) and not opt.force:
        print('ERROR: ska sync config file {} already exists.  Use --force option to overwrite.')

    with open(in_path, 'r') as fh:
        config_text = fh.read()

    # Change hardwired default comment
    if opt.user:
        config_text = re.sub(r'# user: name', 'user: {}'.format(opt.user), config_text)

    with open(out_path, 'w') as fh:
        fh.write(config_text)

    print('Wrote ska sync config file to {}'.format(out_path))


def file_sync(packages, user, host):
    """
    Sync files for packages assuming location in $SKA/data/<package>/.
    """
    files = []
    for package in sorted(packages):
        paths = packages[package]
        for path in sorted(paths):
            files.append('data/{}/{}\n'.format(package, path))

    sync_files_path = os.path.join(ska_path(), 'ska_sync_files')
    with open(sync_files_path, 'w') as fh:
        fh.writelines(files)

    rsync_cmd = ()
    print('\n'
          'COPY and PASTE the following at your terminal command line prompt:\n\n'
          '  rsync -arzv --progress --size-only --files-from="{sync_files_path}" \\\n'
          '    {user}@{host}:/proj/sot/ska/ "{ska_path}/"\n'
          .format(user=user, host=host, ska_path=ska_path(), sync_files_path=sync_files_path))


def main():
    opt = get_opt()
    if opt.install:
        install(opt)
        return

    config_path = SKA_CONFIG_PATH or PACKAGE_CONFIG_PATH
    config = yaml.safe_load(open(config_path, 'r'))
    print('Loaded config from {}'.format(config_path))

    # Remote user name
    user = opt.user or config.get('user') or os.environ['USER']

    file_sync(config['file_sync'], user, config['host'])
