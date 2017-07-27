#-*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from .views import *

urlpatterns = [
    url(r'^health$', health),
    url(r'^mod_list$', mod_list),
    url(r'^add_mod$', add_mod),
    url(r'^edit_mod$', edit_mod),
    url(r'^job_list$', job_list),
    url(r'^add_job$', add_job),
    url(r'^show_log$', show_log),
    url(r'^update_state$', update_state),
    url(r'^ajax_deploy$', ajax_deploy),
]
