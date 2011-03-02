from django.db import models

class Code(models.Model):
    code = models.TextField()
    lang = models.CharField(max_length=100)