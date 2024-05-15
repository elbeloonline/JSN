

import base64
from datetime import datetime
import logging

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.views.decorators.csrf import csrf_exempt
from .models import Order, Client
from .forms import SearchNameForm, OrderForm, ClientForm, QuickSearchForm
from .utils import OrderUtils
from xml.dom import minidom
from pdftools.helpers import replace_coverpage, replace_docketreport, replace_patriot, replace_usdc, replace_bankruptcy


@login_required
def index(request):
    """
    The main page returned when the user logs into the system
    :param request: the request object
    :return: django render object
    """
    current_user = request.user
    context = OrderUtils.list_latest_orders(current_user)
    return render(request, 'orders/index.html', context)

@login_required
def order_new(request):
    """
    View for requesting the creation of a new order
    :param request: the request object
    :return: django render object
    """
    from .utils import OrderUtils

    logger = logging.getLogger(__name__)
    NameSearchFormSet = formset_factory(SearchNameForm, extra=0)
    todays_date = datetime.today()
    # date_format_string = '%-m/%-d/%Y'
    date_format_string = '%Y-%m-%d'
    two_decades_prior = todays_date.replace(year=todays_date.year - 20).strftime(date_format_string)

    form_client = None
    if request.method == "POST":
        namesearch_formset = NameSearchFormSet(request.POST)
        form_client = ClientForm(request.POST, prefix="form_client")
        form_client.is_valid()
        form_client.initial = {'client_name' :form_client.cleaned_data['client_name'].id}
        form_order = OrderForm(request.POST, prefix="form_order")

        logger.info('getting ready to validate form_order')
        if not form_client.is_valid():
            messages.error(request, 'A valid client is required for this order.')
        if form_client.is_valid() and form_order.is_valid(): # and form_search_name.is_valid():
            first_searchname_form = namesearch_formset[0]
            if first_searchname_form.is_valid():
                selected_client_id = form_client.cleaned_data['client_name'].id
                client = Client.objects.get(id=selected_client_id)
                order = form_order.save(commit=False)
                order.client = client
                order.save()
                for namesearch_form in namesearch_formset:
                    logger.info('getting ready to validate namesearch_form')
                    if namesearch_form.is_valid():
                        # avoiding addition of empty names to search which cause errors later
                        if (not namesearch_form.cleaned_data['first_name'] == '' and \
                            not namesearch_form.cleaned_data['last_name'] == '') or \
                            (not namesearch_form.cleaned_data['company_name'] == ''):
                            search_name = namesearch_form.save(commit=False)
                            search_name.order = order
                            search_name.save()
                            # messages.success(request, 'Name submission successful')
                current_user = request.user
                if current_user.is_superuser:  # admins see the order screen to generate partial reports for testing
                    context = OrderUtils.list_latest_orders(current_user)
                    return render(request, 'orders/index.html', context)
                else:
                    return run_search(request, order_id=order.id, report_type='full')
            else:
                messages.error(request, 'Submission was missing a valid name')
    else:
        form_order = OrderForm(prefix="form_order")
        namesearch_formset = NameSearchFormSet(initial=[
            {'search_from': two_decades_prior,
             'search_to': datetime.today().strftime(date_format_string)}
        ])
    # get user's available client list
    if not form_client:
        form_client = ClientForm(prefix="form_client")
    current_user = request.user
    if not request.user.is_superuser:
        client_id_queryset = OrderUtils.get_user_client_ids(current_user)

        client_id_queryset = client_id_queryset.values('client_id')
        client_ids = [str(u['client_id']) for u in client_id_queryset]

        # form_client.client_options = Client.objects.filter(id__in=client_ids).order_by('client_name')
        form_client.fields['client_name'].queryset = Client.objects.filter(id__in=client_ids).order_by('client_name')
    else:
        form_client.client_options = Client.objects.all().order_by('client_name')

    # send user to form, new or with error messages
    context = {
        'form_client': form_client,
        'form_order': form_order,
        'formset_search_name': namesearch_formset,
        'two_decades_prior': two_decades_prior,
        'todays_date': todays_date.strftime(date_format_string)
    }
    return render(request, 'orders/order_edit_new.html', context)

