#!/bin/env python3
# coding=utf-8
"""
This script convert version string from year.month into yearmonth.spversion(22.03sp1->2203.1)
from openeuler repo, Which is used as WSL app major version
"""

import re
import sys

import requests

def get_sp_version(rel: str) -> str:
    """
    Get the release version info from repo
    And convert
    """
    headers = {"Content-type": "application/json",
               "User-Agent": "Python"}

    resp = requests.get("https://repo.openeuler.org/", headers=headers, timeout=60)
    if resp.status_code != 200:
        sys.exit(1)

    res = re.compile(f'openEuler-{rel}(-LTS)?(-SP([0-9]))?')

    ver = re.findall(res, resp.text)[-1][2]

    return ver if ver else '0'


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'{sys.argv[0]} <release>')
        sys.exit(1)
    RELEASE = sys.argv[1]
    RELEASE = RELEASE.replace('.', '')
    print(RELEASE + '.' + get_sp_version(sys.argv[1]))
