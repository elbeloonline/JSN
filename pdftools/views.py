# -*- coding: utf-8 -*-


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import base64
from docx import Document
from xml.dom import minidom
import re, os
import sys
import subprocess

from pdftools.helpers import replace_coverpage, replace_docketreport, replace_patriot, replace_usdc, replace_bankruptcy, replace_state

# Create your views here.
@login_required
def results_comparison(request, order_id):
    context = {
        'order_id': order_id
    }
    return render(request, 'orders/results_comparison.html', context)


@login_required
def cj_comparison(request):
    from .utils import JudgmentsExtractor
    return JudgmentsExtractor.cj_pdf_comparison(request)

@csrf_exempt
def make_pdf(request):
    if request.method == 'POST':
        request_body = json.loads(request.body.decode("utf-8"))
        uri = request_body['Uri']
        data_source = request_body['Datasources'][0]
        template_name = data_source["Name"]
        namesearch_data = base64.b64decode(data_source['Data'])
        xml_data = minidom.parseString(namesearch_data)
        
        if template_name == 'PatriotReport':
            replace_patriot(uri, xml_data)
        elif template_name == 'CoverPage':
            replace_coverpage(uri, xml_data)
        elif template_name == 'DocketReport':
            replace_docketreport(uri, xml_data)
        elif template_name == 'UsdcReport':
            replace_usdc(uri, xml_data)
        elif template_name == 'BankruptcyReport':
            replace_bankruptcy(uri, xml_data)
        elif template_name == 'CaseReport':
            replace_state(uri, xml_data)

        
        # Convert word to pdf. Requires installing LibreOffice and adding the directory to PATH
        subprocess.run([
            'soffice', 
            '--headless', 
            '--convert-to', 
            'pdf', 
            '--outdir', 
            os.path.join('.', 'jsnetwork_project', 'media'), 
            os.path.join('.', 'jsnetwork_project', 'media', f'generated_{template_name}.docx')
        ])
            
        pdf_file = open(os.path.join('.', 'jsnetwork_project', 'media', f'generated_{template_name}.pdf'), 'rb')
        base64_data = base64.b64encode(pdf_file.read()).decode("utf-8")
        
        return JsonResponse({'Data': base64_data})
    else:
        pass
    
@csrf_exempt
def pdf_version(request):
    if request.method == 'POST':
        context = {
            'order_id': 1
        }
        return JsonResponse({'ServiceVersion': '1.0', 'EngineVersion': '1.0'})
    else:
        pass
