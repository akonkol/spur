#/usr/bin/env python
import pexpect
import Systems 
import sys
import re

def to_raw_string(s):
	if isinstance(s,str):
	   s = s.encode('string-escape')
	if isinstance(s,unicode):
	   s = s.encode('unicode-escape')
	return s

class SessionError(Exception):
	pass


class Session:

	def __init__(self, host, port, proto, operatingsystem):
		self.host = host
		self.proto = proto
		self.port = port
		self.operatingsystem = operatingsystem
		self.connected = False

	def __str__(self):
		return self.host +":"+ str(self.port) + " via " + self.proto

	def __telnet_login__(self,connection_args):
		self.connection = pexpect.spawn(connection_args,timeout=10) # spawns session
		
		i = self.connection.expect([r"(?i)(username|login)[\s:]+",r"uthentication failed.",pexpect.TIMEOUT]) #assigns int to match 
		if i==0: #matched username
			self.connection.sendline(self.username)
			i = self.connection.expect(r"(?i)password[\s:]+")
		if i==0: #matched password
			self.connection.sendline(self.password)
			i = self.connection.expect(self.operatingsystem.PROMPTLINE)
			if i ==0: #matched promptline
				if self.operatingsystem.PAGINATES: # if OS paginates, disable it
					self.connection.sendline(self.operatingsystem.DISABLE_PAGINATION)
					i = self.connection.expect(self.operatingsystem.PROMPTLINE)
				if i==0:
					self.connected = True
					return True 
		if i==0:
			raise SessionError("Connection Timed out")
		else:
			self.connected = False
			return False

	def __ssh_login__(self, connection_args):
		self.connection = pexpect.spawn(connection_args,timeout=10)

		i = self.connection.expect(["(?i)are you sure you want to continue connecting","(?i)password","Host key verification failed.",pexpect.TIMEOUT])

		if i==0: # matches the new key warning
			print "got a new key"
			self.connection.sendline("yes")
			i = self.connection.expect(r"(?i)password[\s:]+")
		 	if i==0:
			   '''we got the new key, continue with process'''
			   i=1

		if i==1: # matches password prompt
			self.connection.sendline(self.password)
			i = self.connection.expect(self.operatingsystem.PROMPTLINE)
			if i==0: # we should be logged in.
				if self.operatingsystem.PAGINATES:
					self.connection.sendline(self.operatingsystem.DISABLE_PAGINATION)
					i = self.connection.expect(self.operatingsystem.PROMPTLINE)
				if i==0:
					self.connected = True
					return True
		if i==2:
			print "before: " + self.connection.before 
			print "after: " + self.connection.after
			raise SessionError("Key Mismatch " + self.connection.before)

		if i==3:
			raise SessionError("Connection Timed out")	
		else:
			pass


	def login(self, username, password):
		self.username = username
		self.password = password

		spawn_cmd =''

		if self.proto =="telnet":
			connection_string = 'telnet -K %s %d' % (self.host, self.port)
			self.__telnet_login__(connection_string)
		elif self.proto =="ssh":
			connection_string = 'ssh -o Port=%d -l %s %s' % (self.port, self.username, self.host)
			self.__ssh_login__(connection_string)
		else:
			pass
		if self.connected:
			return True

	def logout(self):
		self.connection.sendline("exit")
		self.connection.close()
		self.connected = False

	def sendcommand(self,cmd): # sends command, returns list of results
		if self.connected:
			self.connection.sendline(cmd)
			#self.connection.expect(to_raw_string(cmd))
			self.connection.expect(re.escape(cmd))

			self.connection.expect(self.operatingsystem.PROMPTLINE)
			#print "***", self, cmd + " yielded: *** "
			if len(self.connection.after) > 0:
				idx = self.connection.before.rfind("\r\n")
				#print self.connection.before[:idx]
				self.connection.before = self.connection.before[:idx]
				if "Invalid" in self.connection.before:
			           raise SessionError("***INVALID COMMAND***" + str(self.connection.before))
				
			else:
				print self.connection.before

			return self.connection.before.strip()
		else:
			sys.stderr.write("***Could not connect to %s" %(self.host) )
			raise SessionError("***Not Connected***")


	def getconfig(self):
		if self.connected:
			self.sendcommand(self.operatingsystem.GET_CONFIG)
		else:
			raise SessionError("***Not Connected***")
	
	def getversion(self):
		if self.connected:
			self.sendcommand(self.operatingsystem.VERSION)
		else:
			raise SessionError("***Not Connected***")

	def escalateprivileges(self, escalated_password=None):
		escalated_password = escalated_password
		if self.connected:
			self.connection.sendline(self.operatingsystem.ESCALATE_COMMAND)
			i = self.connection.expect(r"(?i)password[\s:]+")
			if i==0:
				self.connection.sendline(escalated_password)
       		 		i = self.connection.expect(self.operatingsystem.PROMPTLINE)
				if i==0:
					if("denied" in self.connection.before):
					   raise SessionError("***Escalation Failed***")
		else:
			raise SessionError("***Not Connected***")


