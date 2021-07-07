"""
Synchronize data files for Ska runtime environment

Examples
========

Arguments
=========
"""
import os
import getpass
import time
import textwrap
from pathlib import Path

import yaml

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

    parser.add_argument('--sync-mp',
                        action='store_true',
                        help='Sync mission planning files relevant to ACA for current year')

    parser.add_argument('--fix-mp-links',
                        action='store_true',
                        help='Fix mission planning ofls symlinks')

    opt = parser.parse_args()
    return opt


def install(opt):
    import shutil
    in_path = PACKAGE_CONFIG_PATH
    out_path = SKA_CONFIG_PATH
    if os.path.exists(out_path) and not opt.force:
        print('ERROR: ska sync config file {} already exists.  Use --force option to overwrite.'
              .format(out_path))
        return

    shutil.copy(in_path, out_path)
    print('Wrote ska sync config file to {}'.format(out_path))


def file_sync(packages, user, host, sync_mp=False):
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

    print('\n'
          'COPY and PASTE the following at your terminal command line prompt:\n\n'
          'rsync -arzv --progress --files-from="{sync_files_path}" \\\n'
          '  {user}@{host}:/proj/sot/ska/ "{ska_path}/"\n'
          .format(user=user, host=host, ska_path=ska_path(), sync_files_path=sync_files_path))

    year = time.localtime().tm_year
    if sync_mp:
        cmd = f"""\
              rsync -arzv --prune-empty-dirs \\
                --include "*/" \\
                --include "ofls" \\
                --include="CR*.tlr" \\
                --include="CR*.backstop" \\
                --include="starcheck.txt" \\
                --include="*.pkl.gz" \\
                --include="mps/md*.dot" \\
                --include="mps/or/*.or" \\
                --include="mps/ode/characteristics/CHARACTERIS_*" \\
                --include="mps/m*.sum" \\
                --include="output/*_ManErr.txt" \\
                --include="output/*_dynamical_offsets.txt" \\
                --include="output/TEST_mechcheck.txt" \\
                --include="History/ATTITUDE.txt" \\
                --include="History/DITHER.txt" \\
                --include="History/FIDSEL.txt" \\
                --include="History/RADMON.txt" \\
                --include="History/SIMFOCUS.txt" \\
                --include="History/SIMTRANS.txt" \\
                --exclude="*" \\
                {user}@{host}:/data/mpcrit1/mplogs/{year}/ \\
                {ska_path()}/data/mpcrit1/mplogs/{year}/"""
        cmd = textwrap.dedent(cmd)
        print(cmd)
        print()
        print('ska_sync --fix-mp-links')
        print()


def fix_mp_links():
    """Fix SOT MP ofls -> oflsa link

    SOT MP uses absolute links like::

      APR0620/ofls -> /data/mpcrit1/mplogs/2020/APR0620/oflsa

    There is no obvious reason to do this but there you go.
    """
    mp_dir = Path(ska_path()) / 'data' / 'mpcrit1' / 'mplogs'

    # Oddly, mp_dir.glob('????/???????/ofls') does not return anything, so we
    # need mp_dir.glob('????/???????/ofls*') and then filter results.
    ofls_links = mp_dir.glob('????/???????/ofls*')
    for ofls_link in ofls_links:
        if ofls_link.name != 'ofls':
            continue
        link = os.readlink(ofls_link)
        if link.startswith('/data'):
            link = Path(link)
            print(f'Linking {ofls_link} -> {link.name}')
            ofls_link.unlink()
            ofls_link.symlink_to(link.name)


def main():
    opt = get_opt()
    if opt.install:
        install(opt)
        return

    if opt.fix_mp_links:
        fix_mp_links()
        return

    config_path = SKA_CONFIG_PATH or PACKAGE_CONFIG_PATH
    config = yaml.safe_load(open(config_path, 'r'))
    print('Loaded config from {}'.format(config_path))

    # Remote user name
    user = opt.user or config.get('user') or getpass.getuser()

    file_sync(config['file_sync'], user, config['host'], opt.sync_mp)


if __name__ == '__main__':
    main()
