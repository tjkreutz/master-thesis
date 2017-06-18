from .dataselection import *
from .datatransformation import *
from collections import defaultdict
from nltk.tokenize import RegexpTokenizer


def extract_labels(dr, outfile):
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
        validlabels = [str(v) for v in item if 91 < v < 424]
        if validlabels:
            filename = os.path.basename(key)
            string = filename + '\t' + ','.join(str(v) for v in item if v > 91) + '\n'
            outfile.write(string)


def select_and_convert_rawdata(datadir, outdir):

    xds = XMLDataSelector(datadir)
    xds.set_file_paths(xds.find_file_paths())
    xds.query_file_path('RB', 2)
    xds.query_string('http://psi.rechtspraak.nl/rechtsgebied#strafRecht') #zorg dat het strafrecht is
    xds.query_string('http://psi.rechtspraak.nl/procedure#eersteAanleg') #zorg dat het eerste aanleg is

    dtxt = DataTransformerXMLToText(xds.get_file_paths(), outdir)
    dtxt.transform_and_output()


def main():
    # an example setup. Converts xml files and extracts labels to labelfile
    datadir = os.path.abspath('data/xml')
    outdir = os.path.abspath('data/txt')
    select_and_convert_rawdata(datadir, outdir)

    labelfile = os.path.abspath('data/labelfile.csv')
    outfile = open(labelfile, 'w')
    dr = DataReader(outdir)
    dr.set_file_paths(dr.find_file_paths())
    extract_labels(dr, outfile)


if __name__ == '__main__':
    main()

