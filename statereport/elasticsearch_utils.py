from django.conf import settings

from django_elasticsearch_dsl import Index, fields, Document
from elasticsearch import Elasticsearch


class ElasticSearchUtils:

    def __init__(self):
        es_host_str = settings.ELASTICSEARCH_DSL['default']['hosts']
        es_host, es_port = es_host_str.split(':')
        # es_host_nodes = [{"host": "18.205.38.138", "port": 9200}]
        es_host_nodes = [{"host": es_host, "port": int(es_port)}, scheme: "https"]
        self.host_nodes = es_host_nodes

    def _build_name_q(self, names_list):
        """
        Build a list of elasticsearch-dsl Q objects to create a search filter
        List is created with OR operator
        :param names_list: list of names to use for filter
        :return: list of Q objects to use for searching ES database
        """
        from elasticsearch_dsl import Q
        # q_list = None
        # for name in names_list:
        #     if not q_list:
        #         q_list = Q("match", full_search_party_name=name)
        #     else:
        #         q_list = q_list | Q("match", full_search_party_name=name)
        names_list = [x[:9] for x in names_list]
        q_list = Q("terms", full_search_party_name=names_list)
        return q_list

    def _build_bkcy_name_q(self, names_list):
        """
        Build a list of elasticsearch-dsl Q objects to create a search filter
        List is created with OR operator
        :param names_list: list of names to use for filter
        :return: list of Q objects to use for searching ES database
        """
        from elasticsearch_dsl import Q
        q_list = Q("terms", party_name=names_list)
        return q_list

    def _extract_cases_from_es_results(self, response):
        """
        Extract a list of case ids from response
        :param response: Elasticsearch Search response
        :return: list of case_ids
        """
        x = []
        xn = []
        for es_match in response:
            x.append(es_match.case_id)
            xn.append(es_match.full_search_party_name)
        return x

    def _extract_bkcy_cases_from_es_results(self, response):
        """
        Extract a list of bankruptcy case ids from response
        :param response: Elasticsearch Search response
        :return: list of case_ids
        """
        x = []
        xn = []
        for es_match in response:
            x.append(es_match.bankruptcy_index_case_id)
            xn.append(es_match.party_name)
        return x

    def get_scnj_cases(self, case_list):
        """
        Fetch a list of statereport.models.Case objects matching case ids provided
        :param case_list: list of Case ids to match
        :return: list of matching statereport.models.Case objects
        """
        from statereport.models import Case
        case_matches = Case.objects.filter(pk__in=case_list).using(settings.NAMESEARCH_DB)
        return case_matches

    def scnj_case_list_from_name_list(self, first_name_list, last_name_list, es_index):
        """
        Return a list of SCNJ cases from elasticsearch index matching the first and last name lists
        :param first_name_list: list of first name aliases
        :param last_name_list: list of last name aliases
        :param es_index: elasticsearch index to use for performing the lookup
        :return:
        """
        from elasticsearch_dsl import Q, Search
        es = Elasticsearch(hosts=self.host_nodes)
        search = Search(using=es, index=es_index)
        firstNameFilter = self._build_name_q(first_name_list)
        lastNameFilter = self._build_name_q(last_name_list)

        # combinedFilter = (firstNameFilter) & (lastNameFilter)
        # search = search.query('bool', filter=[combinedFilter])
        search = search.query('bool', filter=firstNameFilter).query('bool', filter=lastNameFilter)

        search_count = search.count()
        response = search[:search_count].execute()  # retrieve more than default 10 results
        # case_list = self._extract_bkcy_cases_from_es_results(response)
        case_list = self._extract_cases_from_es_results(response)
        return case_list

    def case_list_from_name_list(self, first_name_list, last_name_list, es_index):
        """
        Return a list of BKCY cases from elasticsearch index matching the first and last name lists
        :param first_name_list: list of first name aliases
        :param last_name_list: list of last name aliases
        :param es_index: elasticsearch index to use for performing the lookup
        :return:
        """
        from elasticsearch_dsl import Q, Search
        es = Elasticsearch(hosts=self.host_nodes)
        search = Search(using=es, index=es_index)
        firstNameFilter = self._build_bkcy_name_q(first_name_list)
        lastNameFilter = self._build_bkcy_name_q(last_name_list)

        # combinedFilter = (firstNameFilter) & (lastNameFilter)
        # search = search.query('bool', filter=[combinedFilter])
        search = search.query('bool', filter=firstNameFilter).query('bool', filter=lastNameFilter)

        search_count = search.count()
        response = search[:search_count].execute()  # retrieve more than default 10 results
        case_list = self._extract_bkcy_cases_from_es_results(response)
        return case_list
