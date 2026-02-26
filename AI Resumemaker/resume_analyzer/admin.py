from django.contrib import admin
from .models import UploadedResume


@admin.register(UploadedResume)
class UploadedResumeAdmin(admin.ModelAdmin):
    list_display = ('id', 'original_filename', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('original_filename', 'extracted_text')
