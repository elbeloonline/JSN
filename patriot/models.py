

from django.db import models

# Create your models here.


class PatriotPrimName(models.Model):
    """
    A simple class for representing patriot name searches in the system
    """
    prim_name = models.CharField(max_length=255)
    prim_type = models.CharField(max_length=255)

    def __unicode__(self):
        return self.prim_name


class PatriotAltName(models.Model):
    """
    A simple class for representing patriot name searches in the system
    """
    alt_name = models.CharField(max_length=255)
    alt_type = models.CharField(max_length=255)

    def __unicode__(self):
        return self.alt_name


class PatriotImport:
    """
    Data import routines for Patriot searches
    """

    def __init__(self):
        import os

        from django.conf import settings
        alt_filename = "cons_alt.csv"
        prim_filename = "cons_prim.csv"
        primary_data_file = os.path.join(settings.MEDIA_ROOT, prim_filename)
        alt_data_file = os.path.join(settings.MEDIA_ROOT, alt_filename)
        assert os.path.exists(primary_data_file) == True
        assert os.path.exists(alt_data_file) == True
        self.primary_data_file = primary_data_file
        self.alt_data_file = alt_data_file

    @staticmethod
    def _truncate_patriot_tables():
        """
        Clear both the primary name and alternate name
        :return:
        """
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("TRUNCATE TABLE `patriot_patriotprimname`")
        cursor.execute("TRUNCATE TABLE `patriot_patriotaltname`")

    @staticmethod
    def _save_primary_name(prim_name, prim_type):
        """
        Saves patriot primary name record to db
        :param alt_name: str the primary name
        :param alt_type: str the type of the primary name
        :return:
        """
        m = PatriotPrimName(prim_name=prim_name, prim_type=prim_type)
        m.save()

    @staticmethod
    def _save_alternate_name(alt_name, alt_type):
        """
        Saves patriot alternate name record to db
        :param alt_name: str the alternate name
        :param alt_type: str the type of alternate name
        :return:
        """
        m = PatriotAltName(alt_name=alt_name, alt_type=alt_type)
        m.save()

    def import_data(self, limit_processed=None):
        """
        Routine to import Patriot data
        :param: limit_processed int max number of records to process for each type pf name
        :return: num names processed
        """
        import csv
        import logging

        num_prim_processed = 0
        num_alt_processed = 0

        logger = logging.getLogger(__name__)
        self._truncate_patriot_tables()  # rebuild tables from scratch each time this is run
        # primary names
        with open(self.primary_data_file) as csvfile:
            prim_csv_reader = csv.reader(csvfile, quotechar=str('"'), delimiter=str(','))
            for row in prim_csv_reader:
                if not limit_processed or num_prim_processed < limit_processed:
                    try:
                        prim_name = row[1]
                        prim_type = row[2]
                        # print("Data read: {} - {}".format(prim_name, prim_type))
                        self._save_primary_name(prim_name, prim_type)
                    except IndexError:
                        logger.warning("Problem parsing primary name record: {}".format(row))
                else:
                    break
                num_prim_processed += 1
        logger.info("Processed primary names!")
        # alt names
        with open(self.alt_data_file) as csvfile:
            alt_csv_reader = csv.reader(csvfile, quotechar=str('"'), delimiter=str(','))
            for row in alt_csv_reader:
                if not limit_processed or num_alt_processed < limit_processed:
                    try:
                        alt_name = row[3]
                        alt_type = row[2]
                        # print("Data read: {} - {}".format(alt_name, alt_type))
                        self._save_alternate_name(alt_name, alt_type)
                    except IndexError:
                        logger.warning("Problem parsing alt name record: {}".format(row))
                else:
                    break
                num_alt_processed += 1
        logger.info("Processed alternate names!")
        return num_prim_processed + num_alt_processed


class PatriotReportQueryManager:

    def __init__(self):
        pass

    @staticmethod
    def query_database_by_searchname_details(searchname):
        """
        Manager method for querying patriot tables in database
        :param searchname: orders.models.SearchName
        :return: dict
        """
        from .helpers import PatriotResultsDict as prd
        prim_name_matches = PatriotPrimName.objects\
            .filter(prim_name__icontains=searchname.first_name)\
            .filter(prim_name__icontains=searchname.last_name)
        alt_name_matches = PatriotAltName.objects\
            .filter(alt_name__icontains=searchname.first_name)\
            .filter(alt_name__icontains=searchname.last_name)

        patriot_matches = {}  # need the name type attribute for reporting
        # if prim_name_matches:
        #     patriot_matches[prd.PRIM_MATCHES] = prim_name_matches
        # if alt_name_matches:
        #     patriot_matches[prd.ALT_MATCHES] = alt_name_matches
        patriot_matches[prd.PRIM_MATCHES] = prim_name_matches
        patriot_matches[prd.ALT_MATCHES] = alt_name_matches

        return patriot_matches
