from django import forms
from .models import SummaryData

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = SummaryData
        fields = ('file_name',) 
