from django.db import models

# Create your models here.

class Country(models.Model):

    code = models.CharField(max_length=8, unique=True, null=False)

    name = models.CharField(max_length=128)

class City(models.Model):

    name = models.CharField(max_length=128, null=False)

    country = models.ForeignKey(
        to=Country,
        on_delete=models.CASCADE,
        related_name='city_country',
        null=False,
    )

    latitude = models.CharField(max_length=32, null=True, blank=True)

    longitude = models.CharField(max_length=32, null=True, blank=True)

class District(models.Model):

    name = models.CharField(max_length=128, null=False)

    city = models.ForeignKey(
        to=City,
        on_delete=models.CASCADE,
        related_name='district_city',
        null=False,
    )

    latitude = models.CharField(max_length=32, null=True, blank=True)

    longitude = models.CharField(max_length=32, null=True, blank=True)

class Ward(models.Model):

    name = models.CharField(max_length=128, null=False)

    district = models.ForeignKey(
        to=District,
        on_delete=models.CASCADE,
        related_name='ward_district',
        null=False,
    )

    latitude = models.CharField(max_length=32, null=True, blank=True)

    longitude = models.CharField(max_length=32, null=True, blank=True)
