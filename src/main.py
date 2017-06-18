import os
from helpers.dataselection import DataReader
from helpers.helperfunctions import *

def main():
    # an example setup. Converts xml files and extracts labels to labelsfile
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
