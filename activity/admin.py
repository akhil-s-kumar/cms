from django.contrib import admin
from .models import *
from easy_select2 import select2_modelform
from import_export.admin import ImportExportModelAdmin, ExportActionMixin


@admin.register(News)
class NewsAdmin(ImportExportModelAdmin, ExportActionMixin, admin.ModelAdmin):
    fieldsets = [
        ('Basic Details', {
            'fields': [
                ('author', 'pinned'),
                ('title', 'slug', 'cover'),
                ('date', 'categories'),
                'tags',
                'description'
            ]
        }),
    ]
    list_display = ('title', 'pinned', 'categories')
    list_filter = ('categories', 'pinned', 'tags')
    select2 = select2_modelform(News, attrs={'width': '800px', 'max-width': '100%'})
    form = select2


@admin.register(Tags)
class NewsAdmin(ImportExportModelAdmin, ExportActionMixin, admin.ModelAdmin):
    fieldsets = [
        ('Basic Details', {
            'fields': [
                ('name', 'author')
            ]
        }),
    ]
