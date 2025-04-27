# forms.py

from django import forms
from .models import CrimeReport, ReportImage

class CrimeReportForm(forms.ModelForm):
    class Meta:
        model = CrimeReport
        fields = ['authority', 'crime_type', 'first_name', 'last_name', 'email']

class ReportImageForm(forms.ModelForm):
    class Meta:
        model = ReportImage
        fields = ['image']
