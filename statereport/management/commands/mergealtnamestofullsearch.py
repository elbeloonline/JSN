

import logging

from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from statereport.models import Party


class Command(BaseCommand):
    help = 'Updates the statereport_party table full_search_party_name column'

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def handle(self, *args, **options):
        sql = """
            UPDATE statereport_partyalt
            SET full_search_party_name = CONCAT(party_last_name, party_first_name, party_initial, ' ', 
                party_last_name, ' ', party_first_name, ' ', party_initial);
        """
        self.logger.info("Executing db update command...")
        with connection.cursor() as cursor:
            cursor.execute(sql)
            count_sql = """
                select count(1)
                from statereport_party
                where full_search_party_name <> ''        
            """
            cursor.execute(count_sql)
            count_results = cursor.fetchall()
            new_num_records = int(count_results[0][0])
            self.logger.info("Num merged fields now in database: {}".format(new_num_records))


