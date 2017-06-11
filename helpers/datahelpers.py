import os
import sys
import math
from collections import defaultdict
from nltk.tokenize import RegexpTokenizer
from xml.etree import ElementTree
from shutil import copyfile


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
        print('Found {0} files which contained string {1}'.format(len(result), string_query))
        self.set_file_paths(result)

    def select_random(self, amount):
        result = []
        original_file_paths = self.get_file_paths()
        original_amount = len(original_file_paths)
        if amount > original_amount:
            return
        intervals = math.floor(original_amount % amount)
        for i in range(original_amount):
            if i % intervals == 0:
                result.append(original_file_paths[i])
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


class DataTransformer:

    def __init__(self, file_paths, outdir):
        self.file_paths = file_paths
        self.outdir = outdir

    def transform(self):
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        for file_path in self.file_paths:
            destination = os.path.join(self.outdir, os.path.basename(file_path))
            copyfile(file_path, destination)

    def get_file_paths(self):
        return self.file_paths


class DataTransformerXMLToText(DataTransformer):

    def transform(self):
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        xmldr = XMLDataReader()
        xmldr.set_file_paths(self.file_paths)
        xml_files = xmldr.parse_as_xml()
        text_files = self.select_text_from_tag(xml_files, '{http://www.rechtspraak.nl/schema/rechtspraak-1.0}uitspraak')
        for path, text in text_files.items():
            destination = os.path.join(self.outdir, os.path.basename(path))
            outfile = open(destination, 'w', encoding="utf8")
            outfile.write(text)
            outfile.close()

    def select_text_from_tag(self, xml_files, tag):
        text_files = {}
        for name, tree in xml_files.items():
            remove_ext = os.path.splitext(name)[0]
            name = remove_ext + '.txt'
            text_files[name] = ''
            roottag = tree.find(tag)
            if roottag:
                for child in roottag.iter():
                    if child.text:
                        line = child.text.strip()
                        if len(line) > 0:
                            if line[0] in ['•', '*', '-']:
                                text_files[name] += line[1:] + '\n'
                            else:
                                text_files[name] += line + '\n'
        return text_files


def extract_articles(dr, outfile):
    labeldict = defaultdict(set)
    tokenizer = RegexpTokenizer(r'\w+')
    for fname in dr.get_file_paths():
        filehandle = open(fname, 'r', encoding="utf8")
        for line in filehandle.readlines():
            line = line.lower()
            if 'wetboek van strafrecht' in line:
                splitted = line.split('wetboek van strafrecht')
                tokens = tokenizer.tokenize(splitted[0])
                for token in tokens:
                    if len(token) > 3:
                        continue
                    if token.isdigit():
                        labeldict[fname].add(int(token))
                        continue
                    if token[:-1].isdigit():
                        labeldict[fname].add(int(token[:-1]))
                        continue

    for key, item in labeldict.items():
        filename = os.path.basename(key)
        string = filename + '\t' + ','.join(str(v) for v in item if v > 91) + '\n'
        outfile.write(string)


def main(datadir, outdir):
    dr = DataReader(datadir)
    dr.set_file_paths(dr.find_file_paths())

    outfile = open('labels.csv', 'w')
    extract_articles(dr, outfile)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        print("Wrong input format. Use python helpers/datahelpers.py <DATADIR> <OUTPUTDIR>")

