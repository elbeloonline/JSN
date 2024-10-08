from .models import Client


class OrderUtils:

    @staticmethod
    def sync_qb_clients():
        """
        Pull in new clients from an exported QuickBooks file
        :return: number of rows parsed and processed by sync routine
        """
        import csv
        from django.conf import settings

        csv_filename = settings.MEDIA_ROOT + '/' + 'accounts.csv'
        first_row_fetched = False
        rows_processed = 0
        with open(csv_filename,'r') as csvfile:
            qb_account_reader = csv.reader(csvfile)
            for row in qb_account_reader:
                if not first_row_fetched:
                    first_row_fetched = True
                rows_processed += 1
                client_id, client_name = row
                c, created = Client.objects.get_or_create(client_id=client_id, client_name=client_name)
                print(('Created object {}? {}').format(c, str(created)))

        return rows_processed

    @staticmethod
    def client_id_strlist_from_queryset(user_client_id_list, field_name):
        """
        Converts the field_name of queryset user_client_id_list into a python list
        :param user_client_id_list: django queryset
        :param field_name: name of field in queryset to use as values
        :return: List[str]
        """
        client_id_queryset = user_client_id_list.values(field_name)
        client_ids = [str(u[field_name]) for u in client_id_queryset]
        return ','.join(client_ids)

    @staticmethod
    def client_id_intlist_from_queryset(user_client_id_list, field_name):
        """
        Converts the field_name of queryset user_client_id_list into a python list
        :param user_client_id_list: django queryset
        :param field_name: name of field in queryset to use as values
        :return: List[str]
        """
        client_id_queryset = user_client_id_list.values(field_name)
        # client_ids = [str(u[field_name]) for u in client_id_queryset]
        # return ','.join(client_ids)
        client_ids = [int(u[field_name]) for u in client_id_queryset]
        return client_ids

    @staticmethod
    def list_latest_orders(current_user):
        """
        Return orders based on associated user's company/client list
        If not found and user is super user, return all orders
        Otherwise, return nothing
        :param current_user:
        :return:
        """
        from .models import Order
        num_records_to_return = 100
        # # latest_order_list = Order.objects.order_by('-created')[:num_records_to_return].prefetch_related()
        latest_order_list = None

        user_client_id_list = OrderUtils.get_user_client_ids(current_user)
        user_is_superuser = current_user.is_superuser and current_user.is_active

        if len(user_client_id_list) > 0:
            # client_ids = OrderUtils.client_id_strlist_from_queryset(user_client_id_list, 'client_id')
            client_ids = OrderUtils.client_id_intlist_from_queryset(user_client_id_list, 'client_id')
            # latest_order_list = Order.objects.raw("Select * from orders_order where client_id IN (%s) order by id desc LIMIT %s", [client_ids, num_records_to_return])
            latest_order_list = Order.objects.filter(client_id__in=client_ids).order_by("-id")[:100].prefetch_related('client').prefetch_related('generatedreport_set')
        elif user_is_superuser:
            # sql = """
            #     Select * from orders_order, orders_client, orders_generatedreport
            #     where orders_order.client_id = orders_client.id
            #     and orders_order.id = orders_generatedreport.order_id
            #     order by orders_order.id desc LIMIT {}
            # """
            # latest_order_list = Order.objects.raw(sql.format(num_records_to_return))
            latest_order_list = Order.objects.order_by("-id")[:100].prefetch_related('client').prefetch_related('generatedreport_set').prefetch_related('searchname_set')


        context = {
            'latest_order_list': latest_order_list,
        }
        return context

    @staticmethod
    def list_specific_order(current_user, client_file_num_str):
        """
        Find a specific order based on an associated user's company/client list
        If super user, return anything that matches
        Otherwise, return nothing
        :param current_user:
        :return:
        """
        from .models import Order

        user_client_id_list = OrderUtils.get_user_client_ids(current_user)
        user_is_superuser = current_user.is_superuser and current_user.is_active

        if len(user_client_id_list) > 0:
            client_ids = OrderUtils.client_id_strlist_from_queryset(user_client_id_list, 'client_id')
            latest_order_list = Order.objects.raw("Select * from orders_order where client_id IN (%s) and title_number like %s order by id desc", [client_ids, client_file_num_str])
        elif user_is_superuser:
            latest_order_list = Order.objects.raw("Select * from orders_order where title_number like %s order by id desc", [client_file_num_str])

        context = {
            'latest_order_list': latest_order_list,
        }
        return context

    @staticmethod
    def get_user_client_ids(current_user):
        """
        Get a list of users associated with a client/company based on the user id provided
        :param current_user: meant to be the logged in user's id, but can be any user id if known
        :return: list of UserClient objects
        :rtype: list[UserClient]
        """
        from .models import UserClient
        user_client_id_list = UserClient.objects.filter(user_id=current_user.id)
        return user_client_id_list

    @staticmethod
    def get_names_from_order(order):
        """
        Return a list of search names associated with an order
        :param order: Order object
        :return: list of SearchName objects associated with the order
        """
        # type: (orders.models.Order) -> [str]
        # names = order.searchname_set.all()
        # search_names = []
        # for name in names:
        #     search_names.append(name)
        # return search_names
        return order.searchname_set.all()

    @staticmethod
    def check_search_status(order_id, report_type):
        """
        Checks the status of a search to determine if it's complete or not
        Used by the page displayed after an order is submitted.
        When complete, that page can go back to the orders screen so the user can grab their results
        :param order_id: id of the order who's status should be checked
        :param report_type: the type of report being queried for (used by this routine to check the number of results column)
        :return: bool indicating of order is complete or not
        """
        from .models import GeneratedReport
        from nameviewer.windward import ReportTypes
        order_complete = False
        order_report = GeneratedReport.objects.filter(order_id=order_id)
        if order_report and len(order_report) > 0:
            generated_report = order_report[0]
            if report_type == ReportTypes.FULL and not generated_report.merged_report_filename == '':
            # if report_type == ReportTypes.FULL and generated_report.name_select_ready == 'Y':
                order_complete = True
            elif report_type == ReportTypes.STATE and generated_report.num_state_matches > -1:
                order_complete = True
            elif report_type == ReportTypes.BANKRUPTCY and generated_report.num_bankruptcy_matches > -1:
                order_complete = True
            elif report_type == ReportTypes.USDC and generated_report.num_usdc_matches > -1:
                order_complete = True
            elif report_type == ReportTypes.PATRIOT and generated_report.num_patriot_matches > -1:
                order_complete = True

        return order_complete

    @staticmethod
    def clear_order_generated_reports(order_id, report_type):
        """
        Clear the search results for a order with previously generated results
        :param order_id: the order id to query for
        :param report_type: the report type to operate on
        :return: None
        """
        from orders.models import Order
        from nameviewer.windward import ReportTypes
        order = Order.objects.get(pk=order_id)
        generated_reports = order.generatedreport_set.order_by('-id')
        if (len(generated_reports) > 0):
            generated_report = generated_reports[0]
            if report_type == ReportTypes.STATE:
                generated_report.state_filename = ''
                generated_report.num_state_matches = -1
                print("****** state report, clearing old report data *******")
            elif report_type == ReportTypes.BANKRUPTCY:
                generated_report.bankruptcy_filename = ''
                generated_report.num_bankruptcy_matches = -1
            elif report_type == ReportTypes.USDC:
                generated_report.usdc_filename = ''
                generated_report.num_usdc_matches = -1
            elif report_type == ReportTypes.PATRIOT:
                generated_report.patriot_filename = ''
                generated_report.num_patriot_matches = -1
            elif report_type == ReportTypes.FULL:
                generated_report.merged_report_filename = ''
                generated_report.name_select_ready = ''
                # generated_report.cover_filename = ''
                OrderUtils.clear_order_generated_reports(order_id, ReportTypes.STATE)
                OrderUtils.clear_order_generated_reports(order_id, ReportTypes.BANKRUPTCY)
                OrderUtils.clear_order_generated_reports(order_id, ReportTypes.USDC)
            generated_report.save()
            # order.generatedreport_set[0] = generated_report
            order.save()

from enum import Enum

class CaseMatchSortType(Enum):
    """
    An Enum to determine how report results are sorted and returned
    """
    CHILD_SUPPORT_AMT_DESC = 'child_suport_amt_desc'
    CASE_FILED_DATE_ASC = 'case_filed_date_asc'
