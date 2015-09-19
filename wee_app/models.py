from django.contrib import auth
from django.db import models

class Point(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        unique_together = (('latitude', 'longitude'),)

class Hotel(models.Model):
    # Priceline's hotel ID.
    pcln_id = models.IntegerField(primary_key=True)
    point = models.OneToOneField(Point)

class Stop(models.Model):
    destination = models.ForeignKey(Point)
    timestamp = models.DateTimeField()

    class Meta:
        unique_together = (('destination', 'timestamp'),)

class PlannedUberRequest(models.Model):
    pickup = models.ForeignKey(Point, related_name='+')
    destination = models.ForeignKey(Point, related_name='+')
    request_timestamp = models.DateTimeField()

    class Meta:
        unique_together = (('pickup', 'destination', 'request_timestamp'),)

class Trip(models.Model):
    user = models.ForeignKey(auth.models.User)
    hotel = models.ForeignKey(Hotel)
    check_in = models.DateField()
    check_out = models.DateField()
    stops = models.ManyToManyField(Stop)
    planned_uber_requests = models.ManyToManyField(PlannedUberRequest)

    # Every point in every planned request must correspond to a stop, and every
    # request timestamp must be reasonable with respect to the stop times.
