
import os
import tempfile
from xml.dom.minicompat import NodeList
import zipfile
from lxml import etree
from docxtpl import DocxTemplate
from xml.dom import minidom
from datetime import date
from docx import Document
from copy import deepcopy

def parse_matches(document: Document, context):
    matches = []
    for match in context["SEARCH_MATCH"]:
        match_array = [m.firstChild.nodeValue if m.firstChild is not None else None for m in match]
        if(len(match_array) != 0):
            matches.append(" ".join(match_array))
        else:
            matches.append("Search For Above Name Has Come Back Clear")
    return matches
    
def parse_court_match(document: Document, context):
    matches = []
    for match in context["COURT_MATCHES"]:
        match_array = [m.firstChild.nodeValue if m.firstChild is not None else None for m in match]
        if len(match_array) != 0 and match_array[0] is not None:
            matches.append(" ".join(match_array))
        else:
            matches.append("***Name Clear***")
    return matches

def parse_judgements(document: Document, context):
    matches = []
    for match in context["COURT_MATCHES"]:
        match_array = [m.firstChild.nodeValue if m.firstChild is not None else None for m in match]
        if len(match_array) != 0 and match_array[0] is not None:
            matches.append("**With Judgements** ")
        else:
            matches.append("")
    return matches

def parse_search_type(document: Document, check, context):
    matches = []
    for type in context["SEARCH_TYPES"]:
        for subtype in type:
            if check == 'isState':
                matches.append("Superior Court:" if subtype == 'STATE_DOCKET_LIST' else '')
            elif check == 'isBankruptcy':
                matches.append("Bankruptcy:" if subtype == 'BANKRUPTCY_DOCKET_LIST' else '')
            elif check == 'isUSDC':
                matches.append("United States District Court:" if subtype == 'USDC_DOCKET_LIST' else '')
    return matches

def parse_docket_num(document: Document, context):
    matches = []
    for docket_results in context["DOCKET_NUMS"]:
        for docket_nums in docket_results:
            dns = []
            for docket_num in docket_nums:
                dns.append(f"{docket_num} _____")
            matches.append("\n".join(dns))
    return matches

