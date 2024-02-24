from django.db import models

class Trackable(models.Model):

    class Meta:
        abstract = True

    