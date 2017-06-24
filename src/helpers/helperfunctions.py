import os
import sys
from dataselection import *
from datatransformation import *
from collections import defaultdict
from nltk.tokenize import RegexpTokenizer


def remove_unlabelled_files(labeldict, datadir):
    dr = DataReader(datadir)
    dr.set_file_paths(dr.find_file_paths())

    for file_path in dr.get_file_paths():
        abs_file_path = os.path.abspath(file_path)
        if not abs_file_path in labeldict:
            os.remove(file_path)


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


def write_labelfile(labeldict, outfile):
    for key, item in labeldict.items():
        filename = os.path.basename(key)
        string = filename + '\t' + ','.join(str(v) for v in item if v > 91) + '\n'
        outfile.write(string)
    outfile.close()


def main(datadir):
    # an example setup. Converts xml files and extracts labels to labelfile
    datadir = os.path.abspath(datadir)
    outdir = os.path.abspath('data/txt')
    select_and_convert_rawdata(datadir, outdir)

    labelfile = os.path.abspath('data/labelfile.csv')
    outfile = open(labelfile, 'w')
    dr = DataReader(outdir)
    dr.set_file_paths(dr.find_file_paths())
    labeldict = extract_labels(dr)

    countlabels = defaultdict(int)
    validdict1 = {}
    # first remove wrong numbers
    for key, item in labeldict.items():
        validlabels = [v for v in item if 91 < v < 424]
        if validlabels:
            validdict1[key] = validlabels
        for label in validlabels:
            countlabels[label] += 1

    validdict2 = {}
    # second remove uncommon numbers
    for key, item in labeldict.items():
        validlabels = [v for v in item if countlabels[v] > 19]
        if validlabels:
            validdict2[key] = validlabels

    remove_unlabelled_files(validdict2, outdir)
    write_labelfile(validdict2, outfile)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])