def replace_context(document: Document, template_name, context):
    #Iterate SEARCH_NAME_ELEMENT and copy tables whenever necessary
    if 'SEARCH_NAME_ELEMENT' in context and context["SEARCH_NAME_ELEMENT"] > 1:
        copies = 0
        while copies < context["SEARCH_NAME_ELEMENT"] - 1:
            table_index = 0
            if template_name == 'CoverPage':
                table_index = 1
            table = document.tables[table_index]
            table.add_row()
            row_index = 2
            if template_name == 'PatriotReport':
                row_index = 3
            for row in table.rows:
                new_tr = deepcopy(row._tr)
                table.rows[row_index]._tr.addnext(new_tr)
                row_index += 1
                
            copies += 1
    #Replace matches in table
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    if p.text.startswith("[MATCHES}))>0"):
                        context["[MATCHES}))>0,True, False)][SEARCH_MATCH})][else]Search For Above Name Has Come Back Clear[:if]"] = parse_matches(document, context)
                    if p.text.startswith("  [ifWithJudg]"):
                        # context["[ifWithJudg]**With Judgments**[:if][ifWithJudg] [COURT_MATCH][courtMatch] [:foreach][else] ***Name Clear***[:if]"] = "***Name Clear***"
                        context["[ifWithJudg]**With Judgments**[:if]"] = parse_judgements(document, context)
                        context["[ifWithJudg] [COURT_MATCH][courtMatch] [:foreach][else] ***Name Clear***[:if]"] = parse_court_match(document, context) 
    
    #Iterate all paragraphs
    paragraphs = list(document.paragraphs)

    docket_paragraphs = []
    #Paragraphs in docket list
    p_index = 0
    copied_paragraphs = []
    for p in paragraphs:
        if 'N_SEARCH_RESULTS' in context and context['N_SEARCH_RESULTS'] > 0 and p_index >= 1 and p.text not in context.keys():
            docket_paragraphs.append(p)
            copies_para = 1
            while copies_para < context['N_SEARCH_RESULTS']:
                output_para = document.add_paragraph()
                for run in p.runs:
                    output_run = output_para.add_run(run.text)
                    # Run's bold data
                    output_run.bold = run.bold
                    # Run's italic data
                    output_run.italic = run.italic
                    # Run's underline data
                    output_run.underline = run.underline
                    # Run's color data
                    output_run.font.color.rgb = run.font.color.rgb
                    # Run's font data
                    output_run.font.name = run.font.name
                    # Run's style
                    output_run.style.name = run.style.name
                # Paragraph's alignment data
                output_para.paragraph_format.alignment = p.paragraph_format.alignment
                copied_paragraphs.append(output_para)
                copies_para += 1
        if 'N_CASES' in context and context['N_CASES'] > 0 and p.text not in context.keys():
            docket_paragraphs.append(p)
            copies_para = 1
            while copies_para < context['N_CASES']:
                output_para = document.add_paragraph()
                for run in p.runs:
                    output_run = output_para.add_run(run.text)
                    # Run's bold data
                    output_run.bold = run.bold
                    # Run's italic data
                    output_run.italic = run.italic
                    # Run's underline data
                    output_run.underline = run.underline
                    # Run's color data
                    output_run.font.color.rgb = run.font.color.rgb
                    # Run's font data
                    output_run.font.name = run.font.name
                    # Run's style
                    output_run.style.name = run.style.name
                # Paragraph's alignment data
                output_para.paragraph_format.alignment = p.paragraph_format.alignment
                copied_paragraphs.append(output_para)
                copies_para += 1
        p_index += 1
    
    docket_paragraphs += copied_paragraphs
    
    if template_name == 'DocketReport':    
        for i in range(len(docket_paragraphs)):
            print(docket_paragraphs[i].text)
            search_type_paragraphs = []
            paragraphs.append(docket_paragraphs[i])
            copies = 0
            while copies < len(context["SEARCH_TYPES"][copies]) - 1:
                if '[isState]' in docket_paragraphs[i].text or '[DOCKET_NUM]' in docket_paragraphs[i].text:
                    output_para = deepcopy(docket_paragraphs[i])
                    docket_paragraphs[i + 2]._p.addnext(output_para._p)
                    search_type_paragraphs.append(output_para)
                copies += 1
            paragraphs += search_type_paragraphs
            
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    print(p.text)
                    paragraphs.append(p)
    
    header = document.sections[0].header
    for t in header.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    print(p.text)
                    paragraphs.append(p)
    for p in header.paragraphs:
        print(p.text)
        paragraphs.append(p)
    
    if template_name == 'DocketReport':
        context["[isState]Superior Court:[:if]"] = parse_search_type(document, 'isState', context)
        context["[isBankruptcy]Bankruptcy:[:if]"] = parse_search_type(document, 'isBankruptcy', context)
        context["[isUSDC]United States District Court:[:if]"] = parse_search_type(document, 'isUSDC', context)
        context["[DOCKET_NUM][${varDocketNum}] _____"] = parse_docket_num(document, context)
   
    for key, value in context.items():
        j = 0
        for p in paragraphs:
            if key in p.text and type(value) is str:
                runs = p.runs
                started = False
                key_index = 0
                found_runs = list()
                found_all = False
                replace_done = False
                for i in range(len(runs)):
                    # case 1: Found in a single run
                    if key in runs[i].text and not started:
                        found_runs.append((i, runs[i].text.find(key), len(key)))
                        text = runs[i].text.replace(key, value)
                        runs[i].text = text
                        replace_done = True
                        found_all = True
                        break
                    
                    if key[key_index] not in runs[i].text and not started:
                        continue
                    
                    # case 2: Search for partial text, find first run
                    if key[key_index] in runs[i].text and runs[i].text[-1] in key and not started:
                        start_index = runs[i].text.find(key[key_index])
                        check_length = len(runs[i].text)
                        for text_index in range(start_index, check_length):
                            if runs[i].text[text_index] != key[key_index]:
                                break
                        if key_index == 0:
                            started = True
                        chars_found = check_length - start_index
                        key_index += chars_found
                        found_runs.append((i, start_index, chars_found))
                        if key_index != len(key):
                            continue
                        else:
                            found_all = True
                            break
                        
                    # case 2: Search for partial text, find subsequent run
                    if key[key_index] in runs[i].text and started and not found_all:
                        chars_found = 0
                        check_length = len(runs[i].text)
                        for text_index in range(0, check_length):
                            if runs[i].text[text_index] == key[key_index]:
                                key_index += 1
                                chars_found += 1
                            else:
                                break
                        found_runs.append((i, 0, chars_found))
                        if key_index == len(key):
                            found_all = True
                            break
                    
                if found_all and not replace_done:
                    for i, item in enumerate(found_runs):
                        index, start, length = [t for t in item]
                        if i == 0:
                            text = runs[index].text.replace(runs[index].text[start : start + length], value)
                            runs[index].text = text
                        else:
                            text = runs[index].text.replace(runs[index].text[start : start + length], '')
                            runs[index].text = text
            elif key in p.text and type(value) is list and type(value[0]) is str:
                runs = p.runs
                started = False
                key_index = 0
                found_runs = list()
                found_all = False
                replace_done = False
                for i in range(len(runs)):
                    if len(runs[i].text) > 0:
                        # case 1: Found in a single run
                        if key == runs[i].text and started == False:
                            found_runs.append((i, runs[i].text.find(key), len(key)))
                            text = runs[i].text.replace(key, value[j])
                            runs[i].text = text
                            replace_done = True
                            found_all = True
                            break
                        if key[key_index] not in runs[i].text and not started:
                            continue
                        
                        # case 2: Search for partial text, find first run
                        if key[key_index] in runs[i].text and runs[i].text[-1] in key and not started:
                            start_index = runs[i].text.find(key[key_index])
                            check_length = len(runs[i].text)
                            for text_index in range(start_index, check_length):
                                if runs[i].text[text_index] != key[key_index]:
                                    break
                            if key_index == 0:
                                started = True
                            chars_found = check_length - start_index
                            key_index += chars_found
                            found_runs.append((i, start_index, chars_found))
                            
                            if key_index != len(key):
                                continue
                            else:
                                found_all = True
                                break
                            
                        # case 2: Search for partial text, find subsequent run
                        if key[key_index] in runs[i].text and started and not found_all:
                            start_index = runs[i].text.find(key[key_index])
                            chars_found = 0
                            check_length = len(runs[i].text)
                            for text_index in range(0, check_length):
                                if runs[i].text[text_index] == key[key_index]:
                                    key_index += 1
                                    chars_found += 1
                                else:
                                    break
                            found_runs.append((i, start_index, chars_found))
                            if key_index == len(key):
                                found_all = True
                                break
                      
                if found_all and not replace_done:
                    for i, item in enumerate(found_runs):
                        index, start, length = [t for t in item]
                        if i == 0:
                            text = runs[index].text.replace(runs[index].text[start : start + length], value[j], 1)
                            runs[index].text = text
                        else:
                            text = runs[index].text.replace(runs[index].text[start : start + length], '', 1)
                            runs[index].text = text
                    j += 1
                        
            
