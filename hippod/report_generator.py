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
            # check whether data is a image or description
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

        def store_achievement(app, data, sub_dir):
            if not os.path.isdir(sub_dir):
                os.mkdir(sub_dir)
            # check whether data is achievement like
            if 'result' in data:
                dst_path = os.path.join(sub_dir, 'achievement.db')
                with open(dst_path, 'w') as dst:
                    data = json.dumps(data, sort_keys=True,indent=4,
                      separators=(',', ': '))
                    dst.write(data)
                return dst_path
            else:
                return None


        def add_data(description_path, file_path):
            with open(description_path, 'r') as text:
                description = text.read()
            with open(description_path, 'w') as text:
                description = str(description) + '\n' + '![image caption here]({})'.format(file_path)
                text.write(description)

        def add_achievement(description_path, achievement_path, title):
            if description_path == None:
                # remove '/achievement.db' of the path and create a 'description.md' file in this directory
                tmp_item_path = os.path.dirname(achievement_path)
                description_path = os.path.join(tmp_item_path, 'description.md')
                with open(achievement_path, 'r') as achievement:
                    content = json.load(achievement)
                    result = content['result']
                with open(description_path, 'w') as text:
                    description = '''
# {} #

-----------------------------------------------------------------------------------
**Test result:**    {}

-----------------------------------------------------------------------------------

                    '''.format(title, result)
                    text.write(description)
                return description_path
            else:
                with open(achievement_path, 'r') as achievement:
                    content = json.load(achievement)
                    result = content['result']
                with open(description_path, 'r') as text:
                    description = text.read()
                with open(description_path, 'w') as text:
                    description = '''
# {} #

-----------------------------------------------------------------------------------
**Test result:**    {}

-----------------------------------------------------------------------------------

                    '''.format(title, result) +\
                    '\n' + str(description)
                    text.write(description)
                    return description_path


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
                files_catalog[sub_dir] = dict()
                files_catalog[sub_dir]['data'] = list()
                sha_major = item[0]
                sha_minor = item[1]
                achievement_id = item[2]
                title = item[3]
                files_catalog[sub_dir]['title'] = title
                subcontainer = os.path.join(db_path, sha_major[0:2], sha_major, sha_minor, 'subcontainer.db')
                achievement = os.path.join(db_path, sha_major[0:2], sha_major, sha_minor, 'achievements', '{}.db'.format(achievement_id))
                with open(achievement, 'r') as achiev:
                    content = json.load(achiev)
                stored_data_path = ReportGenerator.ReportGeneratorDocument.store_achievement(app, content, sub_dir)
                files_catalog[sub_dir]['achievement'] = stored_data_path
                with open(subcontainer, 'r') as subc:
                    content = json.load(subc)
                if 'data' not in content['object-item']:
                    continue
                data_list = content['object-item']['data']
                for i, data in enumerate(data_list):
                    stored_data_path = ReportGenerator.ReportGeneratorDocument.store_data(app, data, sub_dir)
                    files_catalog[sub_dir]['data'].append(stored_data_path)
            print('here files catalog {}'.format(files_catalog))
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
                title = item['title']
                counter = 0
                for d in item['data']:
                    counter += 1
                    name, data_type = os.path.splitext(d)
                    if data_type == '.md':
                        ReportGenerator.ReportGeneratorDocument.sanitize_description(d)
                        description_path = d
                        if 'achievement' in item:
                            achievement_path = item['achievement']
                            ReportGenerator.ReportGeneratorDocument.add_achievement(description_path, achievement_path, title)
                        counter = 0
                    # if no '.md' found --> use at least title and test result for the report
                    elif counter == len(item['data']):
                        if 'achievement' in item:
                            achievement_path = item['achievement']
                            description_path = ReportGenerator.ReportGeneratorDocument.add_achievement(None, achievement_path, title)
                    else:
                        continue
                for d in item['data']:
                    name, data_type = os.path.splitext(d)
                    if data_type == '.png':                                 # what about other formats?
                        attach_path = d
                    else:
                        continue
                    ok = ReportGenerator.ReportGeneratorDocument.check_image_reference(description_path, attach_path)
                    if not ok:
                        ReportGenerator.ReportGeneratorDocument.add_data(description_path, attach_path)
                if len(item['data']) == 0:
                    achievement_path = item['achievement']
                    description_path = ReportGenerator.ReportGeneratorDocument.add_achievement(None, achievement_path, title)
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
            shutil.rmtree(self.tmp_path)





    class ReportGeneratorCollector(object):

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
                    continue # what if? ---> no raise ApiError possible
                title = cont_obj['title']
                if filter == ReportGenerator.LAST_ACHIEVEMENTS:
                    last_achiev_list = ReportGenerator.ReportGeneratorCollector.search_last_achievements(app, cont['object-item-id'], cont_obj)
                    last_achiev_list.append(title)
                    search_list.append(last_achiev_list)
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
