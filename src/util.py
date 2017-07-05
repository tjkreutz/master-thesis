import os
from helpers.dataselection import DataReader, XMLDataSelector
from helpers.datatransformation import DataNormalizer, DataTransformerXMLToText
from collections import defaultdict
from nltk.tokenize import RegexpTokenizer


def extract_labels(dr):
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
    return labeldict


def select_and_convert_rawdata(datadir, outdir):

    xds = XMLDataSelector(datadir)
    xds.set_file_paths(xds.find_file_paths())
    xds.query_file_path('RB', 2)
    xds.query_string('http://psi.rechtspraak.nl/rechtsgebied#strafRecht') #zorg dat het strafrecht is
    xds.query_string('http://psi.rechtspraak.nl/procedure#eersteAanleg') #zorg dat het eerste aanleg is

    dtxtt = DataTransformerXMLToText(xds.get_file_paths(), outdir)
    dtxtt.transform_and_output()


def read_labelfile(labelfile):
    labeldict = {}
    for line in labelfile.readlines():
        splitted = line.split('\t')
        key = splitted[0]
        item = splitted[1].rstrip().split(',')
        labeldict[key] = item
    return labeldict


def write_labelfile(labeldict, outfile):
    for key, item in labeldict.items():
        filename = os.path.basename(key)
        string = filename + '\t' + ','.join(str(v) for v in item if v > 91) + '\n'
        outfile.write(string)
    outfile.close()

