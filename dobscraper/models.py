

from django.db import models

# Create your models here.
class ScnjDebtorDob(models.Model):
    judgment_number = models.CharField(max_length=255)
    dob = models.CharField(max_length=20, db_index=False, default=None, null=True)
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return "Debtor name: {}, DoB: {}".format(self.name, self.dob)
