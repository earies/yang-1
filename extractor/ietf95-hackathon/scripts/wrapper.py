#!/usr/bin/python

import argparse
import os

parser = argparse.ArgumentParser(
        description='Wrapper script to run analysis on YANG modules')
parser.add_argument('--debug', type=bool, default=False,
        help='Optional: Toggle debugging')
args = parser.parse_args()

def main():
    files = os.listdir('../models')
    for i in files:
        cmd = './extractor.py --src_dir ../models/ --dst_dir ../output/ --yang_type typedef ' + i
        os.popen(cmd).read()
        cmd = './extractor.py --src_dir ../models/ --dst_dir ../output/ --yang_type grouping ' + i
        os.popen(cmd).read()
        cmd = './extractor.py --src_dir ../models/ --dst_dir ../output/ --yang_type identity ' + i
        os.popen(cmd).read()

if __name__ == '__main__':
    main()
