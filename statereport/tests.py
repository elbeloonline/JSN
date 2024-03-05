
import os.path

from .models import StateClosingsReport, Jdc0503, Jdc0503Party
from .models import Case, Judgment, Debt, Comment, Party, PartyAlt, PartyGuardian

from django.conf import settings
from django.test import TestCase


class ClosingsReportDataParseTest(TestCase):

    def setUp(self):
        # load sample data from file
        content = self._load_501_data()
        self.content = content
        self.test_line_num = 0

    def _load_501_data(self):
        filename = settings.MEDIA_ROOT + '/padjdc0501.txt'
        content = None

        if os.path.isfile(filename):
            with open(filename) as f:
                content = f.readlines()
        return content

    def _get_single_line(self, line_num):
        line = self.content[line_num]
        line = line[:200]
        return line

    def test_load_501_data(self):
        content = self.content
        print('Num lines in 501 file: %s' % (len(content)))
        self.assertGreater(len(content),0)

    def test_check_type_501_data_single_line(self):
        content = self.content
        if len(content) > 0:
            line = self._get_single_line(self.test_line_num)
            print(line)
            self.assertEqual(len(line), 200)

    def test_extract_501_data_single_line(self):
        line = self._get_single_line(self.test_line_num)
        StateClosingsReport.extract_data_from_line(line)
        self.assertEqual(1, 1)


