from django.db import models
from bulk_update.manager import BulkUpdateManager
# Create your models here.


class Video(models.Model):
    uuid = models.CharField(max_length=255)
    count = models.IntegerField(null=False, blank=False)
    objects = BulkUpdateManager()

class Stats(models.Model):
    enque_time = models.CharField(null=True, max_length=255)
    consume_time = models.CharField(null=True, max_length=255)


def __unicode__(self):
    return self.uuid