def replace_patriot(uri, xml_data: minidom.Document):
    client_ref_num = xml_data.getElementsByTagName('CLIENT_REF_NUM')[0].firstChild.nodeValue
    search_to = xml_data.getElementsByTagName('SEARCH_TO')[0].firstChild.nodeValue
    search_name_element = xml_data.getElementsByTagName('SEARCH_NAME_ELEMENT')
    matches = []
    searched_names = []
    search_matches = []
    for i in range(0, len(search_name_element)):
        match = search_name_element[i].getElementsByTagName('MATCHES')[0].childNodes
        searched_name = search_name_element[i].getElementsByTagName('SEARCHED_NAME')[0].firstChild.nodeValue
        search_match = search_name_element[i].getElementsByTagName('SEARCH_MATCH')
        matches.append(match)
        searched_names.append(searched_name)
        search_matches.append(search_match)
    context = {
        '[CLIENT_REF_NUM]': client_ref_num,  
        "[SEARCH_TO]": search_to, 
        'MATCHES': matches, 
        'SEARCH_MATCH': search_matches,
        '[SEARCHED_NAME})]': searched_names, 
        'SEARCH_NAME_ELEMENT': len(search_name_element), 
        "[SEARCH_NAME_ELEMENT]": '', 
        '[:forEach]': '',
    }    
    document = Document(uri)
    replace_context(document, 'PatriotReport', context)
    document.save(os.path.join(".",'jsnetwork_project','media',f'generated_PatriotReport.docx'))
    
