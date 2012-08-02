from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.utils import simplejson
import subprocess
from ncm.forms import *
from ncm.management.commands import Connectivity, Systems
from ncm.models import *
import difflib

@staff_member_required
def import_node(request):
    if request.method == "POST":
        form = NodeImportForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            success = True
            return HttpResponseRedirect("/admin/ncm/node/")
    else:
        form = NodeImportForm()
        context = {"form": form}
        return render_to_response("admin/ncm/import_node.html", context,
        context_instance=RequestContext(request))

def run_job(request, job_id):
	job = Job.objects.get(id=job_id)
	job.next_run = timezone.now() 
	job.save()
	return HttpResponseRedirect("/admin/ncm/output/")

def diff(request, change_id):
	change = Change.objects.get(id=change_id)
	d = difflib.HtmlDiff()
	table = d.make_table(change.from_output.splitlines(), change.to_output.splitlines(),
	                     "%s<br/>%s<br/>%s" %(change.job.command.command,change.node,change.from_datetime),
		             "%s<br/>%s<br/>%s"	%(change.job.command.command,change.node,change.to_datetime))
	if request.is_ajax():
	   result = {'table':"",'success':""}
	   result['table'] = table
	   result['success']= True
	   json = simplejson.dumps(result)
	   return HttpResponse(json, mimetype='application/json')

	return render_to_response("admin/ncm/full_diff.html", {'diff':table,'change':change})

def ping(request, node_id):
        node = Node.objects.get(id=node_id)
        address = node.ip
        success = False
        try:
           result = subprocess.call(["ping","-c","3",address],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
           if result == 0:
              success = True
              msg = "Recieved Response from: %s" %(address)
           elif result == 1:
              msg = 'Host not found'
           elif result == 2:
              msg = 'Ping timed out'
        except Exception:
           msg =  "Ping error"
           raise
	if request.is_ajax():
	   result = {'response':msg,'success':True}
	   json = simplejson.dumps(result)
	   return HttpResponse(json, mimetype='application/json')


def test_login(request, node_id):
        node = Node.objects.get(id=node_id)
        if node.transport == "telnet":
           port =23
        if node.transport == "ssh":
           port=22

        try:
           m = Systems.OperatingSystems[node.os]
           s = Connectivity.Session(node.ip,port,node.transport,m)
           success = s.login(node.credentials.username, node.credentials.password)
           if success:
              msg = "Login Succeeded"
           else:
              raise
        except Exception, e:
           msg = str(e)

	if request.is_ajax():
	   result = {'response':msg,'success':True}
	   json = simplejson.dumps(result)
	   return HttpResponse(json, mimetype='application/json')
        return render_to_response("admin/ncm/test_login.html",{'msg':msg})

def redirect_to_admin(request):
	return HttpResponseRedirect("/admin/")
