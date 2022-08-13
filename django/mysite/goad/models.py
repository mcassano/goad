from django.db import models

# Create your models here.

class Person(models.Model):
    slack_id = models.CharField(primary_key=True, max_length=40)
    slack_name = models.CharField(max_length=40)
    steam_id = models.CharField(max_length=40)
    team_id = models.CharField(max_length=40)