import os
import sys

import ujson as json
from django.core.wsgi import get_wsgi_application
proj_path = os.path.join(os.getcwd(), 'video_distributor/')
sys.path.append(proj_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "video_distributor.settings")
application = get_wsgi_application()
from video.models import Stats, Video


class ClientError(Exception):
    pass


class Client(object):
    """
    Class that allows us to interact with the django models (databse ORM)
    """
    def __init__(*args, **kwargs):
        """
        PROHIBIT class from Instantiation
        @raise
        Client
        """
        raise ClientError("Client is an Engine, Donot Instantiate this Class")

    @classmethod
    def update_count(cls, data):
        """
        update count for a individual video
        """
        uuid, count = data
        rec = Video.objects.get(uuid=uuid)
        rec.count = count
        rec.save()
        # print "invoked real-time", uuid, count

    @classmethod
    def update_counts(cls, to_update):
        """
        update a dicionary of playcounts.
        optimized for bulk_update
        """
        videos_to_update = Video.objects.filter(uuid__in=to_update.keys())
        for v in videos_to_update:
            v.count = to_update[v.uuid]
        Video.objects.bulk_update(videos_to_update, update_fields=['count'])

    @classmethod
    def update_stats(cls, data):
        """
        update the stats model
        """
        enque_time, consume_time = data
        record = Stats(enque_time=enque_time, consume_time=consume_time)
        record.save()

    @classmethod
    def truncate(cls):
        """
        truncate everything
        """
        Video.objects.all().delete()
        Stats.objects.all().delete()

    @classmethod
    def reset(cls, uuids):
        """
        reset according to given uuids
        """
        cls.truncate()
        objs = [Video(uuid=u, count=0) for u in uuids]
        Video.objects.bulk_create(objs)

    @classmethod
    def export_result(cls):
        """
        export the Video model
        """
        return json.dumps(Video.objects.all().values())

    @classmethod
    def export_stats(cls):
        """
        export the Stats Model
        """
        return json.dumps(Stats.objects.all().values())
