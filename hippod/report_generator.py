import os
import pypandoc
import shutil
import markdown
import tempfile
import datetime
import json
import re
import tempfile
import logging

import hippod.api_shared
import hippod.error_object

log = logging.getLogger()


class ReportGenerator(object):
    LAST_ACHIEVEMENTS = 1
    FILTER_BY_ANCHOR = 2
    PDF = 3

    @staticmethod
    def generate(app, outputs, report_filter):
        reports_path = app['REPORT_PATH']
        tmp_path = os.path.join(app['DB_ROOT_PATH'], 'tmp')
        if not os.path.isdir(tmp_path):
            os.mkdir(tmp_path)
        list_of_lists = ReportGenerator.ReportGeneratorCollector.search(app, report_filter)
        date = str(datetime.datetime.now().replace(second=0, microsecond=0))
        doc_name = '{}-report.pdf'.format(date)
        pdf_out_path = os.path.join(reports_path, doc_name)
        rpd = ReportGenerator.ReportGeneratorDocument(list_of_lists, tmp_path)
        converted_data = rpd.convert(app)
        rpd.generate_pdf(app, pdf_out_path, converted_data)


    class ReportGeneratorDocument(object):
        def __init__(self, list_of_lists, tmp_path):
            self.list_of_lists = list_of_lists
            # self.tmp_path = tempfile.TemporaryFile()
            self.tmp_path = tmp_path


        # def __del__(self):
        #     shutil.rmtree(self.tmp_path)


        def store_data(app, data, sub_dir):
            src_path = os.path.join(app['DB_DATA_PATH'], data['data-id'], 'blob.bin')
            if not os.path.isdir(sub_dir):
                os.mkdir(sub_dir)
            if 'type' not in data:
                head, tail = os.path.split(data['name'])
                name, data_type = os.path.splitext(tail)
                if data_type == '.png':
                    dst_path = os.path.join(sub_dir, '{}.png'.format(name))
                elif data_type == '.pcap':
                    dst_path = os.path.join(sub_dir, 'trace.pcap')
                else:
                    # FIXME: not sure, but this function should return. If
                    # not dst_path is undefined and will definitly crash some
                    # lines later!
                    log.error("data type not supported: {}".format(data_type))

                with open(src_path, 'rb') as file:
                    data = file.read()
                    #data = zlib.decompress(data)
                    data += b'==='                                              # arrange that correctly!
                    decoded = hippod.hasher.decode_base64_data(data)
                with open(dst_path, 'wb') as file:
                    file.write(decoded)
                with open(dst_path, 'wb') as dst:
                    shutil.copyfile(src_path, dst_path)

            else:
                dst_path = os.path.join(sub_dir, 'description.md')
                with open(dst_path, 'wb') as dst:
                    shutil.copyfile(src_path, dst_path)
            return dst_path


        def add_data(description_path, file_path):
            with open(description_path, 'r') as text:
                description = text.read()
            with open(description_path, 'w') as text:
                description = str(description) + '\n' + '![image caption here]({})'.format(file_path)
                text.write(description)


        def sanitize_description(description_path):
            with open(description_path, 'r') as input_text:
                in_descr = input_text.readlines()
            with open(description_path, 'w') as output_text:
                for line in in_descr:
                    match = re.search(r'^#[#]*', line)
                    p = re.compile(r'(#[#]*)')
                    if match != None:
                        newline = p.sub('{}#'.format(match.group(0)), line)
                        output_text.write(newline)
                    else:
                        output_text.write(line)


        def check_image_reference(description_path, attach_path):
            reference_avaible = False
            head, tail = os.path.split(attach_path)
            with open(description_path, 'r') as input_text:
                in_descr = input_text.readlines()
            with open(description_path, 'w') as output_text:
                for line in in_descr:
                    match = re.search(r'(\()(.*[.]png)', line)       # jpeg,...  # enough to assume there's a reference?
                    p = re.compile(r'\(.*[.]png')
                    if match != None:
                        if match.group(2) == tail:
                            reference_avaible = True
                            newline = p.sub('({}'.format(attach_path), line)
                            output_text.write(newline)
                        else:
                            output_text.write(line)
                    else:
                        output_text.write(line)
            return reference_avaible


        def convert(self, app):
            db_path = app['DB_OBJECT_PATH']
            files_catalog = dict()
            for j, item in enumerate(self.list_of_lists):
                sub_dir = os.path.join(self.tmp_path, 'item{}'.format(j))
                files_catalog[sub_dir] = list()
                # FIXME item[0][0:2], and item[?] is a little bit hacky,
                # save these in extra variables and name then accordingly:
                # WHAT IS THE CONTENT OF THESE? item[0] can means all/nothing
                subcontainer = os.path.join(db_path, item[0][0:2], item[0], item[1], 'subcontainer.db')
                achievement = os.path.join(db_path, item[0][0:2], item[0], item[1], 'achievements', '{}.db'.format(item[2]))
                with open(subcontainer, 'r') as subc:
                    content = json.load(subc)
                data_list = content['object-item']['data']
                for i, data in enumerate(data_list):
                    # FIXME: the next line should be splitted into several
                    # lines to make clear what happens here. The line is
                    # doing tooo much. Split into several lines and save intermediate
                    # results in local variables and name the variables accoringly
                    files_catalog[sub_dir].append(ReportGenerator.ReportGeneratorDocument.store_data(app, data, sub_dir))
            return files_catalog

        def _pandoc_generate(self, app, markdown_in_path, pdf_out_path):
            assert(os.path.isfile(markdown_in_path))
            cmd  = "pandoc "
            cmd += "--latex-engine xelatex "
            if "REPORT-PDF-TEMPLATE" in app:
                cmd += "--template {} ".format(app["REPORT-PDF-TEMPLATE"])
            cmd += "--listings "
            cmd += "--toc "
            cmd += "{} ".format(markdown_in_path)
            cmd += " -o \"{}\" ".format(pdf_out_path)
            log.debug("executing: \"{}\"".format(cmd))
            os.system(cmd)


        def generate_pdf(self, app, pdf_out_path, converted_data):
            sub_reports = list()
            for key, item in converted_data.items():
                for d in item:
                    name, data_type = os.path.splitext(d)
                    if data_type == '.md':
                        ReportGenerator.ReportGeneratorDocument.sanitize_description(d)
                        description_path = d
                    else:
                        continue
                for d in item:
                    name, data_type = os.path.splitext(d)
                    if data_type == '.png':                                 # what about other formats?
                        attach_path = d
                    else: continue
                    ok = ReportGenerator.ReportGeneratorDocument.check_image_reference(description_path, attach_path)
                    if not ok:
                        ReportGenerator.ReportGeneratorDocument.add_data(description_path, attach_path)
                sub_reports.append(description_path)
            for i in range(len(sub_reports) - 1):
                    with open(sub_reports[i+1], 'r') as text2:
                        description2 = text2.read()
                    with open(sub_reports[0], 'r') as text1:
                        description1 = text1.read()
                        description1 = str(description1) + '\n \n \n' + str(description2)
                    with open(sub_reports[0], 'w') as text1:
                        text1.write(description1)
            # FIXME, need arguments
            self._pandoc_generate(app, sub_reports[0], pdf_out_path)





    class ReportGeneratorCollector(object):         # filter at first simply 'ALL_ACHIEVEMENTS_LAST'

        @staticmethod
        def null_func(data):
            pass

        @staticmethod
        def search(app, filter):
            object_index_data = hippod.api_shared.object_index_read(app)
            if not object_index_data:
                return None
            # maybe specify limit in filter?
            search_list = list()
            # list_sort_func = (null_func(), reversed)[bool(True)]          # here variable reversed instead of hardcoded True
            # for cont in list_sort_func(object_index_data):
            for cont in object_index_data:
                ok, cont_obj = hippod.api_shared.read_cont_obj_by_id(app, cont['object-item-id'])
                if not ok:
                    pass # what if? ---> no raise ApiError possible
                # if filter == 'ReportGenerator.LAST_ACHIEVEMENTS':
                if filter == ReportGenerator.LAST_ACHIEVEMENTS:
                    search_list.append(ReportGenerator.ReportGeneratorCollector.search_last_achievements(app, cont['object-item-id'], cont_obj))
            return search_list


        @staticmethod
        def search_last_achievements(app, sha_major, cont_obj):
            ret_list = list()
            buff_dict = dict()
            # fetch latest subcontainer (subcontainer with latest achievement) and related meta
            for sub_cont in cont_obj['subcontainer-list']:
                sc = sub_cont['sha-minor']
                ok, full_sub_cont = hippod.api_shared.read_subcont_obj_by_id(app, sha_major, sc)
                if not ok:
                    pass # what if? ---> no raise ApiError possible
                data = hippod.api_object_get_full.get_all_achievement_data(app, sha_major, sc, full_sub_cont)
                if data:
                    buff_dict[sc] = data[0]['date-added']
            if data:
                latest_sha_minor = max(buff_dict, key=lambda key: buff_dict[key])
                latest_index = next(index for (index,d) in enumerate(cont_obj['subcontainer-list']) if d['sha-minor'] == latest_sha_minor)

            ret_list.append(sha_major)

            if not data:
                sub_cont_last = cont_obj['subcontainer-list'][0]
                latest_sha_minor = sub_cont_last['sha-minor']
            else:
                sub_cont_last = cont_obj['subcontainer-list'][latest_index]
            ret_list.append(sub_cont_last['sha-minor'])

            db_root_path = app['DB_OBJECT_PATH']
            subcntr_path = os.path.join(db_root_path, sha_major[0:2], sha_major,\
                                        latest_sha_minor, 'subcontainer.db')
            with open(subcntr_path) as file:
                full_sub_cont_last = json.load(file)

            data = hippod.api_object_get_detail.get_last_achievement_data(app, sha_major, latest_sha_minor, full_sub_cont_last)
            ret_list.append(data['id'])
            return ret_list
