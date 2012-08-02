import csv
from django.http import HttpResponse
from django.shortcuts import render_to_response

def export_as_csv_action(description="Export selected objects as CSV file",
                         fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """
    def export_as_csv(modeladmin, request, queryset):
        """
        Generic csv export admin action.
        based on http://djangosnippets.org/snippets/1697/
        """
        opts = modeladmin.model._meta
        field_names = set([field.name for field in opts.fields])
        if fields:
            fieldset = set(fields)
            field_names = field_names & fieldset
        elif exclude:
            excludeset = set(exclude)
            field_names = field_names - excludeset

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')

        writer = csv.writer(response, quoting = csv.QUOTE_ALL)
        if header:
            writer.writerow(list(field_names))
        for obj in queryset:
	    values=[]
	    for field in field_names:
	       value = getattr(obj, field)
	       value = str(value)
	       value = value.encode('unicode-escape')
	       values.append(unicode(value).encode("utf-8"))
            writer.writerow(values)
        return response
    export_as_csv.short_description = description
    return export_as_csv

def perform_diff(modeladmin, request, queryset):
	opts = modeladmin.model._meta
	count = queryset.count()
	if count !=2:
	   raise Exception("You can only compare 2 outputs")
	else:
	   
	   from_output = queryset[0]
	   to_output = queryset[1]
           import difflib
   	   d = difflib.HtmlDiff()
           table = d.make_table(from_output.result.splitlines(), to_output.result.splitlines(),
                             "%s<br/>%s<br/>%s" %(from_output.job.command.command,from_output.node,from_output.updated_on),
                             "%s<br/>%s<br/>%s" %(to_output.job.command.command,to_output.node,to_output.updated_on))
	   return render_to_response("admin/ncm/full_diff.html",{'diff':table})

	perform_diff.short_description = description

def disable_jobs(modeladmin, request, queryset):
	queryset.update(enabled=False)
	disable_jobs.short_description ="Disable selected jobs"

def enable_jobs(modeladmin, request, queryset):
	queryset.update(enabled=True)
	disable_jobs.short_description ="Enable selected jobs"