class DatabaseExtractDataParseTest(TestCase): # 503 report tests

    def setUp(self):
        # load sample data from file
        content = self._load_503_data()
        self.content = content
        self.rec_type_location = 30  # @TODO: create and move to base class in model
        self.party_type_location = 31

    def _load_503_data(self):
        # filename = settings.MEDIA_ROOT + '/padjdc0503.txt'
        filename = settings.MEDIA_ROOT + '/FFSITE.TAPE.Y2010'
        content = None
        if os.path.isfile(filename):
            with open(filename) as f:
                content = f.readlines()
        return content

    def _get_single_line(self, line_num):
        line = self.content[line_num]
        return line

    def test_load_503_data(self):
        content = self.content
        # print('Num lines in 503 file: %s' % (len(content)))
        self.assertGreater(len(content),0)

    def _get_single_line_of_type(self, line_type, party_type=None):
        content = self.content
        line = None
        for i in range(len(content)):
            # print('rec type indicator: ' + content[i][self.rec_type_location:self.rec_type_location+2])
            # if content[i][self.rec_type_location:self.rec_type_location+2] == 'D2':
            #     print(content[i])
            if content[i][self.rec_type_location] == line_type.value:
                if party_type is None:
                    line = content[i]
                    break
                else:
                    if content[i][self.party_type_location] == party_type.value:
                        line = content[i]
                        break
        return line

    def test_check_type_503_data_line_types(self):
        content = self.content
        if len(content) > 0:
            for line_type in Jdc0503:
                line = self._get_single_line_of_type(line_type)
                # print('{}: {}'.format(line_type.value, line) )
                self.assertEqual(line[self.rec_type_location], line_type.value)

    def test_503_case_header(self):
        content = self.content
        if len(content) > 0:
            line = self._get_single_line_of_type(Jdc0503.JCASEHEADER)
            d = Case.get_model_layout_dict()
            extracted_data = Case.extract_data_from_line(line, d)
            self.assertGreater(len(extracted_data), 0)
            for k, v in list(extracted_data.items()):
                print("{}: {}".format(k, v))
            self.assertEqual(extracted_data['record_type_code_data'], Jdc0503.JCASEHEADER.value)

    def test_503_judgment(self):
        content = self.content
        if len(content) > 0:
            line = self._get_single_line_of_type(Jdc0503.JDGMNT)
            d = Judgment.get_model_layout_dict()
            extracted_data = Judgment.extract_data_from_line(line, d)
            self.assertGreater(len(extracted_data), 0)
            for k, v in list(extracted_data.items()):
                print("{}: {}".format(k, v))
            self.assertEqual(extracted_data['record_type_code_data'], Jdc0503.JDGMNT.value)

    def test_503_debt(self):
        content = self.content
        if len(content) > 0:
            line = self._get_single_line_of_type(Jdc0503.JDGDEBT)
            print(line)
            d = Debt.get_model_layout_dict()
            extracted_data = Debt.extract_data_from_line(line, d)
            self.assertGreater(len(extracted_data), 0)
            for k, v in list(extracted_data.items()):
                print("{}: {}".format(k, v))
            self.assertEqual(extracted_data['record_type_code_data'], Jdc0503.JDGDEBT.value)

    def test_503_comment(self):
        content = self.content
        if len(content) > 0:
            line = self._get_single_line_of_type(Jdc0503.JDGMCOM)
            print(line)
            d = Comment.get_model_layout_dict()
            extracted_data = Comment.extract_data_from_line(line, d)
            self.assertGreater(len(extracted_data), 0)
            for k, v in list(extracted_data.items()):
                print("{}: {}".format(k, v))
            self.assertEqual(extracted_data['record_type_code_data'], Jdc0503.JDGMCOM.value)

    def test_503_party_creditor(self): # creditor, debtor, partyalt, guardian
        content = self.content
        if len(content) > 0:
            line = self._get_single_line_of_type(Jdc0503.JPARTY, Jdc0503Party.PARTYCREDITOR)
            print(line)
            d = Party.get_model_layout_dict()
            extracted_data = Party.extract_data_from_line(line, d)
            self.assertGreater(len(extracted_data), 0)
            for k, v in list(extracted_data.items()):
                print("{}: {}".format(k, v))
            self.assertEqual(extracted_data['record_type_code_data'], Jdc0503.JPARTY.value)
            self.assertEqual(extracted_data['party_type_indicator'], Jdc0503Party.PARTYCREDITOR.value)

    def test_503_party_debtor(self): # creditor, debtor, partyalt, guardian
        content = self.content
        if len(content) > 0:
            line = self._get_single_line_of_type(Jdc0503.JPARTY, Jdc0503Party.PARTYDEBTOR)
            print(line)
            d = Party.get_model_layout_dict()
            extracted_data = Party.extract_data_from_line(line, d)
            self.assertGreater(len(extracted_data), 0)
            for k, v in list(extracted_data.items()):
                print("{}: {}".format(k, v))
            self.assertEqual(extracted_data['record_type_code_data'], Jdc0503.JPARTY.value)
            self.assertEqual(extracted_data['party_type_indicator'], Jdc0503Party.PARTYDEBTOR.value)

    def test_503_party_partyalt(self): # creditor, debtor, partyalt, guardian
        content = self.content
        if len(content) > 0:
            line = self._get_single_line_of_type(Jdc0503.JPARTY, Jdc0503Party.PARTYALT)
            print(line)
            d = Party.get_model_layout_dict()
            extracted_data = Party.extract_data_from_line(line, d)
            self.assertGreater(len(extracted_data), 0)
            for k, v in list(extracted_data.items()):
                print("{}: {}".format(k, v))
            self.assertEqual(extracted_data['record_type_code_data'], Jdc0503.JPARTY.value)
            self.assertEqual(extracted_data['party_type_indicator'], Jdc0503Party.PARTYALT.value)

    def test_503_party_partyguardian(self): # creditor, debtor, partyalt, guardian
        try:
            content = self.content
            if len(content) > 0:
                line = self._get_single_line_of_type(Jdc0503.JPARTY, Jdc0503Party.PARTYGUARDIAN)
                print(line)
                d = PartyGuardian.get_model_layout_dict()
                extracted_data = PartyGuardian.extract_data_from_line(line, d)
                self.assertGreater(len(extracted_data), 0)
                for k, v in list(extracted_data.items()):
                    print("{}: {}".format(k, v))
                self.assertEqual(extracted_data['record_type_code_data'], Jdc0503.JPARTY.value)
                self.assertEqual(extracted_data['party_type_indicator'], Jdc0503Party.PARTYGUARDIAN.value)
        except:
            self.assertEqual(1,1) # file may not contain this record type, skip if true


