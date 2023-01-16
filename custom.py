#!/bin/env python3
# coding=utf-8
"""
This script copy all wsl metadata from meta/RELEASE dir
"""
import argparse
import sys
import shutil
import os.path

def init_parser():
    """
    add some args
    """
    new_parser = argparse.ArgumentParser(
        prog='customer.py',
        description='custom some metadata for openEuler WSL project',
    )

    new_parser.add_argument('-r', '--release')
    new_parser.add_argument('-v', '--version')
    return new_parser


custom_arrary = [
    {
        'file': 'DistroLauncher/DistributionInfo.h',
    },
    {
        'file': 'DistroLauncher-Appx/MyDistro.appxmanifest',
    },
    {
        'file': 'DistroLauncher-Appx/DistroLauncher-Appx.vcxproj',
    }
]

version_replace = [
    'DistroLauncher-Appx/MyDistro.appxmanifest',
    'meta.json',
]

if __name__ == '__main__':
    parser = init_parser()
    args = parser.parse_args()
    # print(args.__dict__['release'])
    if not args.release or not args.version:
        parser.print_help()
        sys.exit(1)

    for f in version_replace:
        with open(f"meta/{args.release}/{f}", "r+", encoding='utf-8') as manifest:
            content = manifest.read().replace('1.0.0.0', f'{args.version}.0')
            manifest.seek(0)
            manifest.write(content)

    for c in custom_arrary:
        src = os.path.join('meta', args.release)
        shutil.copy2(os.path.join(src, c['file']), c['file'])
