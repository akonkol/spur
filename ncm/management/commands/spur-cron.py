from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import connection
from datetime import datetime
from croniter import croniter
import pytz
from multiprocessing import Process
import Systems
import Connectivity
import re
from ncm.models import Output, Change, Job
import difflib

def ExecuteJob(job, node):
	'''close db connection while spawning'''
	connection.close()
 	try:
	   host = node.ip
	   username = node.credentials.username
	   password = node.credentials.password
	   result=""
	   transport = node.transport
	   if transport == "telnet":
	      port = 23
	   if transport == "ssh":
	      port =22

           o = Systems.OperatingSystems[node.os]
           session = Connectivity.Session(host, port, transport, o)
           session.login(username, password)
	
	   '''if we have escalation credentials, escalate'''
	   if node.escalation_credentials:
	      session.escalateprivileges(node.escalation_credentials.password)
	   for command_line in job.command.command.splitlines():
	         result +=  session.sendcommand(command_line)

           session.logout()
	   successful =True

	except Exception, e:
	   ''' job failed '''
	   successful = False
	   result = str(e) 
	   print "*** FAIL  %s %s %s ***" %(job.name, node.name, result)
	   Output.objects.create(job=job,node=node,performed_command=job.command,result=result,successful = successful)

	if job.perform_diff:	
	   '''we need to find a previous output of the same command and node'''
	   try:
	      previous_output = Output.objects.filter(job=job, node=node, performed_command=job.command,successful=True).latest('updated_on')
	      diff = PerformDiff(previous_output.result, result, previous_output.updated_on, datetime.utcnow().replace(tzinfo=timezone.utc))
	      if diff:
	         '''create change object, update previous_output'''
		 Change.objects.create(job=job, node=node,diff="\n".join(diff), from_output=previous_output.result,to_output= result,
                                       from_datetime=previous_output.updated_on,to_datetime =datetime.utcnow().replace(tzinfo=timezone.utc))
		 previous_output.result=result
		 previous_output.save()
	      else:
	         '''no diff, update previous_output updated_on'''
		 previous_output.save()

	   except Exception,e:
	      '''no previous output for this command and node exists create new output'''
	      Output.objects.create(job=job,node=node,performed_command=job.command,result=result,successful = successful)

	else:
	   '''We aren't performing a diff so just save a copy of the output'''
	   Output.objects.create(job=job,node=node,performed_command=job.command,result=result,successful = successful)

def PerformDiff(previous, current, from_name, to_name):
	import difflib
	diff = difflib.unified_diff(previous.split('\n'), current.split('\n'), 
	                            fromfile=str(from_name), tofile=str(to_name),n=4)
	diff_lines = list(diff)
	if len(diff_lines) > 0:
	   return diff_lines
	else:
	   '''there is no diff'''
	   return None


class Command(BaseCommand):
    help = 'Runs all jobs that are due.'

    def handle(self, *args, **options):
	utc = pytz.UTC

        for job in Job.objects.due():
	   for node in job.nodes.all():
	      '''spawn process for each node'''
	      p = Process(target=ExecuteJob, kwargs={'node':node,'job':job})
	      p.start()

	   for node_group in job.node_groups.all():
	      for node in node_group.get_node_list():
		    '''spawn a process for each node'''
	            p = Process(target=ExecuteJob, kwargs={'node':node,'job':job} )
	            p.start()
	      
	   job.last_run= datetime.utcnow().replace(tzinfo=timezone.utc)
	   cron_string = "%s %s %s %s %s" %(job.minute, job.hour, job.day_of_week,job.month, job.day_of_month) 
	   
	   frequency = croniter(cron_string,timezone.make_naive(job.last_run,timezone.get_current_timezone()))
	   naive_next_run = frequency.get_next(datetime)
	   tz = pytz.timezone('US/Central')
	   d_tz = tz.normalize(tz.localize(naive_next_run))
	   utc = pytz.timezone('UTC') 
	   d_utc = d_tz.astimezone(utc)
	   job.next_run = d_utc 
	   job.save()
