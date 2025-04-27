# models.py

from django.db import models

class CrimeReport(models.Model):
    authority = models.CharField(max_length=50)
    crime_type = models.CharField(max_length=50)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return f"Report for {self.first_name} {self.last_name}"

class ReportImage(models.Model):
    report = models.ForeignKey(CrimeReport, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='crime_reports/')

    def __str__(self):
        return f"Image for {self.report}"
