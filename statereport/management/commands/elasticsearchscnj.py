

import logging
import os

from django.core.management.base import BaseCommand

from statereport.elasticsearch_utils import ElasticSearchUtils

class Command(BaseCommand):
    help = 'runs a party search on a given elasticsearch cluster'

    # def __init__(self):
    #     self.data_dir = os.path.join(settings.MEDIA_ROOT, settings.EMAIL_DATA_DIR)
    #     self.logger = logging.getLogger(__name__)
    #     self.logger.info('Using {} as the data directory'.format(self.data_dir))

    # def add_arguments(self, parser):
    #     parser.add_argument('num_emails_to_fetch', type=int)

    def _first_names(self):
        # return ['juan', 'juana', 'JAUN', 'jon']
        return ['juan', 'juane', 'juann', 'juean', 'juian', 'juanne', 'juano', 'juans', 'juani', 'jeuan', 'jouan', 'juaan', 'juahn', 'juanito', 'juany', 'juanno', 'juanie', 'juanee', 'juanes', 'juanae', 'john', 'jon', 'jonathan', 'jonatan']

    def _last_names(self):
        # return ['rodriguez']
        return ['rodriguez', 'roddriguez', "rodr'iguez", 'rodrigguez', 'rodrigueez', 'rodriguezs', 'rodriguezz', 'rodriguiez', 'rodrriguez', 'rrodriguez', 'rodriguezi', 'rodrigueza', 'rodriguea', 'rodriguee', 'rhodriguez', 'rodrigue', 'rodrigoez', 'rodrigues', 'rodriguiz', 'rodriguz', 'rodriguezii', 'rodriguess', 'rodrigueuz', 'rodrigouz', 'rodrigkuez', 'rodriguev', 'rodriguewz', 'rodriguex', 'rodrigueg', 'rodriguel', 'rodrigueq', 'rodriguer', 'rodriguezc', 'rodriguezb', 'rodiriguez', 'roderiguez', 'rodriguezl', 'rodriguezp', 'rodriguezr', 'rodriguezf', 'rodriguezm', 'rodriigues', 'roidriguez', 'rodriuguez', 'rodriguze', 'rodrigus', 'ridriguez', 'rodrguez', 'rodrigu', 'rodriguear', 'rodriguezzc', 'rodriguezve', 'rodriguezde', 'rodriguezcc', 'rodriguis', 'rodriguies', 'rodrkiguez', 'rodrigruez', 'rodriggues', 'rodrigous', 'rodrigoes', 'riodriguez', 'reodriguez', 'rodraiguez', 'rodreiguez', 'rodrieguez', 'rodrigoe', 'rodrighez', 'rodrigquez', 'rodriguezba', 'rodriguezal', 'rodriguey', 'roudriguez', 'rodruiguez', 'rodrygue', 'rodrigufz', 'rodriguqz', 'rodriguezfi', 'rodriguezma', 'rodriguezra', 'rodriguezjr', 'rodriguezri', 'rodriguezro', 'rodriguezva', 'rodriguezsie', 'rodriguezoq', 'rodriguezgo', 'rodriguezzcc', 'rodrigz', 'rodrigueth', 'rodriguera', 'rodriguery', 'rodriguen', 'rodrigques', 'rhodrigues', 'rodriquez', 'rodriguezreye', 'peraltarodriguez', 'rodr iguez', 'de rodriguez']

    def handle(self, *args, **options):
        first_name_list = self._first_names()
        last_name_list = self._last_names()
        esu = ElasticSearchUtils()
        case_id_list = esu.case_list_from_name_list(first_name_list, last_name_list)
        case_obj_matches = esu.get_scnj_cases(case_id_list)
        print("Case objects returned: {}".format(len(case_obj_matches)))