# @login_required
def _pdf_view(request, pdf_filename):
    """
    Generate a pdf and display in the user's browser
    :param request:
    :param pdf_filename: name of the PDF file on the disk
    :return: a buffered view of the PDF (buffered, not completely loaded in memory at once)
    """
    import logging
    import os

    from django.http import FileResponse, Http404
    from django.conf import settings

    from orders.models import Order, GeneratedReport

    pdf_filename = os.path.join(settings.MEDIA_ROOT, 'generatedpdfs', pdf_filename)
    logger = logging.getLogger(__name__)
    logger.info('Sending PDF file to browser for download')
    logger.info('PDF file path is {}'.format(pdf_filename))
    try:
        assert(os.path.isfile(pdf_filename))
        response = FileResponse(open(pdf_filename, 'rb'), content_type='application/pdf')

        user_pdf_filename = "search_report.pdf"
        pdf_split_filename = pdf_filename.split(os.sep)[-1]
        gr = GeneratedReport.objects.filter(merged_report_filename=pdf_split_filename).first()
        if gr:
            order_id = gr.order_id
            order = Order.objects.get(id=order_id)
            if order.internal_tracking_num:
                user_pdf_filename = order.internal_tracking_num
            else:
                user_pdf_filename = order.title_number # title num = client num
            user_pdf_filename = user_pdf_filename + '.pdf'

        response['Content-Disposition'] = 'attachment; filename={title}'.format(title=user_pdf_filename)
        return response
    except: #  FileNotFoundError:
        raise Http404()


