#coding:utf-8
import os
import sys
import time
import json
import re
import logging
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.conf import settings
from mysite.comm import *
from main.views import *
from .models import *
from .tasks import exec_task

logger = logging.getLogger(__name__)
reload(sys)
sys.setdefaultencoding('utf-8')

def health(request):
    return HttpResponse('ok')

@login_required
@require_role(role_list=['op'])
def mod_list(request):
    title = '模块配置列表'
    key = request.GET.get('key','')
    if key:
        rets = Mod_conf.objects.filter(Q(mod_name__contains=key)|Q(script_name__contains=key)|Q(creator__contains=key))
    else:
        rets = Mod_conf.objects.all()
    msgnum = rets.count()
    pagenum = settings.PAGE_LIMIT
    script_dir = settings.SCRIPT_DIR
    return render_to_response('salt_deploy/mod_list.html',locals())

@login_required
@require_role(role_list=['op'])
def add_mod(request):
    title = '添加模块'
    act = 'add_mod'
    mod_list = [f for f in os.listdir(settings.SCRIPT_DIR) if f.endswith('.sls')]
    return render_to_response('salt_deploy/add_mod.html', locals())

@login_required
@require_role(role_list=['op'])
def edit_mod(request):
    username = request.user.username
    id = request.GET.get('id')
    if not id: return HttpResponse('参数错误')
    act = 'edit_mod'
    title = '修改模块信息'
    info = Mod_conf.objects.get(id=int(id))
    return render_to_response('salt_deploy/edit_mod.html', locals())

@login_required
@require_role(role_list=['op'])
def job_list(request):
    title = '部署任务列表'
    key = request.GET.get('key','')
    page = request.GET.get('page','1')
    if key:
        rets = Job.objects.filter(Q(mod__mod_name__contains=key)|Q(mod__script_name__contains=key)|Q(minions__contains=key)|Q(creator__contains=key)).order_by('-id')
    else:
        rets = Job.objects.order_by('-id')
    msgnum = rets.count()
    pagenum = settings.PAGE_LIMIT
    state_dict = {0:'等待部署',1:'部署中',2:'部署成功',3:'部署失败'}
    return render_to_response('salt_deploy/job_list.html',locals())

@login_required
def update_state(request):
    page = request.GET.get('page','')
    start = (int(page) - 1) * settings.PAGE_LIMIT
    end = start + settings.PAGE_LIMIT
    rets = Job.objects.order_by('-id')[start:end]
    data = []
    for ret in rets:
        update_time = ret.update_time
        update_time = update_time.strftime("%Y-%m-%d %H:%M:%S")    
        d = {'job_id':ret.id, 'state':ret.state, 'update_time':update_time}
        data.append(d)
    return HttpResponse(json.dumps(data))

@login_required
@require_role(role_list=['op'])
def add_job(request):
    title = '添加部署任务'
    act = 'add_job'
    mod_list = Mod_conf.objects.filter(is_active=1).order_by('mod_name')
    g_type_list = ['D', 'N', 'L', 'G', 'E', 'P', 'I', 'S', 'R']
    return render_to_response('salt_deploy/add_job.html', locals())

@login_required
@require_role(role_list=['op'])
def show_log(request):
    title = '查看部署日志'
    id = request.GET.get('id','')
    #工单执行日志文件如果存在则显示执行日志
    log_file = '%s/logs/salt_deploy/%s.log' % (settings.BASE_DIR, id)
    log = ''
    if os.path.exists(log_file):
        f = open(log_file)
        log = f.read()
        f.close()
    return render_to_response('salt_deploy/show_log.html', locals())

@login_required
def ajax_deploy(request):
    user = request.user
    ret = False
    if request.method == 'POST':
        act = request.POST.get('act')
        if act == 'add_mod':
            mod_name = request.POST.get('mod_name').strip()
            script_name = request.POST.get('script_name').strip()
            desc = request.POST.get('desc')
            is_active = request.POST.get('is_active')
            if not Mod_conf.objects.filter(mod_name=mod_name):
                ret = Mod_conf.objects.create(mod_name=mod_name, script_name=script_name, desc=desc, creator=user.username, is_active=int(is_active))
                if ret: ret = '添加成功'
        elif act == 'add_job':
            mod_id = request.POST.get('mod_id')
            g_type = request.POST.get('g_type')
            minions = request.POST.get('minions').strip()
            mod_obj = Mod_conf.objects.get(id=int(mod_id))
            ret = Job.objects.create(mod=mod_obj, g_type=g_type, minions=minions, creator=user.username)
            exec_task.delay(ret.id)
            if ret: ret = '添加成功'
        elif act == 'match_minions':
            g_type = request.POST.get('g_type')
            minions = request.POST.get('minions').strip()
            if g_type == 'D':
                cmd = "/usr/bin/salt '%s' test.ping --out=txt|sort |uniq" %  minions
            else:
                cmd = "/usr/bin/salt -%s '%s' test.ping --out=txt|sort |uniq" % (g_type, minions)
            r, err = local_cmd(cmd)
            if not err:
                num, err = local_cmd('echo -e "%s"|wc -l' % r)
                if len(r) > 1000: r = r[0:1000] + ' ......'
                if not 'ERROR: No return received' in r:
                    ret = r + '\n匹配主机数：' + num
                else:
                    ret = r
            else:
                ret = err
        elif act == 'edit_mod':
            mod_id = request.POST.get('id')
            mod_name = request.POST.get('mod_name').strip()
            script_name = request.POST.get('script_name').strip()
            desc = request.POST.get('desc')
            is_active = request.POST.get('is_active')
            if Mod_conf.objects.filter(id=int(mod_id)):
                mod = Mod_conf.objects.get(id=int(mod_id))
                mod.mod_name = mod_name
                mod.script_name = script_name
                mod.desc = desc
                mod.is_active = int(is_active)
                mod.save()
                ret = '修改成功'
            else:
                ret = '错误：id不存在'
        elif act == 'del_mod':
            mod_id = request.POST.get('id')
            ret = Mod_conf.objects.filter(id=int(mod_id)).delete()
            if ret: ret = '删除成功'
    return HttpResponse(ret)
    