def replace_coverpage(uri, xml_data: minidom.Document):
    client_file_num = xml_data.getElementsByTagName('CLIENT_FILE_NUM')[0].firstChild.nodeValue
    name = xml_data.getElementsByTagName('NAME')[0].firstChild.nodeValue
    address = xml_data.getElementsByTagName('ADDRESS')[0].firstChild.nodeValue
    city_state_zip = xml_data.getElementsByTagName('CITY_STATE_ZIP')[0].firstChild.nodeValue
    search_name_element = xml_data.getElementsByTagName('SEARCH_NAME_ELEMENT')
    court_matches = []
    search_names = []
    search_froms = []
    search_tos = []
    for i in range(0, len(search_name_element)):
        search_name = search_name_element[i].getElementsByTagName('SEARCH_NAME')[0].firstChild.nodeValue
        court_match = [court for court in search_name_element[i].getElementsByTagName('COURT_MATCH')]
        search_to = search_name_element[i].getElementsByTagName('SEARCH_TO')[0].firstChild.nodeValue
        search_from = search_name_element[i].getElementsByTagName('SEARCH_FROM')[0].firstChild.nodeValue
        search_names.append(search_name)
        court_matches.append(court_match)
        search_tos.append(search_to)
        search_froms.append(search_from)
    now = date.today().strftime('%m/%d/%Y')
    context = {
        '[CLIENT_FILE_NUM]': client_file_num, 
        "[NAME]": name, 
        "[ADDRESS]": address, 
        "[CITY_STATE_ZIP]": city_state_zip, 
        "[SEARCH_NAME]": search_names, 
        "[SEARCH_FROM]": search_froms, 
        "[SEARCH_TO]": search_tos, 
        "[=NOW()]": now, 
        "COURT_MATCHES": court_matches,
        "SEARCH_NAME_ELEMENT": len(search_name_element),
        "[SEARCH_NAME_ELEMENT]": '', 
        '[:forEach]': '',
    }    
    document = Document(uri)
    replace_context(document, 'CoverPage', context)
    document.save(os.path.join(".",'jsnetwork_project','media',f'generated_CoverPage.docx'))
    
def replace_docketreport(uri, xml_data: minidom.Document):
    search_results = xml_data.getElementsByTagName('SEARCH_RESULTS')
    search_result = []
    search_names = []
    search_type_names_all = []
    docket_nums_all = []
    for i in range(0, len(search_results)):
        search_name = search_results[i].getElementsByTagName('SEARCH_NAME')[0].firstChild.nodeValue
        search_type_nodes = search_results[i].getElementsByTagName('SEARCH_TYPE')
        search_type_names = []
        docket_nums_result = []
        for j in range(0, len(search_type_nodes)):
            search_type_name = search_type_nodes[j].getElementsByTagName('SEARCH_TYPE_NAME')[0].firstChild.nodeValue
            docket_num_nodes = search_type_nodes[j].getElementsByTagName('DOCKET_RESULTS')[0].childNodes
            docket_nums = []
            for docket_num_node in docket_num_nodes:
                if(type(docket_num_node) is minidom.Element):
                    docket_num = docket_num_node.firstChild.nodeValue
                    docket_nums.append(docket_num)
            search_type_names.append(search_type_name)
            docket_nums_result.append(docket_nums)
        search_type_names_all.append(search_type_names)
        docket_nums_all.append(docket_nums_result) 
        search_names.append(search_name)
        search_result.append("")
    context = { 
        "N_SEARCH_RESULTS": len(search_results),
        "[SEARCH_RESULTS]": '',
        "[SEARCH_NAME]": search_names,
        "[SEARCH_TYPE]": "",
        "DOCKET_NUMS": docket_nums_all,
        "SEARCH_TYPES": search_type_names_all,
        "[endSearchType]": "", 
        "[endSearchResults]": "", 
        "[endDocketNum]": "",
    }
    document = Document(uri)
    replace_context(document, 'DocketReport', context)
    document.save(os.path.join(".",'jsnetwork_project','media',f'generated_DocketReport.docx'))
    
