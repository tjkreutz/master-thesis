import os
from random import shuffle
from xml.etree import ElementTree


class DataReader:

    def __init__(self, datadir=''):
        self.datadir = datadir
        self.file_paths = []

    def find_file_paths(self):
        file_paths = []
        for filename in os.listdir(self.datadir):
            file_path = os.path.join(self.datadir, filename)
            file_paths.append(file_path)
        print('Found {0} files'.format(len(file_paths)))
        return file_paths

    def set_file_paths(self, file_paths):
        self.file_paths = file_paths

    def get_file_paths(self):
        return self.file_paths


class XMLDataReader(DataReader):

    def find_file_paths(self):
        file_paths = []
        for filename in os.listdir(self.datadir):
            if filename.endswith(".xml"):
                file_path = os.path.join(self.datadir, filename)
                file_paths.append(file_path)
        print('Found {0} xml files'.format(len(file_paths)))
        return file_paths

    def parse_as_xml(self):
        parsed_xml_files = {}
        for file_path in self.get_file_paths():
            parsed_xml_file = ElementTree.parse(file_path)
            parsed_xml_files[file_path] = parsed_xml_file
        return parsed_xml_files


class DataSelector(DataReader):

    def query_file_path(self, name_query, name_index):
        result = []
        for file_name in self.get_file_paths():
            splitted = file_name.split("_")
            if name_query in splitted[name_index]:
                result.append(file_name)
        print('Found {0} files with {1} in name segment {2}'.format(len(result), name_query, name_index))
        self.set_file_paths(result)

    def query_string(self, string_query):
        result = []
        for file_name in self.get_file_paths():
            file_handle = open(file_name, 'r', encoding="utf8")
            if string_query.lower() in file_handle.read().lower():
                result.append(file_name)
                file_handle.close()
                continue
        print('Found {0} files which contained string {1}'.format(len(result), string_query))
        self.set_file_paths(result)

    def select_random(self, amount):
        original_file_paths = self.get_file_paths()
        original_amount = len(original_file_paths)
        if amount > original_amount:
            return
        shuffle(original_file_paths)
        result = original_file_paths[:amount]
        self.set_file_paths(result)


class XMLDataSelector(XMLDataReader, DataSelector):

    def query_xml_tag(self, tag, value, exact=True):
        result = []
        for name, tree in self.parse_as_xml():
            for child in tree.iter(tag):
                if exact:
                    if child.text == value:
                        result.append(name)
                else:
                    if value in child.text:
                        result.append(name)
        print('Found {0} xml files with tag value pair {1} {2}'.format(len(result), tag, value))
        self.set_file_paths(result)

