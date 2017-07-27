#coding:utf-8
from django.contrib import admin
from .models import *

class Mod_confAdmin(admin.ModelAdmin):
    list_display = ('id', 'mod_name', 'script_name', 'desc', 'creator', 'is_active', 'create_time', 'update_time')

class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'g_type', 'minions', 'state', 'create_time', 'update_time')

admin.site.register(Mod_conf, Mod_confAdmin)
admin.site.register(Job, JobAdmin)