def replace_usdc(uri, xml_data: minidom.Document):
    client_ref_num = xml_data.getElementsByTagName('CLIENT_REF_NUM')[0].firstChild.nodeValue
    cases = xml_data.getElementsByTagName('case')
    searchnames = []
    usdc_case_numbers = []
    dates_filed = []
    creditors = []
    debtors = []
    attorneys = []
    trustees = []
    dates_discharged = []
    dates_terminated = []
    for i in range(0, len(cases)):
        searchname = cases[i].getElementsByTagName('SEARCHNAME')[0].firstChild.nodeValue
        searchnames.append(searchname)
        usdc_case_number = cases[i].getElementsByTagName('USDC_CASE_NUMBER')[0].firstChild.nodeValue
        usdc_case_numbers.append(usdc_case_number)
        date_filed = cases[i].getElementsByTagName('DATE_FILED')[0].firstChild.nodeValue
        dates_filed.append(date_filed)
        parties = cases[i].getElementsByTagName('PARTIES')
        creditor = cases[i].getElementsByTagName('CREDITOR')[0].firstChild.nodeValue
        creditors.append(creditor)
        debtor = cases[i].getElementsByTagName('DEBTOR')[0].firstChild.nodeValue
        debtors.append(debtor)
        attorney = cases[i].getElementsByTagName('ATTORNEY')[0].firstChild.nodeValue
        attorneys.append(attorney)
        trustee = cases[i].getElementsByTagName('TRUSTEE')[0].firstChild.nodeValue
        trustees.append(trustee)
        date_discharged = cases[i].getElementsByTagName('DATE_DISCHARGED')[0].firstChild.nodeValue
        dates_discharged.append(date_discharged)
        date_terminated = cases[i].getElementsByTagName('DATE_TERMINATED')[0].firstChild.nodeValue
        dates_terminated.append(date_terminated)
        
    context = {
        "N_CASES": len(cases),
        "[case]": '',
        "[PARTIES]": '',
        "[CLIENT_REF_NUM]": client_ref_num,
        "[USDC_CASE_NUMBER]": usdc_case_numbers,
        "[DATE_FILED]": dates_filed,
        "[CREDITOR]": creditors,
        "[DEBTOR]": debtors,
        "[ATTORNEY]": attorneys,
        "[TRUSTEE]": trustees,
        "[DATE_DISCHARGED]": dates_discharged,
        "[DATE_TERMINATED]": dates_terminated,
        "[:forEach]": ''
    }
    document = Document(uri)
    replace_context(document, 'UsdcReport', context)
    document.save(os.path.join(".",'jsnetwork_project','media',f'generated_UsdcReport.docx'))
    
    
# doc_uri = os.path.join(".", "jsnetwork_project", 'media', 'USDC Template.docx')
# xml = open(os.path.join(".", "jsnetwork_project", "media", "alejandro usdc.xml"), 'rb')
# xml_data_str = xml.read().decode("utf-8")
# xml_data = minidom.parseString(xml_data_str)
# replace_usdc(doc_uri, xml_data)
# replace_docketreport(doc_uri, xml_data)
# replace_coverpage(doc_uri, xml_data)
# replace_patriot(doc_uri, xml_data)