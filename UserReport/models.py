from django.db import models

# Create your models here.


class SummaryData(models.Model):
    file_name = models.CharField(max_length=200)
    upload_date = models.DateTimeField(auto_now_add=True)
    summary = models.TextField(blank=True)

    class Meta:
        ordering = ["-upload_date"]
