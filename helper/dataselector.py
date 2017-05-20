import os
import math
from shutil import copyfile
from xml.etree import ElementTree

BASEDIR = ''
DATADIRS = [BASEDIR + '']
OUTPUTFILE = BASEDIR + ''


class DataSelector:

    def __init__(self, datadirs):
        self.datadirs = datadirs
        self.file_paths = self.find_file_paths()

    def find_file_paths(self):
        file_paths = []
        for datadir in self.datadirs:
            for filename in os.listdir(datadir):
                if filename.endswith(".xml"):
                    file_path = os.path.join(datadir, filename)
                    file_paths.append(file_path)
        print('Found {0} xml files'.format(len(file_paths)))
        return file_paths

    def query_xml_tag(self, tag, value, exact=True):
        result = []
        for file_path in self.get_file_paths():
            parsed_xml_file = ElementTree.parse(file_path)
            for child in parsed_xml_file.iter(tag):
                if exact:
                    if child.text == value:
                        result.append(file_path)
                else:
                    if value in child.text:
                        result.append(file_path)
        print('Found {0} xml files with tag value pair {1} {2}'.format(len(result), tag, value))
        self.set_file_paths(result)

    def query_file_path(self, name_query, name_index):
        result = []
        for file_name in self.get_file_paths():
            splitted = file_name.split("_")
            if name_query in splitted[name_index]:
                result.append(file_name)
        print('Found {0} xml files with {1} in name segment {2}'.format(len(result), name_query, name_index))
        self.set_file_paths(result)

    def query_string(self, string_query):
        result = []
        for file_name in self.get_file_paths():
            file_handle = open(file_name, 'r', encoding="utf8")
            if string_query in file_handle.read():
                result.append(file_name)
            file_handle.close()
        print('Found {0} xml files which contained string {1}'.format(len(result), string_query))
        self.set_file_paths(result)

    def set_file_paths(self, file_paths):
        self.file_paths = file_paths

    def get_file_paths(self):
        return self.file_paths

    def select_random(self, amount):
        result = []
        original_file_paths = self.get_file_paths()
        original_amount = len(original_file_paths)
        if amount > original_amount:
            return
        intervals = math.floor(original_amount/amount)
        for i in range(original_amount):
            if i%intervals == 0:
                result.append(original_file_paths[i])
        self.set_file_paths(result)


def main():

    ds = DataSelector(DATADIRS)
    ds.select_random(10)

    for file_path in ds.get_file_paths():
        copyfile(file_path, OUTPUTFILE+os.path.basename(file_path))

main()