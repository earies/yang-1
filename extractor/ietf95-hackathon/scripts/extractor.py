#!/usr/bin/python

import argparse
import json
import logging
import os

FORMAT = '%(asctime)-15s %(levelname)s %(filename)s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
        description='Extracts the typedef, identity, and grouping from a YANG model')
parser.add_argument('source', type=str,
        help='The URL or filename of the YANG model')
parser.add_argument('--src_dir', default='.', type=str,
        help='Optional: directory where to find the source model')
parser.add_argument('--dst_dir', default='.', type=str,
        help='Optional: directory where to output the extracted data')
parser.add_argument('--yang_type', default='all',
        help='Optional flag that determines what to extract (typedef, identity, grouping)')
args = parser.parse_args()

class YangTypeParser(object):
    def __init__(self, source, src_dir, dst_dir,
            yang_type):
        self.src_dir = src_dir
        self.input_file = os.path.join(src_dir, source)
        self.dst_dir = dst_dir
        self.yang_type = yang_type

    def get_typename(self, yang_type, line):
        name = line.split('{')[0].strip()
        name = name.lstrip(yang_type)
        name = name.lstrip()
        return(name)

    def extract_type(self, yang_type):
        fh = open(self.input_file)
        buf = fh.readlines()
        fh.close()

        start_flag = False
        title_flag = False
        nbrac = 0

        result = {}
        result['types'] = {}

        for line in buf:
            if start_flag is False:
                spos = line.find(yang_type)
                if spos >= 0 and spos < 5:
                    start_flag = True
                    title_flag = True

            if start_flag is True:
                if title_flag is True:
                    type_name = self.get_typename(yang_type, line)
                    if not result['types'].get(type_name):
                        result['types'][type_name] = {}
                    result['types'][type_name]['module'] = os.path.basename(self.input_file)
                    result['types'][type_name]['type'] = yang_type
                    data = []
                    title_flag = False

                data.append(line)

                spos = line.find('{')
                if spos >= 0:
                    nbrac = nbrac + 1

                spos = line.find('}')
                if spos >= 0:
                    nbrac = nbrac - 1

                if nbrac == 0:
                    result['types'][type_name]['data'] = ''.join(data)
                    start_flag = False
        return(result)


    def write_json(self, edata):
        for type_name in edata['types']:
            result = {}
            result['module'] = {}
            yang_type = edata['types'][type_name]['type']
            module = edata['types'][type_name]['module']
            data = edata['types'][type_name]['data']

            result['module'][module] = {}
            result['module'][module][type_name] = {}
            result['module'][module][type_name]['type'] = yang_type
            result['module'][module][type_name]['data'] = data
            output_file = os.path.join(self.dst_dir, yang_type + '-' + type_name + '.json')
            if os.path.exists(output_file):
                logger.warning('file exists: %s (duplicate type: %s)', output_file, type_name)
                fh = open(output_file)
                file_exist = json.loads(fh.read())
                key = file_exist['module'].keys()[0]
                result['module'][key] = file_exist['module'][key]
                fh.close()
            output_json = json.dumps(result, indent=4)
            fh = open(output_file, 'w')
            fh.write(output_json)
            fh.close()


    def extract(self):
        if self.yang_type == 'all':
            for ytype in ['typedef', 'grouping', 'identity']:
                res = self.extract_type(ytype)
                self.write_json(res)
        else:
            res = self.extract_type(self.yang_type)
            self.write_json(res)

def main():
    yp = YangTypeParser(args.source, args.src_dir, args.dst_dir, args.yang_type)
    yp.extract()


if __name__ == '__main__':
    main()
