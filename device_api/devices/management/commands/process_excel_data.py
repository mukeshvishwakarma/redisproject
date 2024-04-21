from django.core.management.base import BaseCommand
import pandas as pd
from devices.models import Device, DeviceLocation
from devices.views import get_redis_connection
from datetime import datetime

class Command(BaseCommand):
    help = 'Process and store Excel data in Redis and Django models'

    def handle(self, *args, **options):
        df = pd.read_csv('data/path_to_excel.csv')
        df_sorted = df.sort_values(by='sts')

        r = get_redis_connection()

        for index, row in df_sorted.iterrows():
            device_id = row['device_fk_id']
            latitude = row['latitude']
            longitude = row['longitude']
            timestamp = row['sts']

            # Store in Redis
            device_info = {
                'latitude': latitude,
                'longitude': longitude,
                'timestamp': str(timestamp)
            }
            r.hmset(device_id, device_info)

            # Store in Django models
            device, created = Device.objects.get_or_create(device_id=device_id)
            location = DeviceLocation(device=device, latitude=latitude, longitude=longitude, timestamp=timestamp)
            location.save()

        self.stdout.write(self.style.SUCCESS('Successfully processed and stored data in Redis and Django models'))