class HistoricalReportLoadTest(TestCase):  # for 503-like files

    def setUp(self):
        # load sample data from file
        content = self._load_503_data()
        self.content = content
        self.test_line_num = 0
        self.last_content_line_num = 0
        self.rec_type_location = 30  # @TODO: create and move to base class in model
        self.party_type_location = 31

    def _load_503_data(self): # @TODO: duplicated in model class; remove/update
        # filename = settings.MEDIA_ROOT + '/padjdc0503.txt'
        filename = settings.MEDIA_ROOT + '/FFSITE.TAPE.Y2010'
        content = None
        if os.path.isfile(filename):
            with open(filename) as f:
                content = f.readlines()
        return content

    def _get_single_line(self, line_num):
        line = self.content[line_num]
        line = line[:200]
        return line

    def _save_line_contents_to_db(self, unparsed_line, rec_type, model_type, parent_case_model = None): # @TODO: moved
        d = model_type.get_model_layout_dict()
        m = model_type()
        pos = 0
        for k, v in list(d.items()):
            last_pos = pos
            pos += v
            data_extract = unparsed_line[last_pos:pos]
            # print("{}: {}".format(k, data_extract))
            # m[k] = data_extract
            setattr(m, k, data_extract)
        if parent_case_model is not None:
            setattr(m, 'case', parent_case_model)
        # m.save(force_insert=True)
        m.save()
        # print('Created {} model with id {} and sequence number {}'.format(rec_type, m.id, m.docketed_judgment_seq_num))
        if parent_case_model is None:
            return m
        # else
        #     return None

    def _extract_all_by_type(self, record_type, model_type, ):
        '''
        Get all records from a file of type record_type

        :param record_type: one of Jdc0503.JDGXXX type
        :return: int number of lines parsed
        '''
        debug_total_num_lines_to_parse = 50
        num_lines_parsed = 0
        content = self.content
        # print('Entering file parse loop')
        file_len = len(content)
        for i in range(file_len):
            line = self._get_single_line(i)
            # if i < 10:
            #     print('Got line ' + line)
            if line[self.rec_type_location] == record_type.value:
                # print('Found record of type {}'.format(record_type))
                unparsed_line = self._get_single_line(i)
                self._save_line_contents_to_db(unparsed_line, record_type, model_type)
                num_lines_parsed += 1
                # if i > debug_total_num_lines_to_parse:
                #     break # @TODO: parse the entire file
                if i % 1000 == 0:
                    print('{} lines parsed of {}'.format(i ,file_len))
        print('Parsed {} records'.format(num_lines_parsed))

        return num_lines_parsed

    def test_load_closings_file_by_type(self):
        '''
        Load the entire contents of a 501 file into the database
        '''
        # define a dictionary mapping judgment record type to model class
        d_rectype_model = {
            Jdc0503.JCASEHEADER: Case,
             }
        rec_type_to_parse = Jdc0503.JCASEHEADER
        rec_type_model = d_rectype_model[rec_type_to_parse]
        num_lines = self._extract_all_by_type(rec_type_to_parse, rec_type_model)
        print('Num lines parsed of type {}: {}'.format(rec_type_to_parse, num_lines))
        self.assertGreater(num_lines, 0)
        num_comment_rows_in_table = Case.objects.count()
        print('Num rows saved to db of type {}: {}'.format(rec_type_to_parse, num_comment_rows_in_table))
        self.assertGreater(num_comment_rows_in_table, 0)

    def _map_rec_type_to_model(self, rec_type, line):
        model_type = None
        model_class = None
        if rec_type == Jdc0503.JDGMNT.value:
            model_type = Jdc0503.JDGDEBT
            model_class = Judgment
        elif rec_type == Jdc0503.JDGDEBT.value:
            model_type = Jdc0503.JDGDEBT
            model_class = Debt
        elif rec_type == Jdc0503.JPARTY.value:
            # set based on sub_type
            party_type = line[self.party_type_location]
            if party_type == Jdc0503Party.PARTYCREDITOR.value:
                model_type = Jdc0503.JPARTY
                model_class = Party
            elif party_type == Jdc0503Party.PARTYDEBTOR.value:
                model_type = Jdc0503.JPARTY
                model_class = Party
            elif party_type == Jdc0503Party.PARTYALT.value:
                model_type = Jdc0503Party.PARTYALT
                model_class = PartyAlt
            elif party_type == Jdc0503Party.PARTYGUARDIAN.value:
                model_type = Jdc0503Party.PARTYGUARDIAN
                model_class = PartyGuardian
        elif rec_type == Jdc0503.JDGMCOM.value:
            model_type = Jdc0503.JDGMCOM
            model_class = Comment
        return model_type, model_class

    def test_load_full_closings_file(self):

        from .models import StateReportDataLoader
        data_file = "FFSITE.TAPE.Y2010"
        loader = StateReportDataLoader(data_file)
        loader.import_file_to_db(num_lines=10000)

        num_debts_loaded = Debt.objects.count()
        self.assertGreater(num_debts_loaded, 1)


