import datetime
from django.core.urlresolvers import reverse
from django.db.models.loading import get_model
from django import template
from ncm.models import * 

register = template.Library()

@register.assignment_tag(name="recent_objects")
def recent_objects(model, count, order_by=None):
	obj_model = get_model('ncm',model)
	objects = obj_model.objects.all().order_by(order_by)[:count]
	return objects


@register.tag('make_table')
def do_make_table(parser, token):
    try:
        tag_name, object_list, caption, field_list = token.split_contents()
	field_list = field_list.replace('\"','')
	field_list = field_list.split(",")
	caption = caption.replace('\"','')
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly three arguments" % token.contents.split()[0])
    return MakeTable(object_list,caption, field_list)

class MakeTable(template.Node):
    def __init__(self, object_list,caption, field_list):
        self.object_list = template.Variable(object_list )
	self.field_list = field_list
	self.caption = caption

    def render(self, context):
        try:
	    object_list = self.object_list.resolve(context)
	    if len(object_list) < 1:
	       return ''
	    if self.field_list[0] == "*" and object_list:
	       self.field_list = object_list[0]._meta.get_all_field_names()
	
	    th_fields=[]
	    for field in self.field_list:
	       th_fields.append(field.replace("_"," "))

	    tr_rows =[]
	    for obj in object_list:
	      td_list=[]
	      for field in self.field_list:
		this_field={}
		value = obj.__getattribute__(field.replace("'",""))
		if isinstance(value,datetime.datetime):
		   field_type="date"
		else:
		   field_type="text"
		if field == self.field_list[0]:
		   key = True
		   url = reverse('admin:%s_%s_change' %(obj._meta.app_label,obj.__class__.__name__.lower()), args=(obj.id,) )
		else:
		   url = None
		   key = False

		this_field = {'type':field_type,'value':value,'key':key,'url':url}
		td_list.append(this_field)
	      tr_rows.append(td_list)

	    t = template.loader.get_template('admin/ncm/make_table.html')
	    c = template.Context({'caption':self.caption,'th_fields':th_fields,'tr_rows':tr_rows})
	    rendered = t.render(c)
	    return rendered 
        except template.VariableDoesNotExist:
            return ''


@register.assignment_tag(name="get_recent_errors")
def get_recent_errors():
   err_outputs = Output.objects.filter(successful=False).order_by('-created_on')[:5]
   return err_outputs


@register.assignment_tag(name="get_related")
def get_related(*args, **kwargs):
   parent_obj = args[0]
   model_names = args[1].split(',')
   links=[]
   related_objects=[]
   for rel in parent_obj._meta.get_all_related_objects():
      if rel.model.__name__ in model_names:
         links.append(rel.get_accessor_name())
   for link in links:
      objects = getattr(parent_obj,link).all()
      for obj in objects:
         related_objects.append(obj)
   return related_objects 
