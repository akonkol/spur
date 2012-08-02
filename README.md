# Spur Setup #

Spur is a web based network configuration manager. It allows you to ssh or telnet to any device and run commands through a web front-end. The results of these commands are stored and can be diff'd. Emails can be sent when there is a diff if you want.

## System Requirements ##

### Python ### - simply type "which python" in a command prompt to see if python is installed
---

### Django 1.4 ###- 

wget http://www.djangoproject.com/m/releases/1.4/Django-1.4.1.tar.gz

tar xzvf Django-1.4.1.tar.gz

cd Django-1.4.1

sudo python setup.py install

---

sqlite, mysql, postgres -  I suggest running sqlite if you don't want to setup a daemon style db

sudo apt-get install sqlite


##Python Requirements

django-mptt - 

sudo easy_install django-mptt
---

pexpect - 

sudo easy_install pexpect 
---

##Spur Instalattion

Once you've met the system and python requirements, grab a copy of spur

wget use.io/spur/spur.tar.gz

tar xvzf spur.tar.gz

cd spur

vi spur/spur_settings.py #edit this file to match your enviornment

python manage.py syncdb #create an admin user

python manage.py runserver 0.0.0.0:8000

Create a cronjob for spur

crontab -e

* * * * * /path/to/spur/manage.py spur-cron

Browse to spur http://your_fqdn_or_ip:8000
