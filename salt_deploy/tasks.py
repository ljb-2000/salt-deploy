#coding:utf-8
from celery import task,platforms
from django.conf import settings
from mysite.comm import *
from .models import *

platforms.C_FORCE_ROOT = True

@task()
def exec_task(job_id):
    ret = Job.objects.get(id=job_id)
    g_type = ret.g_type
    minions = ret.minions
    username = ret.creator
    script_name = ret.mod.script_name[:-4]
    state = ret.state  
    ret.state = 1
    ret.save()
    log_file = '%s/logs/salt_deploy/%d.log' % (settings.BASE_DIR, job_id)
    if g_type == 'D':
        cmd = '/usr/bin/salt \'%s\' state.sls %s &>>%s' % (minions, script_name, log_file)
    else:    
        cmd = '/usr/bin/salt -%s \'%s\' state.sls %s &>>%s' % (g_type, minions, script_name, log_file)
    r, err = local_cmd("echo '\n%s\n-----------------------------------------------------------------\n\n' >%s;%s" % (cmd, log_file, cmd))
    if not err:
        ret.state = 2
    else:
        ret.state = 3
    ret.save()
    return job_id