@login_required
def _csv_xlsx_view(request, order_id, high_value):
    """
    Generate a pdf and display in the user's browser
    :param request:
    :param pdf_filename: name of the XLSX file on the disk
    :param high_value: return the high value report if true
    :return: a buffered view of the PDF (buffered, not completely loaded in memory at once)
    """
    import logging
    import os

    from django.http import FileResponse, Http404
    from django.conf import settings

    from orders.models import Order

    csv_filename_base = "{}-{}".format(Order.objects.get(id=order_id).title_number, order_id)
    csv_filename = os.path.join(settings.MEDIA_ROOT, csv_filename_base) + '.csv'
    if high_value:
        csv_filename = os.path.join(settings.MEDIA_ROOT, csv_filename_base) + '-hv.csv'

    if not os.path.isfile(csv_filename):
        csv_filename = csv_filename.replace('.csv', '.xlsx')

    logger = logging.getLogger(__name__)
    logger.info('Sending excel file to browser for download')
    logger.info('Excel file path is {}'.format(csv_filename))
    try:
        assert(os.path.isfile(csv_filename))
        if csv_filename.endswith('csv'):
            response = FileResponse(open(csv_filename, 'rb'), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename={title}'.format(title=csv_filename_base+'.csv')
        else:
            response = FileResponse(open(csv_filename, 'rb'), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            if not high_value:
                logger.info('Linking to regular report')
                response['Content-Disposition'] = 'attachment; filename={title}'.format(title=csv_filename_base + '.xlsx')
            else:
                logger.info('Linking to high value report')
                response['Content-Disposition'] = 'attachment; filename={title}'.format(title=csv_filename_base + '-hv.xlsx')
        return response
    except: #  FileNotFoundError:
        if not high_value:
            logger.error('Could not locate file: {}'.format(csv_filename_base + '.xlsx'))
        else:
            logger.error('Could not locate high value file: {}'.format(csv_filename_base + '-hv.xlsx'))
        raise Http404()

@login_required
def view_report(request, filename):
    """
    Method for accessing internal function to view a pdf report
    :param request: request object
    :param filename: the filename of the pdf to fetch and return
    :return:
    """
    return _pdf_view(request, filename)

@login_required
def csv_report(request, order_id):
    """
    Method for accessing internal function to view a csv/xlsx file
    :param request: the request object
    :param order_id: id of the order to use for fetching the xlsx file
    :return:
    """
    return _csv_xlsx_view(request, order_id, False)

@login_required
def csv_report_high_value(request, order_id):
    """
    Method for accessing internal function to view a csv/xlsx file
    :param request: the request object
    :param order_id: id of the order to use for fetching the xlsx file
    :return:
    """
    return _csv_xlsx_view(request, order_id, True)

@login_required
def merge_and_view_pdf(request, order_id, report_type):
    """
    Unused. View for returning a merged PDF file for the final report
    :param request: the request object
    :param order_id: the id of the order to proess
    :return: django render object
    """
    from nameviewer.pdfutils import PdfMerger
    print("Entered merge routine.")
    doc_merger = PdfMerger()
    merged_report_name = doc_merger.merge_reports_by_type(order_id, report_type)
    return _pdf_view(request, merged_report_name, order_id)

@login_required
def reorder(request, order_id):
    """
    Make a new order cloning the old one but mark as a reorder for billing purposes.
    These are effectively continuations
    :param request:
    :param order_id: id of the order to clone for the reorder
    :return:
    """
    import logging
    from .models import Order
    from nameviewer.windward import ReportTypes

    # schedule report generation in queue
    logger = logging.getLogger(__name__)
    logger.info('Queuing task for reorder...')
    prev_order = Order.objects.get(id=order_id)
    search_names = prev_order.searchname_set.all()

    # clone order
    new_order = prev_order
    new_order.id = None
    new_order.is_reorder = True
    new_order.save()
    logger.info('New order id for reorder is: {}'.format(new_order.id))

    # clone search names associated with original order
    for search_name in search_names:
        logger.debug("Processing search name {}".format(search_name))
        search_name.id = None
        search_name.order_id = new_order.id
        search_name.save()

    report_type = ReportTypes.FULL
    return run_search(request, new_order.id, report_type)

@login_required
def quick_order(request):
    """
    Allow a report to be generated using the order form with a single entry minus the client box
    :param request: the request object
    :return:
    """
    import logging

    from orders.models import SearchName
    from statereport.models import StateReportQueryManager
    from nameviewer.windward import ReportFactory

    logger = logging.getLogger(__name__)
    NameSearchFormSet = formset_factory(SearchNameForm, extra=0)
    todays_date = datetime.today()
    date_format_string = '%-m/%-d/%Y'
    two_decades_prior = todays_date.replace(year=todays_date.year - 20).strftime(date_format_string)

    if request.method == "POST":
        namesearch_formset = NameSearchFormSet(request.POST)
        form_client = ClientForm(request.POST, prefix="form_client")
        form_order = OrderForm(request.POST, prefix="form_order")
        namesearch_form = namesearch_formset[0]
        if namesearch_form.is_valid():
            logger.warning('Ok.')
            seq_num = request.POST['form-0-judgment_number_seq']

            searchname = SearchName()
            searchname.first_name = namesearch_form.cleaned_data['first_name'].upper()
            searchname.last_name = namesearch_form.cleaned_data['last_name'].upper()
            cases = StateReportQueryManager.query_database_by_searchname_details(searchname, True, seq_num)
            logger.warning('Number of cases found: {}'.format(len(cases)))

            order = Order.objects.last()  # need to supply a dummy order to the report
            report_generator = ReportFactory()
            report_name = report_generator.gen_windward_state_report(cases, order, "NoName Quick Order")

            return _pdf_view(request, report_name) # @TODOL: not at ALL safe while multiple sessions are active
            # return HttpResponse("order created.")
    else:
        form_client = ClientForm(prefix="form_client")
        form_order = OrderForm(prefix="form_order")
        namesearch_formset = NameSearchFormSet(initial=[
            {'search_from': two_decades_prior,
             'search_to': datetime.today().strftime(date_format_string)}
        ])
    # send user to form, new or with error messages
    context = {
        'form_client': form_client,
        'form_order': form_order,
        'formset_search_name': namesearch_formset,
        'two_decades_prior': two_decades_prior,
        'todays_date': todays_date.strftime(date_format_string)
    }
    return render(request, 'orders/quick_order_edit.html', context)



@login_required
def detail(request, order_id):
    """
    Fetch some details like the names used for a previously placed order
    :param request: the request object
    :param order_id: the order id to query against
    :return:
    """
    from .utils import OrderUtils
    order = get_object_or_404(Order, pk=order_id)
    names = OrderUtils.get_names_from_order(order)
    context = {
        'search_names': names,
        'title_number': order.title_number,
        'internal_tracking_num': order.internal_tracking_num,
        'created': order.created,
        'order_id': order_id,
        'is_reorder': order.is_reorder,
    }
    return render(request, 'orders/detail.html', context)

@login_required
def quick_search(request):
    """
    Allow a logged in user to perform a full judgment search without having to create an order.
    Meant for demo/validation purposes but could be used in production.

    :param request: contains anything submitted by the user via the form
    :return:
    """

    debug_message = ''
    cases = []
    form = QuickSearchForm(request.GET)
    if form.is_valid():
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        debug_message = 'Name submitted: {} {}'.format(first_name, last_name)

        # do name search
        from statereport.models import StateReportQueryManager
        from orders.models import SearchName
        searchname = SearchName()
        searchname.first_name = first_name
        searchname.last_name = last_name
        cases = StateReportQueryManager.query_database_by_searchname_details(searchname, use_namelist_db=True)
        num_cases = len(cases)
        debug_message = 'Number of cases found: {}'.format(num_cases)

    form = QuickSearchForm()
    context = {
        'search_form': form,
        'matched_cases': cases,
        'debug_message': debug_message,
    }
    return render(request, 'orders/quick_search.html', context)

@login_required
def run_search(request, order_id, report_type):
    """
    This method is meant to run a full search for all 3 databases
    :param request:
    :param order_id:
    :return:
    """
    import logging
    from . import tasks

    # schedule report generation in queue
    logger = logging.getLogger(__name__)
    logger.info('Queuing task...')
    tasks.process_report(order_id, report_type)

    return redirect('/orders/order_status/{}/{}'.format(order_id, report_type))

@login_required
def order_status(request, order_id, report_type):
    """
    Determine the search status of an order based on its id
    :param request: the request object
    :param order_id: the id of the order to process
    :param report_type: the type of report that is of interest
    :return:
    """
    is_order_complete = OrderUtils.check_search_status(order_id, report_type)
    context = {
        'order_id': order_id,
        'order_processing_is_complete' : is_order_complete,
    }
    return render(request, 'orders/generating_report.html', context)


@login_required
def settings(request):
    """
    Let a user customize some options for their session.
    Right now, only the scoring function can be overridden.
    :param request: contains anything submitted by the user via the form
    :return:
    """
    from django.conf import settings
    from .forms import SessionSettingsForm
    debug_message = ''
    name_match_session_varname = 'name_match_score'

    form = SessionSettingsForm(request.GET)

    if form.is_valid():
        name_match_score = form.cleaned_data['name_match_score']
        request.session[name_match_session_varname] = name_match_score
        # debug_message = 'Name submitted: {} {}'.format(first_name, last_name)
    else:
        if name_match_session_varname not in request.session:
            request.session[name_match_session_varname] = settings.NAME_MATCH_SCORE_DEFAULT
    name_match_score = request.session[name_match_session_varname]
    form = SessionSettingsForm(initial={'name_match_score': name_match_score})

    context = {
        'settings_form': form,
        # 'matched_cases': cases,
        'debug_message': debug_message,
    }
    return render(request, 'orders/settings.html', context)


@login_required
def select_names(request, order_id):
    """
    Unused
    :param request: the request object
    :param order_id: id of the order to process
    :return:
    """
    from nameviewer.helpers import NameMergerHelper

    unique_searchname_list = NameMergerHelper.name_parser_orchestrator(order_id)

    context = { 'unique_names': sorted(unique_searchname_list),
                'order_id': order_id
    }
    return render(request, 'orders/select_names.html', context)


@login_required
def name_select_view_pdf(request):
    """
    Function to return the names selected for an order and generate the cover page, docket list and patriot report.
    This was originally intended to allow a user to filter out names they didn't want included in their final report
    Since then, the xlsx file that's been added allows a user to filter with additional options beyond what this routine
    is capable of handling
    :param request: the request object
    :return:
    """
    from nameviewer.helpers import XMLNameFilterHelper
    from nameviewer.windward import ReportTypes
    from . import tasks

    logger = logging.getLogger(__name__)

    order_id = request.POST['order_id']
    selected_names = request.POST.getlist('selected_name')
    logger.debug("Names selected by user for order id {}".format(order_id))
    logger.debug(selected_names)
    # @TODOs:
    # - create filtered state report
    # - created filtered BK and USDC reports
    # * store name variations selected for the search name in db with dates/order ids for corresponding report
    # * add report name to history of reports generated for this order
    XMLNameFilterHelper.xml_name_filter_orchestrator(order_id, selected_names)

    tasks.process_report(order_id, ReportTypes.DOCKETLIST)
    tasks.process_report(order_id, ReportTypes.PATRIOT)
    tasks.process_report(order_id, ReportTypes.COVER)

    # return the user to the order list screen with new filter reports attached for order
    current_user = request.user
    context = OrderUtils.list_latest_orders(current_user)
    return render(request, 'orders/index.html', context)


@login_required
def search_prev(request):
    """
    Provide access to a previous order that is no longer displayed in the last 100 orders/order list.
    User can specify an order id and the lookup will be performed via that ID
    :param request: the request object
    :return:
    """
    user_search_info = None
    if request.method == "POST":
        client_num = request.POST.get('client_num')
        if client_num:
            current_user = request.user
            context = OrderUtils.list_specific_order(current_user, client_num)
            return render(request, 'orders/index.html', context)

    context = {
        'user_search_info' : user_search_info
    }
    return render(request, 'orders/search_prev.html', context)


@csrf_exempt
def xml_to_base64(request):
    if request.method == 'POST' and request.FILES.get('file'):
        xml_file = request.FILES['file']
        xml_content = xml_file.read()
        encoded_content = base64.b64encode(xml_content).decode('utf-8')
        # Guardar el contenido codificado en la sesión para usarlo en la siguiente vista
        selected_option = request.POST.get('option')
        
        if encoded_content:
            template_name = selected_option
            namesearch_data = base64.b64decode(encoded_content)
            xml_data = minidom.parseString(namesearch_data)
            
            if template_name == 'BankruptcyReport':
                response= replace_bankruptcy(xml_data)
            return response
        else:
            pass
    
    return JsonResponse({'error': 'Invalid request'}, status=400)