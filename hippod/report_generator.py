import os
import pypandoc
import shutil
import markdown
import tempfile

class ReportGenerator:

    class ReportGeneratorDocument:
        def __init__(self, output_type, output_name):
            self.type = output_type
            self.name = output_name

        def add_data(self, description_path, file_path):
            with open(description_path, 'r') as text:
                description = text.read()
            with open(description_path, 'w') as text:
                description = str(description) + '\n' + '![image caption here]({})'.format(file_path)
                text.write(description)

        def convert(self, file_path):
            output = pypandoc.convert_file(file_path, self.type, outputfile=self.name)  # convert from file or from text/string?
            # output = pypandox.convert_text()



    class ReportGeneratorCollector:         # filter at first simply 'ALL_ACHIEVEMENTS_LAST'

        def __init__(self, store_root, store_dir):
            self.store_root = store_root
            self.store_dir = store_dir
            self._init_store()


        def _init_store(self):
            if not os.path.isdir(self.store_root):
                os.mkdir(self.store_root)           # here make tmp file
            if not os.path.isdir(self.store_dir):
                os.mkdir(self.store_dir)            # here make tmp file or only for root tmp?
            


        def store_file(self, src_path, dst_path):
            with open(dst_path, 'wb') as dst:
                shutil.copyfile(src_path, dst_path)
                return dst_path