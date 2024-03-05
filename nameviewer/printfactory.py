import os
import os.path
from xml.etree.ElementTree import Element, Comment, SubElement, tostring

from .utils import SpecCodes
from statereport.models import PartyAlt, PartyGuardian, Party, Debt


class PrintFactory:
    def __init__(self):
        self.top = Element('root', attrib={'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance'})
        self.comment = Comment('Generated for JSN')
        self.top.append(self.comment)

    def _make_float(self, amt, with_money_symbol=True):
        """
        Convert TAPE-format money strings into a human-readable value
        :type amt: string in cobol format read from the original tape drive
        """
        if amt != '':
            d = {}
            d['{'] = 0
            d['A'] = 1
            d['B'] = 2
            d['C'] = 3
            d['D'] = 4
            d['E'] = 5
            d['F'] = 6
            d['G'] = 7
            d['H'] = 8
            d['I'] = 9
            d['}'] = -0
            d['J'] = -1
            d['K'] = -2
            d['L'] = -3
            d['M'] = -4
            d['N'] = -5
            d['O'] = -6
            d['P'] = -7
            d['Q'] = -8
            d['R'] = -9

            fmt_str = '{}.{}'
            # convert low bit
            low_bit = amt[-1]
            pennies_value = d[low_bit]
            if pennies_value < 0:
                fmt_str = ' -' + fmt_str
            pennies_value = abs(pennies_value)
            if with_money_symbol:
                fmt_str = '$' + fmt_str
            fmt_str += str(pennies_value)
            # end convert low bit
            return fmt_str.format(amt[:9].lstrip('0'), amt[9])
        else:
            return amt

    def _make_american_date(self, dt):
        """
        Make dates appear as MM/DD/YY
        :param dt: a date pulled from the database
        :return: a formatted string
        """
        year = dt[2:4]
        month = dt[4:6]
        day = dt[6:]
        return_date = '{}/{}/{}'.format(month, day, year)
        if return_date == '00/00/00':
            return_date = ''
        return return_date

    def _make_case_xml(self, case_instance, order, searchname):
        """
        Build case-related XML elements for this class instance
        :param case_instance: a single instance of a Case model
        :param order: the order associated with the name search
        :param searchname: the name that was searched
        :return: the XML node representing this case
        """
        # type: (Case, orders.models.Order) -> xml.etree.ElementTree
        # @TODO: can be multiple debts per judgment per case
        # debt_instance = Debt.objects.filter\
        #     (docketed_judgment_seq_num=case_instance.docketed_judgment_seq_num).first()  # type:Debt
        debt_instance = case_instance.debt_set.all()[0]  # type: orders.model.Debt
        # @TODO: this only looks at the first debt!
        judgment_instance = case_instance.judgment_set.all()[0]  # type: orders.model.Judgment
        # @TODO: this only looks at the first judgment!

        client_file_num_xml = SubElement(self.top, 'CLIENT_REF_NUM')
        client_file_num_xml.text = order.title_number  # legacy error, really client ref file number
        child_case = SubElement(self.top, 'case')
        judgment_type_code = case_instance.docketed_judgment_type_code
        seq_num = case_instance.docketed_judgment_seq_num
        searchname_xml = SubElement(child_case, 'SEARCHNAME')
        searchname_xml.text = str(searchname)
        judgment_number_xml = SubElement(child_case, 'JUDGMENT_NUMBER')
        judgment_number_xml.text = "{}-{}-{}{}".format(judgment_type_code, seq_num, case_instance.docketed_judgment_cc,
                                                       case_instance.docketed_judgment_yy)
        case_casenumber_xml = SubElement(child_case, 'CASE_NUMBER')
        case_number = case_instance.acms_docket_number
        if case_number == "":
            case_number = case_instance.nonacms_docket_number
        case_casenumber_xml.text = case_number
        case_date_entered_xml = SubElement(child_case, 'DATE_ENTERED')
        case_date_entered_xml.text = self._make_american_date(case_instance.case_filed_date)
        if case_date_entered_xml.text == '00/00/00':
            case_date_entered_xml.text = self._make_american_date(debt_instance.entered_date)
        case_date_signed_xml = SubElement(child_case, 'DATE_SIGNED')
        case_docketed_date_xml = SubElement(child_case, 'DOCKETED_DATE')
        case_docketed_date_xml.text = self._make_american_date(judgment_instance.judgment_docketed_date)

        case_date_signed_xml.text = self._make_american_date(debt_instance.debt_status_date)
        case_note_xml = SubElement(child_case, 'CASE_NOTE')
        case_note_xml.text = debt_instance.debt_comments

        case_action_type_xml = SubElement(child_case, 'ACTION_TYPE')
        case_action_type_xml.text = self._map_civil_venue_code(case_instance.case_type_code, SpecCodes.CIVIL)
        # ;;;;;
        # case_action_type_xml.text = 'blah2'
        # ;;;;;
        case_venue_xml = SubElement(child_case, 'VENUE')
        case_venue_xml.text = case_instance.acms_venue_id
        case_venue_xml.text = self._map_civil_venue_code(case_instance.acms_venue_id, SpecCodes.VENUE)
        case_status_xml = SubElement(child_case, 'CASE_STATUS')
        case_status_xml.text = debt_instance.record_type_code #case_instance.record_type_code

        # get comment
        comment_text = ""
        case_comments_xml = SubElement(child_case, 'COMMENTS')
        comments = case_instance.comment_set.all()
        import string
        if len(comments) > 0:
            c_list = []
            for c in comments:
                c_list.append(c.jdgcomm_comments)
            # c_str = comments[0].jdgcomm_comments
            c_str = "\n".join(c_list)
            comment_text = ''.join([x if x in string.printable else '' for x in c_str])
        case_comments_xml.text = comment_text

        return child_case

    def _make_case_bankruptcy_xml_elements(self, browser, matched_name, bk_cases_dict, searchname):  # bk_case_dict contains a dict of db_ref and case_model
        """
        Build case-related XML elements for this class instance
        :param matched_name: a single instance of PacerSearchUtils.BkNameMatch
        :return: the XML node representing this case
        """
        # type: (utils.BkNameMatchCaseList, dict(PacerBankruptcyIndexCase)) -> None

        def map_db_ref_to_ec2_server_instance(db_ref):
            """
            Unused. Map a ec2 host name to a db instance defined in the settings config file
            :param db_ref:
            :return: str of the host
            """
            from django.conf import settings
            host_instance = settings.DATABASES[db_ref]['HOST']
            print(("DB host being used to retrieve file: {}".format(host_instance)))
            return host_instance

        def get_remote_party_file(remote_db, remote_username, remote_fetch_files):
            """
            Grabs a remote file from remote_file_path on server remote_db and returns the path to a tmp file with that file's contents
            The calling function needs to delete this file when they're done with it
            :param remote_db: address of remote system, SSH enabled
            :param remote_file_path: path of file on remote system
            :return: str to tmp_file on host system
            """
            import paramiko
            import tempfile
            from pacerscraper.utils import SSHManager

            k = paramiko.RSAKey.from_private_key_file(
                os.path.join(str(settings.ROOT_DIR), "bitnami-aws-879738187445.pem"))

            c = paramiko.SSHClient()
            c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            c.connect(hostname=remote_db, username=remote_username, pkey=k)

            tmp_file_paths = []
            file_dir = "/opt/bitnami/apps/django/django_projects/jsnetwork_project/jsnetwork_project/media/pacer_bankruptcy_idx"
            for remote_file in remote_fetch_files:
                remote_file_path = os.path.join(file_dir, remote_file)
                print(("Remote file path being used for fetch: {}".format(remote_file_path)))

                remote_file_contents = SSHManager.get_file_contents_from_ssh(c, remote_file_path)
                # parse data needed from files
                fd, tmp_file_path = tempfile.mkstemp()
                # party_details = []
                try:
                    with os.fdopen(fd, 'w') as tmp:
                        tmp.write(remote_file_contents)
                        # for debugging
                    with open(os.path.join('jsnetwork_project','media','last.html'), 'w') as f:
                        f.write(remote_file_contents)
                except:
                    print('Problem accessing remote file!')
                    tmp_file_path = None
                tmp_file_paths.append(tmp_file_path)
            return tmp_file_paths

        def fetch_party_details_from_file(browser, file_path, original_bk_case):
            """
            Extracts details of a party from a BKCY file
            :param browser: the selenium browser to use for parsing
            :param file_path: the physical path to the file
            :param original_bk_case: the bkcy case number
            :return: a dict containing various party details
            """
            import os
            from selenium.common.exceptions import NoSuchElementException
            from pacerscraper.utils import PacerScraperUtils, ReportHelper, PacerScraperBankruptcyUtils

            # print('Parsing party details from file path: {}'.format(file_path))
            party_details = {}
            # party_details['trustee'] = 'No trustee listed'
                # browser = PacerScraperUtils.load_local_judgment_report(file_path)
            html_source = os.path.join(PacerScraperUtils.pacer_files_dir, file_path)
            try:
                assert os.path.exists(html_source) == True
                # html_source = os.readlink(html_source)
            except AssertionError:
                # try to recover by re-fetching the file from the server
                print(("Couldn't find file! Refetching {} and related files from server".format(file_path)))
                try:
                    browser2 = PacerScraperBankruptcyUtils.get_webdriver()
                    PacerScraperBankruptcyUtils.pacer_login(browser2)
                    # PacerScraperBankruptcyUtils.navigate_to_query_form(browser2)

                    browser2.get(PacerScraperBankruptcyUtils.pacer_bankruptcy_search_form_url)
                    PacerScraperBankruptcyUtils.check_page_has_text(browser2, r'Live Database')

                    PacerScraperUtils.enter_case_data_on_form(browser2, original_bk_case.case_number)
                    d = PacerScraperBankruptcyUtils.archive_case_summary_data(
                        browser2, PacerScraperBankruptcyUtils.bankruptcy_files_dir, original_bk_case)
                    # update original case record with new data for building XML in printfactory
                    original_bk_case.case_summary_file = d['Case Summary']
                    original_bk_case.party_file = d['Party']
                    original_bk_case.alias_file = d['Alias']
                    # update case with new file info - don't save, don't know where original record came from
                    # original_bk_case.save(using=original_bk_case.db_ref)
                    bankruptcy_files_dir = PacerScraperBankruptcyUtils.bankruptcy_files_dir
                    html_source = os.path.join(bankruptcy_files_dir, original_bk_case.party_file)
                except NoSuchElementException:
                    print('Encountered error while trying to refetch data from server.')
                    raise
                else:
                    assert os.path.exists(html_source) == True
                finally:
                    browser2.close()

            browser_filename = 'file://' + html_source
            # browser = PacerScraperBase.get_webdriver()
            browser.get(browser_filename)
            # @TODO: move the stuff above into a function
            tbody_element = browser.find_element_by_css_selector("table tbody")
            rows = tbody_element.find_elements_by_tag_name('tr')
            for row in rows:
                row_match = row.find_elements_by_tag_name('td')
                party_cell = row_match[0]
                # @TODO: don't call lower() a million times below
                # print("Examining cell text  -->: {}".format(party_cell.text))
                if 'defendant' in party_cell.text.lower() or 'debtor' in party_cell.text.lower():
                    #  check if matched name in text somewhere
                    # print('Found matching party for parsing!!!!')
                    # print('Matching party names are {}'.format(matched_name.name_list))  # [u'Sung Nam Park']
                    # for name in matched_name.name_list:
                    #     print("Names in name match list: {}".format(name.split()))
                    if all(name in party_cell.text for name in matched_name.name_list):
                        if 'debtor' in party_cell.text.lower() or 'defendant' in party_cell.text.lower():
                            # print("Using cell text to build XML: {}".format(party_cell.text))
                            party_details['attorney'] = ReportHelper.parse_attorney_from_debtor_details(row)
                            party_details['debtor'] = ReportHelper.parse_party_from_debtor_details(row)
                            # print(party_details)
                if 'trustee' in party_cell.text.lower() and not party_details.get('trustee', None):
                    party_details['trustee'] = ReportHelper.parse_trustee_from_party_details(row)
                    # print('Got trustee data {} from function'.format(party_details['trustee']))
                    # print('$$$$$$$$$$$$ Assigned trustee {} $$$$$$$$$$$$'.format(party_details['trustee']))
            if not party_details.get('trustee'):
                party_details['trustee'] = 'No trustee listed'

            voluntary_element = browser.find_element_by_css_selector("body div center")
            ve = voluntary_element.text  # type: str

            # parse voluntary BK data - more complicated than you would think
            idx_vol_begin = ve.find('Vol:')+5
            if idx_vol_begin > 4:
                idx_judge = ve.find('Judge:')
                idx_related = ve.find('Related bankruptcy:')
                idx_honarable = ve.find('Honorable:')
                vol_found_list = [idx_judge, idx_related, idx_honarable]
                idx_vol_stop = min(i for i in vol_found_list if i > 0)
                party_details['voluntary'] = ve[idx_vol_begin:idx_vol_stop].strip().split(' ')[0]
            else:
                party_details['voluntary'] = ''

            # parse chapter data if present
            chapter_str = 'Chapter: '
            idx_chapter = ve.find(chapter_str)
            if idx_chapter > 0:
                idx_chapter_end = ve.find(' ', idx_chapter+len(chapter_str)+1)
                party_details['chapter'] = ve[idx_chapter+len(chapter_str):idx_chapter_end].strip()
            else:
                party_details['chapter'] = ''
            # parse dates
            # date_element = browser.find_element_by_css_selector("body div center")
            date_element = browser.find_element_by_xpath("/html/body/div/center[1]")
            date_filed_str = "Date filed:"
            date_discharged_str = "Date discharged:"
            date_last_filing_str = "Date of last filing:"
            date_terminated_str = "Date terminated:"
            de = date_element.text
            # print("Possible date element found in info block: {}".format(de))
            if date_filed_str in de:
                party_details['date_filed'] = fetch_date_from_case_details(date_filed_str, de)
                # print("----> Date filed: {}".format(party_details['date_filed']))
            if date_discharged_str in date_element.text:
                party_details['date_discharged'] = fetch_date_from_case_details(date_discharged_str, de)
                # print("----> Date discharged: {}".format(party_details['date_discharged']))
            elif date_last_filing_str in date_element.text:
                party_details['date_discharged'] = fetch_date_from_case_details(date_last_filing_str, de)
                # print("----> Date discharged: {}".format(party_details['date_discharged']))
            if date_terminated_str in date_element.text:
                party_details['date_terminated'] = fetch_date_from_case_details(date_terminated_str, de)
                # print("----> Date terminated: {}".format(party_details['date_terminated']))
            return party_details

        def fetch_date_from_case_details(date_descr_str, date_element_text):
            """
            Fetch the case filed data from the supplied date element text str
            :param date_descr_str: the string to look for when locating the date element in the html. this proceeds the date desired to be matched on
            :param date_element_text: the date element pulled from the case file's html code
            :return:
            """
            sample_date_len = len('01/01/2000')+2
            date_descr_str_len = len(date_descr_str)
            date_filed_idx = date_element_text.find(date_descr_str)
            date_filed = date_element_text[date_filed_idx + date_descr_str_len:
                                           len(date_descr_str) + date_filed_idx + sample_date_len].strip()
            return date_filed

        def fetch_case_summary_details_from_tmp_file(tmp_file_path):
            """
            Unused. fetch case summary details from a file
            :param tmp_file_path: the filepath of the file to parse
            :return:
            """
            import os
            from pacerscraper.utils import PacerScraperUtils

            case_summary_details = {}
            ssn_match = []
            try:
                browser = PacerScraperUtils.load_local_judgment_report(tmp_file_path)
                table_row_element = browser.find_element_by_css_selector("table tbody tr")
                venue_element = table_row_element.find_elements_by_tag_name('td')[0]
                filed_element = table_row_element.find_elements_by_tag_name('td')[2]
                case_summary_details['venue'] = venue_element.text
                case_summary_details['filed'] = filed_element.text

                tbody_element = browser.find_element_by_css_selector("table tbody")
                discharged_element = tbody_element.find_element_by_css_selector('tr:nth-of-type(3) td:nth-of-type(3)')
                case_summary_details['discharged'] = discharged_element.text

                # pull SSNs
                first_td_elements = tbody_element.find_elements_by_css_selector('tr td:nth-of-type(1)')
                for td_element in first_td_elements:
                    if 'Party' in td_element.text:
                        print(('Found party info: {}'.format(td_element.text)))
                        ssn_match.append(td_element.text)
                case_summary_details['ssn'] = ssn_match

                # print("Grabbed venue: {}".format(case_summary_details['venue']))
                # print("Grabbed filed date: {}".format(case_summary_details['filed']))
                # print("Grabbed discharged date: {}".format(case_summary_details['discharged']))
            finally:
                os.remove(tmp_file_path)
            return case_summary_details

        def make_party_file_xml(bk_cases_dict, party_details_from_file, case_details_from_file=None):
            """
            Make the party xml from a dict of party details
            :param bk_cases_dict: a dict of bkcy cases
            :param party_details_from_file: a dict of party details
            :param case_details_from_file: unused. a dict of bkcy case details
            :return:
            """
            parties_xml = SubElement(bk_case, 'PARTIES')
            attorney_xml = SubElement(parties_xml, 'ATTORNEY')
            print(('-------> Full party details: {}'.format(party_details_from_file)))
            attorney_xml.text = '\n'.join(party_details_from_file.get('attorney',''))

            trustee_xml = SubElement(parties_xml, 'TRUSTEE')
            trustee_xml.text = party_details_from_file.get('trustee','')

            # bk_idx_case = PacerBankruptcyIndexCase.objects.get(case_number=case_instance.case_number)
            bk_idx_case = bk_cases_dict[matched_name.case_number]['case_model']
            print(('Db record id for filtered case: {}'.format(bk_idx_case.id)))
            # @TODO: verify there is ever only one case (above)
            bk_parties = bk_idx_case.pacerbankruptcyparty_set.all()
            # bk_parties = PacerBankruptcyParty.objects.filter(bankruptcy_index_case__case_number=case_instance.case_number)
            # print("Number of parties matched during xml filter: {}".format(len(bk_parties)))

            chapter_xml = SubElement(bk_case, 'CHAPTER')
            chapter_xml.text = party_details_from_file.get('chapter','')
            voluntary_xml = SubElement(bk_case, 'VOLUNTARY')
            voluntary_xml.text = party_details_from_file.get('voluntary','')
            date_filed_xml = SubElement(bk_case, 'DATE_FILED')
            date_filed_xml.text = party_details_from_file.get('date_filed','')
            date_discharged_xml = SubElement(bk_case, 'DATE_DISCHARGED')
            date_discharged_xml.text = party_details_from_file.get('date_discharged','')
            date_terminated_xml = SubElement(bk_case, 'DATE_TERMINATED')
            date_terminated_xml.text = party_details_from_file.get('date_terminated','')

            party_details = party_details_from_file['debtor']  # type: str
            party_details_split = party_details.split('\n')
            party_name = party_details_split[0]
            party_address_details = []
            party_ssn = ''
            for i, line in enumerate(party_details_split):
                if i > 0 and not 'SSN' in line:
                    party_address_details.append(line)
                elif 'SSN' in line:
                    party_ssn = line
                    break

            party_city_state_zip = party_address_details[-1]
            party_details_address_12 = party_address_details[:-1]
            party_xml = SubElement(parties_xml, 'DEBTOR')
            party_xml.text = party_name
            party_address_xml = SubElement(parties_xml, 'ADDRESS')
            party_address_xml.text = ', '.join(party_details_address_12)
            party_zip_xml = SubElement(parties_xml, 'CITYSTATEZIP')
            party_zip_xml.text = party_city_state_zip
            party_ssn_xml = SubElement(parties_xml, 'SSN')
            party_ssn_xml.text = party_ssn

            # if case_details_from_file:
            #     for party in case_details_from_file['ssn']: # type: str
            #         party_data_sep = party.split('\n')
            #         pn = party_data_sep[0]
            #         party_name = pn[pn.find(':') + 1:pn.find('(')].strip()
            #         party_ssn = party_data_sep[1].strip()
            #         party_xml = SubElement(parties_xml, 'PARTY')
            #         party_name_xml = SubElement(party_xml, 'NAME')
            #         party_name_xml.text = party_name
            #         ssn_xml = SubElement(party_xml, 'SSN')
            #         ssn_xml.text = party_ssn



            # print(tostring(bk_case))
            return bk_case

        from pacerscraper.models import PacerBankruptcyIndexCase
        from django.conf import settings

        matched_case_data = bk_cases_dict.get(matched_name.case_number, None)
        if matched_case_data:
            original_bk_case = matched_case_data['case_model'] # type: PacerBankruptcyIndexCase
            original_bk_case.db_ref = matched_case_data['db_ref']  # add for saving record later
            bk_case = SubElement(self.top, 'case')
            searchname_xml = SubElement(bk_case, 'SEARCHNAME')
            searchname_xml.text = str(searchname)
            bankruptcy_number_xml = SubElement(bk_case, 'BANKRUPTCY_NUMBER')
            bankruptcy_number_xml.text = matched_name.case_number
            # print('Bankruptcy case details: {}'.format(original_bk_case))
            # print("Bankruptcy case party details: {}".format(original_bk_case.pacerbankruptcyparty_set.all()))

            # get party data from file here
            ec2_login = "bitnami"
            party_file = original_bk_case.party_file
            case_summary_file = original_bk_case.case_summary_file
            print(("Bankruptcy party original file: {}".format(original_bk_case.party_file)))
            print(("Bankruptcy case summary original file: {}".format(original_bk_case.case_summary_file)))
            # remote_fetch_files = [party_file, case_summary_file]
            remote_fetch_files = [party_file]
            party_db = bk_cases_dict[matched_name.case_number]['db_ref']

            party_file = os.path.join(settings.MEDIA_ROOT, 'pacer_bankruptcy_idx',party_file)
            try:
                assert(os.path.exists(party_file))
            except Exception:
                from pacerscraper.utils import PacerScraperBankruptcyUtils
                bankruptcy_files_dir = PacerScraperBankruptcyUtils.bankruptcy_files_dir
                party_file = os.path.join(bankruptcy_files_dir, original_bk_case.party_file)
            print(('File being used to fetch data for case number {}: {}'.format(matched_name.case_number, party_file)))
            # ssh_instance = map_db_ref_to_ec2_server_instance(party_db)
            # remote_file_paths = get_remote_party_file(ssh_instance, ec2_login, remote_fetch_files)
            #
            # remote_party_file_path = remote_file_paths[0]
            # if len(remote_file_paths) > 1:
            #     remote_case_index_file_path = remote_file_paths[1]

            # party_details_from_file = fetch_party_details_from_file(remote_party_file_path)
            try:
                party_details_from_file = fetch_party_details_from_file(browser, party_file, original_bk_case)
                # case_details_from_file = fetch_case_summary_details_from_tmp_file(remote_case_index_file_path)
                # bk_case = make_party_file_xml(bk_cases_dict, party_details_from_file, case_details_from_file)
                bk_case = make_party_file_xml(bk_cases_dict, party_details_from_file)
            except Exception:  # this tends to trigger when the BK data couldn't be refetched @TODO: fixme
                pass
            # modifying the top node's contents, so don't need to return anything
            # return bk_case



    # a lot of this is duplicated from from _make_case_bankruptcy_xml_elements
    # consolidate this once it works (then make it right...)
    def _make_case_usdc_xml_elements(self, browser, matched_names, usdc_cases_dict, searchname):  # bk_case_dict contains a dict of db_ref and case_model
        """
        Build case-related XML elements for this class instance
        :param matched_name: a list of PacerSearchUtils.BkNameMatch
        :return: the XML node representing this case
        """
        # type: (utils.BkNameMatchCaseList, dict(PacerJudgmentIndexCase)) -> None

        def fetch_party_details_from_file(browser, file_path):
            import os
            from pacerscraper.utils import PacerScraperUtils, ReportHelper

            print(('Parsing party details from file path: {}'.format(file_path)))
            party_details = {}
            party_details['trustee'] = 'No trustee listed'
                # browser = PacerScraperUtils.load_local_judgment_report(file_path)
            html_source = os.path.join(PacerScraperUtils.pacer_files_dir, file_path) #  @TODO: check bk isn't broken here
            try:
                assert os.path.exists(html_source) == True
                # html_source = os.readlink(html_source)
            except OSError:
                pass
            browser_filename = 'file://' + html_source
            # browser = PacerScraperBase.get_webdriver()
            browser.get(browser_filename)
            # @TODO: move the stuff above into a function

            # find judge for case
            judge_element = browser.find_elements_by_xpath("//*[contains(text(), 'presiding')]")
            print(('Located judge: {}'.format(judge_element)))

            tbody_element = browser.find_element_by_css_selector("table tbody")
            rows = tbody_element.find_elements_by_tag_name('tr')
            parsed_party_details = []
            parsed_creditor_details = []
            parsed_attorney_details = []
            parsed_creditor_attorney_details = []
            for row in rows:
                row_match = row.find_elements_by_tag_name('td')
                party_cell = row_match[0]
                # print("Examining cell text  -->: {}".format(party_cell.text))
                # if 'defendant' in party_cell.text.lower() or 'debtor' in party_cell.text.lower():
                #     if all(name in party_cell.text for name in matched_names.name_list):
                #         if 'debtor' in party_cell.text.lower() or 'defendant' in party_cell.text.lower():
                #             party_details['attorney'] = ReportHelper.parse_attorney_from_debtor_details(row)
                #             party_details['debtor'] = party_details.get('debtor', '').\
                #                 append(ReportHelper.parse_party_from_debtor_details(row))
                #         elif '(Trustee)' in party_cell.text:
                #             party_details['trustee'] = ReportHelper.parse_trustee_from_party_details(row)
                if 'defendant' in party_cell.text.lower() or 'debtor' in party_cell.text.lower():
                    parsed_party_details.append(ReportHelper.parse_party_from_debtor_details(row))
                    parsed_attorney_details.append('\n'.join(ReportHelper.parse_attorney_from_debtor_details(row)))
                    # print('************** Parsed party details: {}'.format(parsed_party_details))
                if 'plaintiff' in party_cell.text.lower() or 'creditor' in party_cell.text.lower():
                    parsed_creditor_details.append(ReportHelper.parse_creditor_from_party_details(row))
                    parsed_creditor_attorney_details.append('\n'.join(ReportHelper.parse_attorney_from_debtor_details(row)))
                    # could use the same functions here that are used above

            party_details['debtor'] = '\n'.join(parsed_party_details)
            party_details['creditor'] = '\n'.join(parsed_creditor_details)
            # party_details['attorney'] = '\n'.join(parsed_attorney_details)

            deduped_attorney_list = []
            for attorney in parsed_attorney_details:
                if not attorney in deduped_attorney_list:
                    deduped_attorney_list.append(attorney)
            party_details['attorney'] = '\n'.join(deduped_attorney_list)
            # party_details['attorney'] = '\n'.join(list(set(parsed_attorney_details)))

            deduped_creditor_attorney_list = []
            for attorney in parsed_creditor_attorney_details:
                if not attorney in deduped_creditor_attorney_list:
                    deduped_creditor_attorney_list.append(attorney)
            party_details['creditor_attorney'] = '\n'.join(deduped_creditor_attorney_list)
            # @TODO: check this isn't set to another field in BK report

            voluntary_element = browser.find_element_by_css_selector("body div center")
            ve = voluntary_element.text  # type: str

            # parse voluntary BK data - more complicated than you would think
            idx_vol_begin = ve.find('Vol:')+5
            if idx_vol_begin > 4:
                idx_judge = ve.find('Judge:')
                idx_related = ve.find('Related bankruptcy:')
                idx_honarable = ve.find('Honorable:')
                vol_found_list = [idx_judge, idx_related, idx_honarable]
                idx_vol_stop = min(i for i in vol_found_list if i > 0)
                party_details['voluntary'] = ve[idx_vol_begin:idx_vol_stop].strip()
            else:
                party_details['voluntary'] = ''

            # parse chapter data if present
            chapter_str = 'Chapter: '
            idx_chapter = ve.find(chapter_str)
            if idx_chapter > 0:
                idx_chapter_end = ve.find(' ', idx_chapter+len(chapter_str)+1)
                party_details['chapter'] = ve[idx_chapter+len(chapter_str):idx_chapter_end].strip()
            else:
                party_details['chapter'] = ''
            # parse dates
            # date_element = browser.find_element_by_css_selector("body div center")
            date_element = browser.find_element_by_xpath("/html/body/div/center[1]")
            date_filed_str = "Date filed:"
            date_discharged_str = "Date discharged:"
            date_last_filing_str = "Date of last filing:"
            date_terminated_str = "Date terminated:"
            de = date_element.text
            # print("Possible date element found in info block: {}".format(de))
            if date_filed_str in de:
                party_details['date_filed'] = fetch_date_from_case_details(date_filed_str, de)
                # print("----> Date filed: {}".format(party_details['date_filed']))
            if date_discharged_str in date_element.text:
                party_details['date_discharged'] = fetch_date_from_case_details(date_discharged_str, de)
                # print("----> Date discharged: {}".format(party_details['date_discharged']))
            elif date_last_filing_str in date_element.text:
                party_details['date_discharged'] = fetch_date_from_case_details(date_last_filing_str, de)
                # print("----> Date discharged: {}".format(party_details['date_discharged']))
            if date_terminated_str in date_element.text:
                party_details['date_terminated'] = fetch_date_from_case_details(date_terminated_str, de)
                # print("----> Date terminated: {}".format(party_details['date_terminated']))
            print(("Party details dict contents: {}".format(party_details)))
            return party_details

        def fetch_date_from_case_details(date_descr_str, date_element_text):
            sample_date_len = len('01/01/2000')+2
            date_descr_str_len = len(date_descr_str)
            date_filed_idx = date_element_text.find(date_descr_str)
            date_filed = date_element_text[date_filed_idx + date_descr_str_len:
                                           len(date_descr_str) + date_filed_idx + sample_date_len].strip()
            return date_filed

        def make_party_file_xml(usdc_cases_dict, party_details_from_file, case_details_from_file=None):
            parties_xml = SubElement(usdc_case, 'PARTIES')
            attorney_xml = SubElement(parties_xml, 'ATTORNEY')
            # attorney_xml.text = '\n'.join(party_details_from_file.get('attorney',''))
            attorney_xml.text = party_details_from_file.get('attorney','')

            trustee_xml = SubElement(parties_xml, 'TRUSTEE')
            trustee_xml.text = party_details_from_file.get('trustee','')

            # @TODO: this is wrong - specific to a db instance
            # bk_idx_case = PacerBankruptcyIndexCase.objects.get(case_number=case_instance.case_number)
            bk_idx_case = usdc_cases_dict[matched_names.case_number]
            print(('Db record id for filtered case: {}'.format(bk_idx_case.id)))
            # @TODO: verify there is ever only one case (above)
            usdc_parties = bk_idx_case.pacerjudgmentparty_set.all()

            date_filed_xml = SubElement(usdc_case, 'DATE_FILED')
            date_filed_xml.text = party_details_from_file.get('date_filed','')
            date_discharged_xml = SubElement(usdc_case, 'DATE_DISCHARGED')
            date_discharged_xml.text = party_details_from_file.get('date_discharged','')
            date_terminated_xml = SubElement(usdc_case, 'DATE_TERMINATED')
            date_terminated_xml.text = party_details_from_file.get('date_terminated','')

            party_details = party_details_from_file.get('debtor','')  # type: str
            party_details_split = party_details.split('\n')
            party_name = '\n'.join(party_details_split)
            party_xml = SubElement(parties_xml, 'DEBTOR')
            party_xml.text = party_name

            creditor_xml = SubElement(parties_xml, 'CREDITOR')
            creditor_xml.text = party_details_from_file.get('creditor','')
            creditor_attorney_xml = SubElement(parties_xml, 'CREDITOR_ATTORNEY')
            creditor_attorney_xml.text = party_details_from_file.get('creditor_attorney','')

            return usdc_case

        from pacerscraper.models import PacerJudgmentIndexCase
        from django.conf import settings
        usdc_case = SubElement(self.top, 'case')

        searchname_xml = SubElement(usdc_case, 'SEARCHNAME')
        searchname_xml.text = str(searchname)

        matched_name_case_number = matched_names.case_number

        usdc_case_number = self.format_usdc_case_number(matched_name_case_number)

        usdc_case_number_xml = SubElement(usdc_case, 'USDC_CASE_NUMBER')
        usdc_case_number_xml.text = usdc_case_number
        original_usdc_case = usdc_cases_dict[matched_names.case_number] # type: PacerJudgmentIndexCase
        print(original_usdc_case)

        # get party data from file here
        party_file = original_usdc_case.party_file
        print(("Usdc party original file: {}".format(original_usdc_case.party_file)))
        print(("Usdc case summary original file: {}".format(original_usdc_case.case_summary_file)))
        party_file = os.path.join(settings.MEDIA_ROOT, 'pacer_judgment_idx',party_file)
        print(('File being used to fetch data for case number {}: {}'.format(matched_names.case_number, party_file)))

        party_details_from_file = fetch_party_details_from_file(browser, party_file)
        usdc_case = make_party_file_xml(usdc_cases_dict, party_details_from_file)

        # modifying the top node's contents, so don't need to return anything
        # return bk_case

    @staticmethod
    def format_usdc_case_number(unformatted_case_number):
        """
        Change the USDC case number into a format better suited for end users
        :param unformatted_case_number:
        :return: str
        """
        import re

        exp = "(?<=\:)([0-9]+)\-(.+\-)[A-Z]+"
        m = re.search(exp, unformatted_case_number)
        usdc_case_partial_year = m.group(1)
        usdc_case_number = m.group(2).upper()
        if int(usdc_case_partial_year) > 90:
            usdc_case_number = usdc_case_number + '19' + usdc_case_partial_year
        else:
            usdc_case_number = usdc_case_number + '20' + usdc_case_partial_year
        return usdc_case_number

    def _make_cover_page_court_xml(self, parent_element, court_name_matches, court_name):
        """
        Build the xml elements for the court_name matches found for this court
        :param parent_element: top xml element to attach court match xml elements to
        :param court_name_matches: named_tuple of matches
        :param court_name: name of court searched
        :return:
        """
        child_court = SubElement(parent_element, str(court_name).upper())
        court_match_count_xml = SubElement(child_court, 'NUM_MATCHES')
        court_match_count_xml.text = str(len(court_name_matches))
        court_name_xml = SubElement(child_court, 'COURT_NAME')
        court_name_xml.text = court_name

        return child_court

    def _make_cover_page_client_xml(self, parent_element, client, order):
        """
        Build the xml elements for the client that asked for the search
        :param parent_element: top xml element to attach court match xml elements to
        :param client: Client object
        :param order: the Order associated with this search
        :return:
        """
        client_info = SubElement(parent_element, 'CLIENT_INFO')
        client_file_num_xml = SubElement(client_info, 'CLIENT_FILE_NUM')
        client_file_num_xml.text = order.title_number  # data model typo from long, long ago; really client file num
        client_name_xml = SubElement(client_info, 'NAME')
        client_name_xml.text = client.client_name
        client_address_xml = SubElement(client_info, 'ADDRESS')
        client_address_txt = client.addr1
        if client.addr2:
            client_address_txt = client_address_txt + "\n{}".format(client.addr2)
        client_address_xml.text = client_address_txt
        client_city_state_zip_xml = SubElement(client_info, 'CITY_STATE_ZIP')
        client_city_state_zip_txt = "{}, {} {}".format(client.city, client.state, client.zip)
        client_city_state_zip_xml.text = client_city_state_zip_txt


    def _make_debt_xml(self, case_element, debt_instance):
        """
        Build debt-related XML elements for the provide case instance
        :param case_element: a single instance of a Case model
        :param debt_instance: the debt instance to XML-ify and add to the case XML element
        :return: the XML node representing this debt and the debt comment to attach to the creditor element
        """
        debt_element = SubElement(case_element, 'DEBT')
        debt_party_due_amt_xml = SubElement(debt_element, 'DEBT_AMT')
        debt_party_due_amt_xml.text = self._make_float(debt_instance.party_due_amt, False)
        debt_party_orig_amt_xml = SubElement(debt_element, 'ORIG_DEBT_AMT')
        debt_amt = self._make_float(debt_instance.party_orig_amt, False)
        if debt_amt == '.00':
            debt_amt = self._make_float(debt_instance.party_other_award_orig_amt, False)
        debt_party_orig_amt_xml.text = debt_amt
        debt_other_award_due_amt_xml = SubElement(debt_element, 'DEBT_OTHER_AMT_DUE')
        debt_other_award_due_amt_xml.text = debt_instance.party_other_awd_due_amt
        debt_other_atty_fee_xml = SubElement(debt_element, 'DEBT_OTHER_ATTY_FEE')
        debt_other_atty_fee_xml.text = debt_instance.party_due_atty_fee_amt
        debt_original_docket_xml = SubElement(debt_element, 'DEBT_COMMENT')
        debt_original_docket_xml.text = debt_instance.debt_comments
        return debt_element

    def format_full_party_name(self, party_instance):
        """
        Generate a pretty-formatted party name from a party_instance
        :param party_instance: a Party model object
        :return: a str containing a formatted party name
        """
        if len(party_instance.party_last_name.strip()) == 20:
            party_name_formatted = party_instance.party_last_name + \
                                   party_instance.party_first_name
        else:
            party_name_formatted = "{}{}{}{}".format(party_instance.party_first_name.strip() + ' ',
                                                     self.format_party_middle_initial(party_instance.party_initial),
                                                     party_instance.party_last_name.strip(),
                                                     self.format_party_suffix_initials(party_instance.party_initials))
        return party_name_formatted

    def format_party_middle_initial(self, party_initial):
        """
        Generate formatted middle party initial for printing.
        Basically adds a blank space or returns an empty string if no middle initial is found
        :param party_initial: the middle initial to parse
        :return: a formatted middle initial for printing
        """
        party_formatted_middle_initial = party_initial.strip()
        if len(party_formatted_middle_initial) > 0:
            party_formatted_middle_initial = party_formatted_middle_initial + ' '
        return party_formatted_middle_initial

    def format_party_suffix_initials(self, party_initials):
        """
        Generate formatted suffix initials for printing.
        Basically adds a blank space or returns an empty string if no last name initial is found.
        Duplicated from middle initial but leaves some flexibility for future format variations
        :param party_initials:
        :return:
        """
        party_formatted_suffix_initials = party_initials.strip()
        if len(party_formatted_suffix_initials) > 0:
            party_formatted_suffix_initials = ' ' + party_formatted_suffix_initials
        return party_formatted_suffix_initials

    def _make_party_xml(self, party_element, party_instance, judgment_dobs):
        """
        Build party-related XML elements for the provide case instance
        :param debt_element: a single instance of a Case model
        :param party_instance: the party instance to XML-ify and add to the case XML element
        :param judgment_dobs: dictionary of judgment numbers without dashes and matching DOB
        """

        from django.conf import settings
        from statereport.utils import StateReportNameSearchUtils

        def format_alt_party_name(party_instance):
            """
            Formats an alt party name. This name can spill over multiple fields if the original name was longer
            than what the database could store in a single field, so some smarts are used here to determine what
            kind of name is being handled and it is formatted accordingly
            :param party_instance: the Party (alt) model object to parse
            :return:
            """
            if len(party_instance.party_last_name.strip()) == 20:
                party_name_formatted = party_instance.party_last_name + \
                                       party_instance.party_first_name + party_instance.party_initial
            else:
                party_name_formatted = "{} {}".format(party_instance.party_last_name.strip(),
                                                      party_instance.party_first_name.strip())
            return party_name_formatted

        print("-------------------------------------------")
        PARTY_ALT = "Party Alt"
        print(("Party last name detected before parsing: {}".format(party_instance.party_last_name, )))
        if isinstance(party_instance, PartyAlt):
            party_type = PARTY_ALT
            print('-----------> Found alt party name')
        elif isinstance(party_instance, PartyGuardian):
            party_type = "Party Guardian"
        elif isinstance(party_instance, Party):
            party_type = "Normal Party"
        else:
            party_type = "Unknown Party Type"

        credit_debt_party_info_xml = None
        if party_type == "Normal Party":
            party_type_code = party_instance.party_role_type_code
            if party_type_code == "C":
                party_type_code_long = "Creditor(s):"
            else:
                party_type_code_long = "Debtor(s):"
            # party_element = debt_element  # skipping explicit inclusion of <PARTY/> element
            if party_type_code == "C":
                credit_debt_party_info_xml = SubElement(party_element, 'CREDITOR')
                party_name_formatted = self.format_full_party_name(party_instance)
                creditor_debtor_street_name_xml = SubElement(credit_debt_party_info_xml, 'CREDITOR_STREET_NAME')
            else:
                credit_debt_party_info_xml = SubElement(party_element, 'DEBTOR')
                party_name_formatted = self.format_full_party_name(party_instance)
                party_judgment_num = party_instance.docketed_judgment_number
                party_dob = judgment_dobs.get(party_judgment_num, '')
                # party_license = judgment_dobs.get(party_judgment_num, '')
                # party_ssn = judgment_dobs.get(party_judgment_num, '')
                party_dob_xml = SubElement(credit_debt_party_info_xml, 'DOB')
                if settings.MERGE_PDF_SCRAPED_PARTY_INFO:
                    party_dob_extra = StateReportNameSearchUtils.get_party_extra_identifying_details(party_instance)
                    # if party_dob_extra:
                    #     party_dob_extra = ', ' + party_dob_extra
                    try:
                        party_dob = party_dob + party_dob_extra
                    except TypeError as e:  # known to happen with John Smith
                        party_dob = ''
                party_dob_xml.text = party_dob
                creditor_debtor_street_name_xml = SubElement(credit_debt_party_info_xml, 'DEBTOR_STREET_NAME')
            creditor_debtor_street_name_xml.text = PrintFactory.make_party_address(party_instance)

            party_info_xml = SubElement(credit_debt_party_info_xml, 'PARTY_NAME')
            party_info_xml.text = party_name_formatted.strip()
            debt_party_atty_first_name_xml = SubElement(credit_debt_party_info_xml, 'ATTY_FIRST')
            debt_party_atty_first_name_xml.text = party_instance.atty_firm_first_name.strip()
            debt_party_atty_last_name_xml = SubElement(credit_debt_party_info_xml, 'ATTY_LAST')
            debt_party_atty_last_name_xml.text = party_instance.atty_firm_last_name.strip()
        elif party_type == PARTY_ALT:
            # party_alt_count += 1
            # party_element = debt_element  # see reasoning above
            partyalt_xml = SubElement(party_element, 'PARTY_ALT')
            partyalt_name_xml = SubElement(partyalt_xml, 'PARTY_NAME')
            party_alt_name_formatted = format_alt_party_name(party_instance)
            partyalt_name_xml.text = party_alt_name_formatted
            # partyalt_address_xml = SubElement(partyalt_xml, 'PARTY_ADDRESS')
            # partyalt_address_xml.text = self._make_party_address(party_instance)

        # check for revived status codes and dates
        if credit_debt_party_info_xml:
            party_role_type_code = SubElement(credit_debt_party_info_xml, 'PARTY_ROLE_TYPE_CODE')
            if party_instance.ptydebt_status_code == '03':
                party_role_type_code.text = 'Revived on'
            ptydebt_status_date = SubElement(credit_debt_party_info_xml, 'PTYDEBT_STATUS_DATE')
            ptydebt_status_date.text = party_instance.ptydebt_status_date
        else:
            pass

    @staticmethod
    def make_party_address(party_instance):
        """
        Generate a pretty-print party address from a Party instance
        :param party_instance: the Party model to process
        :return: a string containing a formatted address
        """
        address = ""
        if isinstance(party_instance, Party) and party_instance.party_street_name != '':
            address = "{}, {}, {} {}-{}".format(
                party_instance.party_street_name, party_instance.party_city_name,
                party_instance.party_state_code, party_instance.party_zip_5, party_instance.party_zip_4)
        return address

    # def make_xml(self, case_instance):
    def make_xml(self, cases, order, searchname, judgment_dobs):
        """
        Make an XML document containing case data for state report
        :param cases: one or more instances of case
        :param order: the order associated with the name search
        :param searchname: the name that was searched
        :param judgment_dobs: dictionary of judgment numbers without dashes and matching DOB

        :return: XML document with human readable case data
        """
        top = self.top
        for case_instance in cases:
            child_case = self._make_case_xml(case_instance, order, searchname)
            for debt_num, debt_instance in enumerate(case_instance.debt_set.all()):
                child_debt = self._make_debt_xml(child_case, debt_instance)
                # debtor_alt_names = case_instance.partyalt_set.filter(party_type_indicator=1)
                # for party_instance in debtor_alt_names:
                match_debt_num = "{:03}".format(debt_num + 1)
                for party_instance in case_instance.party_set.filter(debt_number=match_debt_num):
                    print(("Party record type code: " + party_instance.record_type_code_party))
                    print(("Party type indicator party: " + party_instance.party_type_indicator_party))
                    print(("Docketed Judgment Number: " + party_instance.docketed_judgment_number))
                    print(("Debt number: " + party_instance.debt_number_party))
                    print(("Party last name: " + party_instance.party_last_name))
                    print(("Party first name: " + party_instance.party_first_name))
                    self._make_party_xml(child_debt, party_instance, judgment_dobs)
                # for partyalt_instance in case_instance.partyalt_set.all():
                for partyalt_instance in case_instance.partyalt_set.filter(party_type_indicator__in=[1,2]):
                    no_judgment_dobs = {}
                    self._make_party_xml(child_debt, partyalt_instance, no_judgment_dobs)
                if len(case_instance.partyalt_set.all()) == 0:
                    partyalt_xml = SubElement(child_debt, 'PARTY_ALT')

        # print(tostring(top))
        # pretty_xml = self._pretty_print_xml(top)
        # print(pretty_xml)
        # return pretty_xml

        # search missing judgments
        # need to re-run the above xml building routine but make it pull from the missing judgment search results
        # django won't let us build an unsaved object graph, even with bulk=False on the _set.add() method
        # 20220504 @TODO: comment out for now, will revisit
        # missing_judgment_nums = self._find_missing_judgment_dockets(searchname)
        # cases = self._missing_judgment_cases_from_judgment_nums(missing_judgment_nums)
        #
        # for case_instance in cases:
        #     child_case = self._make_case_xml(case_instance, order, searchname)
        #     for debt_num, debt_instance in enumerate(case_instance.debt_set.all()):
        #         child_debt = self._make_debt_xml(child_case, debt_instance)
        #         for party_instance in case_instance.party_set:
        #             self._make_party_xml(child_debt, party_instance, judgment_dobs)


        return tostring(top)

    def make_bankruptcy_xml(self, name_matches, bk_cases_dict, order, searchname):  # bk_case_dict contains a dict of db_ref and case_model
        """
        Make an XML document from bankruptcy data containing case data
        :param name_matches: list of one or more BkNameMatches
        :return: str representation of XML document with human readable case data
        :rtype: str
        """
        # type: (list(PacerSearchUtils.BkNameMatch), dict(PacerBankruptcyIndexCase)) -> str
        from nameviewer.utils import PacerSearchUtils
        from pacerscraper.models import PacerBankruptcyIndexCase
        from pacerscraper.utils import PacerScraperBase

        print(("Working with a total of {} matches".format(str(len(name_matches)))))
        # print("Case dict contents: {}".format(bk_cases_dict))
        # browser = PacerScraperUtils.load_local_judgment_report(file_path)
        browser = PacerScraperBase.get_webdriver()
        top = self.top
        client_file_num_xml = SubElement(self.top, 'CLIENT_REF_NUM')
        client_file_num_xml.text = order.title_number  # legacy error, really client ref file number
        for bk_name_match_case_list in name_matches:
            self._make_case_bankruptcy_xml_elements(browser, bk_name_match_case_list, bk_cases_dict, searchname)
            # the above modified the top xml element
        browser.close()
        print((tostring(top)))
        pretty_xml = self._pretty_print_xml(top)
        return tostring(top)

    def make_usdc_xml(self, name_matches, usdc_cases_dict, order, searchname):  # usdc_case_dict contains a dict of db_ref and case_model
        """
        Make an XML document from bankruptcy data containing case data
        :param name_matches: list of one or more BkNameMatches
        :param searchname: the name that was searched
        :return: XML document with human readable case data
        """
        # type: (list(PacerSearchUtils.BkNameMatch), dict(PacerJudgmentIndexCase)) -> str
        from nameviewer.utils import PacerSearchUtils
        from pacerscraper.models import PacerJudgmentIndexCase
        from pacerscraper.utils import PacerScraperBase

        print(("Working with a total of {} matches".format(str(len(name_matches)))))
        # print("Case dict contents: {}".format(bk_cases_dict))
        # browser = PacerScraperUtils.load_local_judgment_report(file_path)
        browser = PacerScraperBase.get_webdriver()
        top = self.top
        client_file_num_xml = SubElement(self.top, 'CLIENT_REF_NUM')
        client_file_num_xml.text = order.title_number  # legacy error, really client ref file number
        for usdc_name_match_case_list in name_matches:
            self._make_case_usdc_xml_elements(browser, usdc_name_match_case_list, usdc_cases_dict, searchname)
            # the above modified the top xml element
        browser.close()
        print((tostring(top)))
        pretty_xml = self._pretty_print_xml(top)
        return tostring(top)

    def make_patriot_xml(self, name_matches, order, searchname):  # usdc_case_dict contains a dict of db_ref and case_model
        """
        Make an XML document from a list of patriot name matches
        :param name_matches: list of one or more str
        :param searchname: the name that was searched
        :return: XML document with human readable case data
        """
        # type: (str, order.models.Order, str) -> str
        import logging

        logger = logging.getLogger(__name__)
        # logger.info("Working with a total of {} matches".format(len(name_matches)))
        top = self.top
        client_file_num_xml = SubElement(self.top, 'CLIENT_REF_NUM')
        client_file_num_xml.text = order.title_number  # legacy error, really client ref file number
        self._make_search_name_xml(top, name_matches)
        self._make_patriot_search_dates_xml(top, order)
            # the above modified the top xml element
        print((tostring(top)))
        pretty_xml = self._pretty_print_xml(top)
        return tostring(top)

    def _make_search_name_xml(self, parent_element, name_matches):
        """
        Make a patriot search name xml object
        :param parent_element: the root element to attach the rest of the xml tree to
        :param name_matches: a list of name matches
        :return: an xml tree element containing the new patriot xml data generated
        """
        from patriot.helpers import PatriotResultsDict as prd
        import logging

        logger = logging.getLogger(__name__)

        logger.info("Got the following name match dictionary: {}".format(name_matches))

        for searched_name, name_match_dict in name_matches.items():
            search_name_element = SubElement(parent_element, 'SEARCH_NAME_ELEMENT')
            search_name_match_results = SubElement(search_name_element, 'MATCHES')
            searched_name_xml = SubElement(search_name_element, 'SEARCHED_NAME')
            searched_name_xml.text = searched_name
            prim_matches = name_match_dict[prd.PRIM_MATCHES]
            alt_matches = name_match_dict[prd.ALT_MATCHES]
            # @TODO handle alt matches
            for name_match in prim_matches:  # type: patriot.models.PatriotPrimName
                search_name_xml = SubElement(search_name_match_results, 'SEARCH_MATCH')
                search_name_xml.text = name_match.prim_name
                search_name_type_xml = SubElement(search_name_match_results, 'SEARCH_MATCH_TYPE')
                search_name_type_xml.text = name_match.prim_type
        return search_name_element

    def _make_patriot_search_dates_xml(self, parent_element, order):
        """
        Generate xml elements containing search dates used for an order
        :param parent_element: the root patriot element from the xml tree
        :param order: an order model
        """
        from django.utils import formats
        from orders.models import SearchName

        search_dates_element = SubElement(parent_element, 'SEARCH_DATES')
        search_name = SearchName.objects.filter(order_id=order.id).first()
        search_from_xml = SubElement(search_dates_element, 'SEARCH_FROM')
        search_from = formats.date_format(search_name.search_from, 'DATE_FORMAT')
        search_from_xml.text = search_from
        search_to_xml = SubElement(search_dates_element, 'SEARCH_TO')
        search_to = formats.date_format(search_name.search_to, 'DATE_FORMAT')
        search_to_xml.text = search_to

    def _make_search_name_xml2(self, order, parent_element, search_name, court_matches):
        """
        Make xml for the cover page containing names searched on and the number of matches found in each court
        :param parent_element: the root element to attach the rest of the xml tree to
        :param name_matches: a list of name matches
        :return: an xml tree element containing the new patriot xml data generated
        """
        from orders.models import SearchName
        search_name_element = SubElement(parent_element, 'SEARCH_NAME_ELEMENT')
        search_name_xml = SubElement(search_name_element, 'SEARCH_NAME')
        search_name_xml.text = search_name

        from django.utils import formats
        search_name = SearchName.objects.filter(order_id=order.id).first()
        search_from_xml = SubElement(search_name_element, 'SEARCH_FROM')
        search_from = formats.date_format(search_name.search_from, 'SHORT_DATE_FORMAT')
        search_from_xml.text = search_from
        search_to_xml = SubElement(search_name_element, 'SEARCH_TO')
        search_to = formats.date_format(search_name.search_to, 'SHORT_DATE_FORMAT')
        search_to_xml.text = search_to
        # add court match info
        if court_matches == None:
            court_match_xml = SubElement(search_name_element, 'COURT_MATCH')
            # court_match_xml.text = '*** NAME IS CLEAR ***'
        else:
            court_matches_set = set(court_matches)
            for court in court_matches_set:
                court_match_xml = SubElement(search_name_element, 'COURT_MATCH')
                court_match_xml.text = "{}-{}".format(court, str(court_matches.count(court)))
        return search_name_element


    def make_coverpage_xml(self, matched_case_dict, order):
        """
        Make an XML document containing data for cover page
        :param cases: one or more instances of case
        :return: XML document with human readable case data
        """
        # from pacerscraper.models import Client
        from orders.models import Client
        # assert isinstance(case_instance, Case), 'case_instance argument of wrong type!'
        top = self.top
        # for case_instance in cases:
        search_name = matched_case_dict.get('search_name','')
        assert(search_name != '')
        search_name_xml = self._make_search_name_xml(top, search_name, order)
        for court_key_name, searched_court in list(matched_case_dict.items()):
            child_case = self._make_cover_page_court_xml(search_name_xml, searched_court, court_key_name)
        client_id = order.client_id
        client_info = Client.objects.get(id=client_id)

        self._make_cover_page_client_xml(top, client_info)
        print((tostring(top)))
        pretty_xml = self._pretty_print_xml(top)
        # print(pretty_xml)
        # return pretty_xml
        return tostring(top)

    def make_coverpage_xml2(self, matched_case_dict, order):
        """
        Make an XML document containing data for cover page
        :param cases: one or more instances of case
        :return: XML document with human readable case data
        """
        # from pacerscraper.models import Client
        from orders.models import Client
        # assert isinstance(case_instance, Case), 'case_instance argument of wrong type!'
        top = self.top
        # for case_instance in cases:
        search_name = matched_case_dict.get('search_name','')
        assert(search_name != '')
        search_name_xml = self._make_search_name_xml(top, search_name, order)
        for court_key_name, searched_court in list(matched_case_dict.items()):
            child_case = self._make_cover_page_court_xml(search_name_xml, searched_court, court_key_name)
        client_id = order.client_id
        client_info = Client.objects.get(id=client_id)

        self._make_cover_page_client_xml(top, client_info)
        print((tostring(top)))
        pretty_xml = self._pretty_print_xml(top)
        # print(pretty_xml)
        # return pretty_xml
        return tostring(top)

    def make_coverpage_xml3(self, name_search_results_dict, order, highvalue=False):
        """
        Make an XML document containing data for cover page
        :param name_search_results_dict: dict of names searched with value as a list of courts where the name matched
        :param order: orders.model.Order associated with name_search_results_dict
        :param highvalue: if this is a high value judgment search add the number of HV matches
        :return: XML document with human readable case data
        """
        # from pacerscraper.models import Client
        from orders.models import Client
        # assert isinstance(case_instance, Case), 'case_instance argument of wrong type!'
        top = self.top
        for search_name, courts_list in name_search_results_dict.items():
            search_name_element = self._make_search_name_xml2(order, top, search_name, courts_list)

            if highvalue:  # add an xml element for high value searches
                hv_count = 0
                generated_reports = order.generatedreport_set.order_by('-id')
                if (len(generated_reports) > 0):
                    generated_report = generated_reports[0]
                    hv_count = generated_report.num_state_hv_matches
                high_value_matches_xml = SubElement(search_name_element, 'COURT_MATCH')
                high_value_matches_xml.text = 'HV-' + str(hv_count)

        client_id = order.client_id
        client_info = Client.objects.get(id=client_id)


        self._make_cover_page_client_xml(top, client_info, order)
        print("********* Here is the new cover page xml document *********")
        print((tostring(top)))
        return tostring(top)

    def _print_debt_instance(self, debt_instance):
        """
        Generate and print some high level info for a debt instance
        :param debt_instance:
        :return:
        """
        assert isinstance(debt_instance, Debt)
        print('------')
        # print(debt_instance)
        print(('judgment number: ' + debt_instance.docketed_judgment_number))
        print(('entered date: ' + debt_instance.entered_date))

        print(('party orig amt: ' + debt_instance.party_orig_amt))
        print(('comments: ' + debt_instance.debt_comments))
        print('------')

    def _pretty_print_xml(self, elem):
        """
        Return a human readable XML document
        :param elem: an xml.etree.ElementTree Element
        :return: string with beautified XML document
        """
        from xml.etree import ElementTree
        from xml.dom import minidom
        assert isinstance(elem, Element), 'An xml element was supplied for pretty printing!'
        rough_string = ElementTree.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent='  ')

    def dump_xml_to_file(self, xml_doc, xml_filename):
        """
        Write the generated XML document to a file in the media folder
        :param xml_doc: xml docstring to write to file
        :param xml_filename: the name the xml file should have in the target directory
        :return: relative pathname of the file created on the disk
        """
        import os
        xml_fullpath = os.path.join('.', 'jsnetwork_project', 'media', xml_filename)
        xml_file = open(xml_fullpath, 'w')
        xml_file.write(xml_doc)
        xml_file.close()
        return xml_fullpath

    def _map_civil_venue_code(self, d_code, code_type):
        """
        Translate various codes from database into long-form text for printing
        :param d_code: the code to lookup from the CSV
        :param code_type: One of SpecCodes Enum
        :return:
        """
        #  @TODO: make lookup tables a static design pattern for performance
        import csv
        import os

        code_not_found_msg = 'Not provided'

        desc_col_num = 2
        if code_type == SpecCodes.VENUE:
            d_code_filename = 'venue-codes.csv'  # make sure this is a windows-formatted csv file
            desc_col_num = 1
            # print('-------------> Using code {} to lookup venue code'.format(d_code))
        elif code_type == SpecCodes.CIVIL:
            d_code_filename = 'civil-case-type-codes.csv'  # make sure this is a windows-formatted csv file
            # print('-------------> Using code {} to lookup civil code'.format(d_code))

        d_code_fullpath = os.path.join('.', 'jsnetwork_project', 'media', d_code_filename)
        # print("Opening file at: {}".format(d_code_fullpath))
        with open(d_code_fullpath, 'rU') as infile:
            reader = csv.reader(infile)
            code_dict = {rows[0].replace('\xef\xbb\xbf',''): rows[desc_col_num] for rows in reader}
        # print("Constructed code dictionary: {}".format(code_dict))
        matched_code =  code_dict.get(d_code, code_not_found_msg.format(d_code))
        # print('Matched code: {}'.format(matched_code))
        return matched_code


        # def _map_data_code(self, d_code, code_type):
        #     import csv
        #     import os
        #
        #     d_code_fullpath = os.path.join('.', 'jsnetwork_project', 'media', d_code_filename)
        #     with open(d_code_fullpath, 'r') as infile:
        #         reader = csv.reader(infile)
        #         # reader = csv.reader(open(infile, 'rU'), dialect=csv.excel_tab)
        #         self._ccode_dict = {rows[0]: rows[2] for rows in reader}
        #     return self._ccode_dict.get(ccode, 'Code {} Not Found'.format(ccode))

    def _find_missing_judgment_dockets(self, searchname):
        """
        Search missing judgment data for a search name. Exact match only.
        :param searchname: a searchname object containing a first_name and last_name
        :return: list of judgment numbers matching the searchname in XX-XXXXXX-XX format
        """
        from statereport.models import MissingJudgmentDebtSummary
        first_name = searchname.first_name
        last_name = searchname.last_name
        qs = MissingJudgmentDebtSummary.objects.filter(Name__icontains=first_name).filter(Name__icontains=last_name)

        judgment_nums = []
        for r in qs:
            judgment_nums.append(r.JudgmentNum)
        return judgment_nums

    def _missing_judgment_cases_from_judgment_nums(self, missing_judgment_nums):
        """
        Build a list of case objects from missing a list of judgment numbers
        :param missing_judgment_nums:
        :return:
        """

        def map_missing_judgment_to_case(missing_judgment_case):
            from statereport.models import Case
            c = Case()
            c.docketed_judgment_seq_num = missing_judgment_case.JudgmentNum
            c.case_filed_date = missing_judgment_case.JudgmentEnterDate
            c.case_type_code = ''
            c.acms_venue_id = missing_judgment_case.VenueId
            return c

        def map_missing_party_debt_to_case(case, missing_judgment_party_summary):
            from statereport.models import Debt
            d = Debt()
            d.party_due_amt = missing_judgment_party_summary.DebtAmount
            d.party_other_award_orig_amt = missing_judgment_party_summary.OtherAmount
            d.party_due_atty_fee_amt = missing_judgment_party_summary.AttorneyFee
            d.debt_status_code = missing_judgment_party_summary.DebtStatus
            case.debt_set.add(d)
            return d

        def map_missing_judgment_summary_to_case(case, missing_judgment_judgment_summary):
            from statereport.models import Party
            p = Party()
            p.party_role_type_code = missing_judgment_judgment_summary.Role
            last_name, first_name = missing_judgment_judgment_summary.PartyInformation.split(',')
            p.party_last_name = last_name
            p.party_first_name = first_name
            p.docketed_judgment_number = missing_judgment_judgment_summary.JudgmentNum
            p.party_street_name = missing_judgment_judgment_summary.Address1
            p.ptydebt_status_code = missing_judgment_judgment_summary.DebtStatus
            p.ptydebt_status_date = missing_judgment_judgment_summary.PartyDebtStatusDate
            return p

        from statereport.models import MissingJudgmentDetails, MissingJudgmentDebtSummary, MissingJudgmentParty, MissingJudgmentJudgmentSummary
        case_list = []
        for judgment_num in missing_judgment_nums:
            missing_judgment_case = MissingJudgmentDetails.objects.get(JudgmentNum=judgment_num)
            case = map_missing_judgment_to_case(missing_judgment_case)
            # missing_judgment_debt = MissingJudgmentDebtSummary.objects.get(JudgmentNum=judgment_num)
            # map_missing_debt_to_case(case, missing_judgment_debt)
            missing_judgment_party_summary = MissingJudgmentParty.objects.get(JudgmentNum=judgment_num)
            map_missing_party_debt_to_case(case, missing_judgment_party_summary)  # assign to set, process group of results in function

            missing_judgment_judgment_summary = MissingJudgmentJudgmentSummary.objects.get(JudgmentNum=judgment_num)
            map_missing_judgment_summary_to_case(case, missing_judgment_judgment_summary)

            case_list.append(case)



