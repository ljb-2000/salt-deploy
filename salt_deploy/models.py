#coding:utf-8
from __future__ import unicode_literals
from django.db import models


class Mod_conf(models.Model):
    '''模块配置'''
    mod_name = models.CharField(u'模块名', max_length=30, unique=True)
    script_name = models.CharField(u'脚本名', max_length=30)
    desc = models.TextField(u'描述', blank=True)
    is_active = models.IntegerField(u'是否启用', default=1)
    creator = models.CharField(u'创建人', max_length=30)
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    update_time = models.DateTimeField(u'更新时间', auto_now=True)
    def __unicode__(self):
        return self.mod_name

class Job(models.Model):
    '''工作表'''
    mod = models.ForeignKey(Mod_conf, blank=True)
    g_type = models.CharField(u'匹配类型', max_length=1)
    minions = models.CharField(u'minions', max_length=999)
    state = models.IntegerField(u'当前状态', default=0)     #0等待部署 1部署中 2部署完成 3部署失败
    creator = models.CharField(u'创建人', max_length=30)
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    update_time = models.DateTimeField(u'更新时间', auto_now=True)
