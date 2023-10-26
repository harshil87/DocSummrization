from django.contrib import admin
from .models import SummaryData
# Register your models here.

class SummaryAdmin(admin.ModelAdmin):
    list_display = ('id','file_name', 'upload_date','summary')

admin.site.register(SummaryData,SummaryAdmin)