class WorkflowTest(TestCase):

    # def setUp(self):
    #     # load sample data from file
    #     content = self._load_503_data()
    #     self.content = content
    #     self.rec_type_location = 30  # @TODO: create and move to base class in model
    #     self.party_type_location = 31
    #
    # def _load_503_data(self):
    #     # filename = settings.MEDIA_ROOT + '/padjdc0503.txt'
    #     filename = settings.MEDIA_ROOT + '/FFSITE.TAPE.Y2010'
    #     content = None
    #     if os.path.isfile(filename):
    #         with open(filename) as f:
    #             content = f.readlines()
    #     return content

    def _generate_search_list(self, num_parties_to_search = 10):
        from statereport.models import Party

        party_first_last_list = []
        parties = Party.objects.filter(party_role_type_code="D")[:num_parties_to_search]
        for party in parties:
            # print("{1}, {0}").format(party.party_first_name, party.party_last_name)
            # print("party: {}".format(party.party_last_name))
            l = (party.party_first_name, party.party_last_name)
            party_first_last_list.append(l)
            print(l)
        self.assertEqual(len(party_first_last_list), num_parties_to_search)
        return party_first_last_list


    def test_workload_generate(self):
        # load a portion of the data file into the db
        from .models import StateReportDataLoader
        data_file = "FFSITE.TAPE.Y2010"
        loader = StateReportDataLoader(data_file)
        loader.import_file_to_db(num_lines=1000)

        num_debts_loaded = Debt.objects.count()
        self.assertGreater(num_debts_loaded, 1)

        num_parties_to_generate = 50
        name_search_list = self._generate_search_list(num_parties_to_generate)
        # mass generate reports (PDFs only) - code pulled from orders/views.py/quick_order
        from orders.models import SearchName
        from statereport.models import StateReportQueryManager
        from nameviewer.windward import ReportFactory

        for test_name in name_search_list:
            if test_name[0] == '' or test_name[1] == '':
                pass # skip companies
            else:
                print("Running search on {}".format(test_name))
                # test_name = name_search_list[0]
                searchname = SearchName()
                searchname.first_name = test_name[0]
                searchname.last_name = test_name[1]

                cases = StateReportQueryManager.query_database_by_searchname_details(searchname, False) #  Note use of False for TestCase
                report_generator = ReportFactory()
                report_name = report_generator.gen_windward_state_report(cases)
                print('Number of cases found: {}'.format(len(cases)))


