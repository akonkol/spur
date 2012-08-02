from django import forms
from ncm.models import Node, Credential
import csv

class NodeImportForm(forms.Form):
   file = forms.FileField()

   def save(self):
      records = csv.reader(self.cleaned_data["file"])
      for line in records:
         try:
            known_os = OperatingSystem.objects.get(name= line[2])
            os = known_os
         except :
            os = None

         try:
            node_exists = Node.objects.get(ip= line[1])
         except:
            input_node = Node()
            input_node.name = line[0]
            input_node.ip = line[1]
            input_node.os = os
            input_node.transport = line[3]
	    input_node.credential = default_creds
            input_node.save()
