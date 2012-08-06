from django.db import models
from django.contrib.auth.models import User
from mptt.models import MPTTModel, TreeForeignKey
from django.utils import timezone
from ncm.signals import *
from ncm.management.commands import Systems


class Credential(models.Model):
        username = models.CharField(max_length=150, blank=True, null=True)
        password = models.CharField(max_length=150)

        def __unicode__(self):
           if self.username:
              return self.username
           else:
              return "enable password " + str(self.id)

transports = (
    ("ssh","SSH"),
    ("telnet", "TELNET")
)


os_list = ((k,k) for k,k in Systems.OperatingSystems.iterkeys())
os_list2 = ((k,k) for k,k in Systems.OperatingSystems.iterkeys())

class Node(models.Model):
        name = models.CharField(max_length=100)
        ip   = models.IPAddressField(null=True, blank=True)
        description = models.TextField(null=True, blank=True)
        os   = models.CharField(choices=os_list2,max_length=6, null=True, blank=True)
        transport = models.CharField(choices=transports, max_length=10)
        credentials = models.ForeignKey(Credential, blank=True, null=True)
        escalation_credentials = models.ForeignKey(Credential, blank=True, null=True, help_text="root or enable passwords if needed", related_name="enable_password" )

	def get_related(self):
	    return self._meta.get_all_related_objects()
	def get_ip(self):
	   return self.ip
        def __unicode__(self):
           return self.name + " - " + str(self.ip)

class NodeGroup(MPTTModel):
        name = models.CharField(max_length=150)
        description = models.TextField(blank=True, null=True)
        nodes = models.ManyToManyField(Node, blank=True, null=True)
        parent = TreeForeignKey('self', blank =True, null=True, related_name="children")
	
	class MPTTMeta:
	   order_insertion_by = ['name']
	
	def get_node_list(self):
	   node_list =[]
	   for node in self.nodes.all():
	      node_list.append(node)
	   for desc in self.get_descendants():
	      for node in desc.nodes.all():
	         node_list.append(node)
	   return node_list

        def __unicode__(self):
           return self.name


class Command(models.Model):
        command = models.TextField(('Command(s)'))
        description = models.TextField(blank=True, null=True)
        os   = models.CharField(choices=os_list,max_length=6, null=True, blank=True)

        def __unicode__(self):
           return self.command

class JobManager(models.Manager):
   def due(self):
      return self.filter(models.Q(next_run__lte=timezone.now()) & models.Q(enabled=True))

class Job(models.Model):
        name = models.CharField(max_length=150)
        description = models.TextField(blank=True, null=True)
        command = models.ForeignKey(Command)
        nodes = models.ManyToManyField(Node, blank=True, null=True)
        node_groups = models.ManyToManyField(NodeGroup,blank=True, null=True)

        minute = models.CharField(help_text="0-59 or *",blank=False, null=True, max_length=5)
        hour = models.CharField(help_text="0-23 or *",blank=False, null=True, max_length=5)
        day_of_month = models.CharField(help_text="1-31 or *",blank=False, null=True,max_length=5)
        month = models.CharField(help_text="1-12 or *",blank=False, null=True,max_length=5)
        day_of_week = models.CharField(help_text="0-6 or*",blank=False, null=True,max_length=5)

        last_run = models.DateTimeField(editable=False, blank=True, null=True)
        next_run = models.DateTimeField(blank=True, null=True)
        enabled = models.BooleanField(default=True)
        subscribers = models.ManyToManyField(User, blank=True,
                                         limit_choices_to={'is_staff':True})
        perform_diff = models.BooleanField(default=False, help_text="Compares current results to previous results")

        notify_on_failure = models.BooleanField(default=True)
        notify_on_success = models.BooleanField(default=False)
        notify_on_diff = models.BooleanField(default=False, help_text="Email subscribers when there is a change")
        keep_a_copy = models.BooleanField(default=False, help_text="By default, if you are performing a diff on this job spur will only update the results if there is a change")

        objects = JobManager()

	def get_node_list(self):
	   node_list = []
	   for node in self.nodes.all():
	      node_list.append(node)
	   for node_group in self.node_groups.all():
	      tmp_list = node_group.get_node_list()
	      for node in tmp_list:	
	         node_list.append(node)
	   return node_list

	def get_cron_string(self):
	   return "%s %s %s %s %s" %(self.minute, self.hour, self.day_of_month, self.month, self.day_of_week)
	
	
        def __unicode__(self):
           return self.name

class Output(models.Model):
        job = models.ForeignKey(Job)
        performed_command = models.ForeignKey(Command)
        node = models.ForeignKey(Node)
        result = models.TextField()
        created_on = models.DateTimeField()
        updated_on = models.DateTimeField(blank=True, null=True)
        successful = models.BooleanField(default=False)
        subscribers_notified = models.BooleanField(default=False, editable=False)

        class Meta:
           ordering = ['-updated_on','-created_on']


        def save(self, *args, **kwargs):
	   if self.created_on:
              self.updated_on = timezone.now()
	   else:
              self.created_on = timezone.now()
              self.updated_on = timezone.now()
           super(Output, self).save()

        def __unicode__(self):
           return self.node.name

class Change(models.Model):
	job = models.ForeignKey(Job)
	node = models.ForeignKey(Node, related_name="node")
	from_datetime = models.DateTimeField()
	from_output = models.TextField()
	to_datetime = models.DateTimeField()
	to_output = models.TextField() 
        created = models.DateTimeField()
	diff = models.TextField()

        def attrs(self):
           for attr, value in self.__dict__.iteritems():
              yield attr, value
	
	def get_admin_url(self):
	   return "<a href='/admin/ncm/change/%d/'>%s</a>" %(self.id, self)
	
	class Meta:
	   ordering=['-created']

        def save(self, *args, **kwargs):
           self.created = timezone.now()
           super(Change, self).save()

	def __unicode__(self):
	   return "Diff %s > %s " %(self.job.name, self.job.command.command)

models.signals.post_save.connect(email_subscribers, sender=Change)
models.signals.post_save.connect(email_subscribers, sender=Output)
