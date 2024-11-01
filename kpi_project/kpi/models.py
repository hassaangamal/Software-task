from django.db import models

class Asset(models.Model):
    asset_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.asset_id

class KPI(models.Model):
    name = models.CharField(max_length=100, unique=True)
    expression = models.TextField()
    description = models.TextField(blank=True, null=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='kpis', default=1)  
    def __str__(self):
        return self.name

class Message(models.Model):
    asset_id = models.CharField(max_length=50)
    attribute_id = models.CharField(max_length=50)
    timestamp = models.DateTimeField()
    value = models.CharField(max_length=100)  

