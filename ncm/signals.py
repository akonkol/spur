from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.conf import settings

def email_subscribers(sender, instance, *args, **kwargs):
	obj_type = instance.__class__.__name__
	obj_url = "spur.spencerstuart.com" + reverse('admin:%s_%s_change' %(instance._meta.app_label,obj_type.lower()),args=(instance.id,))
	obj_url_tag = "<a href='http:\/\/%s'>%s</a>" %(obj_url,obj_url)
	recipients =[]
	status= None
	for user in instance.job.subscribers.all():
	   recipients.append(user.email)

   	if obj_type == "Output":
      	   if instance.job.notify_on_success or instance.job.notify_on_failure:
              status = None

           if instance.successful and instance.job.notify_on_success:
              status = "COMPLETED"
           if not instance.successful and instance.job.notify_on_failure:
              status = "FAILED"

	   subj_line = "[%s] Task %s > %s " %(status , instance.job, instance.node.name)
           text_body = instance.result

   	if obj_type =="Change":
      	   if instance.job.notify_on_diff:
              status = "CHANGE"
              subj_line = "[%s] %s > %s " %(status,instance.job, instance.node.name)
              text_body = instance.diff

   	if status:
           html_description="This %s was created by issuing %s to %s, you can see the full %s at %s" %(
				obj_type.lower(),instance.job.command.command,instance.node,obj_type.lower(), obj_url_tag
		 	  )
           text_description="This %s was created by issuing %s to %s, you can see the full %s at %s" %(
				obj_type.lower(),instance.job.command.command,instance.node,obj_type.lower(), obj_url
		 	  )
	  
	   html_body = "%s <br/><br/><pre>%s</pre>" %(html_description, text_body) 
	   text_body += text_description
	   
           try:
	      msg = EmailMultiAlternatives(subj_line,text_body,settings.DEFAULT_EMAIL_FROM,recipients)
	      msg.attach_alternative(html_body, "text/html")
	      msg.send()
              instance.subscribers_notified =True
           except Exception, e:
              instance.subscribers_notified =False
              print str(e)
     	else:
           instance.subscribers_notified=False
