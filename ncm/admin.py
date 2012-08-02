from django import forms
from django.contrib import admin
from ncm.models import *
from ncm.actions import *

class CommandAdmin(admin.ModelAdmin):
	list_display= ['command','description','os']
	readonly_fields=[]
	fields =['command','description','os']

	'''if command already exists, make it readonly'''
        def get_readonly_fields(self, request, obj=None):
           if obj is None:
              return self.readonly_fields
	   else:
	      return self.readonly_fields + ['command']

#class NodeAdmin(admin.ModelAdmin):
class NodeAdmin(admin.ModelAdmin):
	change_form_template = 'admin/ncm/change_node.html'
	list_display= ['name','ip','transport','credentials','os']
	list_editable = ['ip','transport','credentials','os']
	search_fields=['name','ip']	
	def ping_node(self, request, obj=None):
	   if obj != None:
	      obj.ping_node()
	   return None
	ping_node.short_description="ping node"

class JobAdminForm(forms.ModelForm):
	class Meta:
     	   model = Job

	def clean(self):
           super(JobAdminForm, self).clean()
           nodes = self.cleaned_data['nodes']
           node_groups = self.cleaned_data['node_groups'] 
           if not nodes and not node_groups:
              raise forms.ValidationError("You must specify either a node or node group")
      	   return self.cleaned_data

class JobAdmin(admin.ModelAdmin):
	change_form_template = 'admin/ncm/change_job.html'
	list_display =['name','enabled','command','get_pretty_node_list','get_cron_string','last_run','next_run','error_button','output_button','run_button']
	actions=[disable_jobs,enable_jobs]
	filter_horizontal=['nodes','node_groups','subscribers']
	form = JobAdminForm
	readonly_fields = ['last_run']
	search_fields=['name','command__command','description','nodes__name','node_groups__name']
  	fieldsets =(
        ('General', {
            'classes': ('wide','title'),
            'fields': ('name','description','command','enabled')
        }),
        ('Devices', {
            'classes': ('wide','title'),
            'fields': ('nodes','node_groups')
        }),
        ('Scheduling', {
            'classes': ('wide','title'),
            'fields': ('minute','hour','day_of_month','month','day_of_week','last_run','next_run')
        }),
        ('Notification', {
            'classes': ('wide','title'),
            'fields': ('subscribers','notify_on_failure','notify_on_success')
        }),
        ('Advanced', {
            'classes': ('wide','title'),
            'fields': ('perform_diff','notify_on_diff')
        }),
	)


	def run_button(self, obj):
           on_click = "window.location='%d/run/?inline=1';" % obj.id
           return '<input type="button" onclick="%s" value="Run" />' % on_click
    	run_button.allow_tags = True
    	run_button.short_description = 'Run Now'
	
	def output_button(self,obj):
	   on_click = "window.location='/admin/ncm/output/?job__id__exact=%d';" %  obj.id
	   return '<input type="button" onclick="%s" value="View Outputs"/>' % on_click
	output_button.allow_tags= True
	output_button.short_description = "Output"

	def error_button(self,obj):
	   on_click = "window.location='/admin/ncm/output/?job__id__exact=%d&successful__exact=0';" %  obj.id
	   return '<input type="button" onclick="%s" value="View Errors"/>' % on_click
	error_button.allow_tags= True
	error_button.short_description = "Errors"

	def get_pretty_node_list(self,obj):
	   list_items_string=""
	   for node in obj.get_node_list():
	     list_items_string += "%s" %(node.name + " " + node.ip)
	   return "%s" %( list_items_string)
	get_pretty_node_list.allow_tags =True
	get_pretty_node_list.short_description = "Node list"

	'''if command already exists, make it readonly'''
        def get_readonly_fields(self, request, obj=None):
           if obj is None:
              return self.readonly_fields
	   else:
	      return self.readonly_fields + ['command']

	


class OutputAdmin(admin.ModelAdmin):
	'''removes "add object" button on index'''
	def has_add_permission(self,request):
	   return False
	change_form_template = 'admin/ncm/output_readonly.html'
	list_display =['job','performed_command','node','created_on','updated_on','successful','subscribers_notified']
	actions = [perform_diff,export_as_csv_action("Export to CSV", fields=['updated_on','job','performed_command','node','result'])]
	readonly_fields= Output._meta.get_all_field_names()
	list_filter=['job','updated_on','node','successful']
	fields=['updated_on','job','node','performed_command','successful','subscribers_notified','result']
	search_fields=['job__name','node__name','node__ip','performed_command__command','result']
	class Media:
           css = {
              "all": ("/static/syntax-highlighter/shCore.css","/static/syntax-highlighter/shThemeDefault.css")
           }
           js = ("/static/syntax-highlighter/shCore.js","/static/syntax-highlighter/shBrushCisco.js","/static/syntax-highlighter/activate.js")



class NodeGroupAdmin(admin.ModelAdmin):
 	change_form_template = 'admin/ncm/change_node_group.html'
	list_display =['name','get_pretty_node_list','parent']
	filter_horizontal=['nodes']
	list_filter=['parent','nodes']

        def get_pretty_node_list(self,obj):
           list_items_string=""
           for node in obj.get_node_list():
             list_items_string += "%s" %(node.name + " " + node.ip) + " , "
           return "%s" %( list_items_string)
        get_pretty_node_list.allow_tags =True
        get_pretty_node_list.short_description = "Node list"


class ChangeAdmin(admin.ModelAdmin):
	'''removes "add object" button on index'''
	def has_add_permission(self,request):
	   return False
	list_display = ['created','job','node','from_datetime','to_datetime']
	change_form_template = 'admin/ncm/change_readonly.html'
	readonly_fields= Change._meta.get_all_field_names()
	fields =['created','job','node','from_datetime','from_output','to_datetime','to_output','diff']
	list_filter=['job','node']
        class Media:
           css = {
              "all": ("/static/syntax-highlighter/shCore.css","/static/syntax-highlighter/shThemeDefault.css")
           }
           js = ("/static/syntax-highlighter/shCore.js","/static/syntax-highlighter/shBrushDiff.js","/static/syntax-highlighter/activate.js")

	

admin.site.register(Command, CommandAdmin)
admin.site.register(Credential)
admin.site.register(Node, NodeAdmin)
admin.site.register(NodeGroup, NodeGroupAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Output, OutputAdmin)
admin.site.register(Change, ChangeAdmin)
