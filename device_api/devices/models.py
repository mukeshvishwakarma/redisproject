from django.db import models

class Device(models.Model):
    device_id = models.CharField(max_length=100)

class DeviceLocation(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField()
