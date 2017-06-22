import os
from shutil import copyfile
from dataselection import XMLDataReader


class DataTransformer:

    def __init__(self, file_paths, outdir):
        self.file_paths = file_paths
        self.outdir = outdir

    def transform_and_output(self):
        self.transform()
        self.output()

    def transform(self):
        pass

    def output(self):
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        for file_path in self.file_paths:
            destination = os.path.join(self.outdir, os.path.basename(file_path))
            copyfile(file_path, destination)

    def get_file_paths(self):
        return self.file_paths


class DataTransformerXMLToText(DataTransformer):

    def transform_and_output(self):
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
                            text_files[name] += line + '\n'
        return text_files
