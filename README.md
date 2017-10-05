MailSnoopy
===================


Mail-snoopy (MS) — it is software for storage and filtering letters from many IMAP-accounts. Unlike usual mail clients, MS not fully synchronize mail with server. Synchronizing only letters receiving, not deleting or moving.  So, MS allow you collect and handle all incoming mail for full work time. At this time, other clients may delete letters from accounts, but MS will save it. 
This specificaly work is explained by pen-test destination. In some situations, pen-tester need to collect many thousands of letters from many accounts, and  filter some important information. 

MS contains two parts — cli and web. cli-part wrote on Python3 and need for server-side work. web-part wrote on Python3+Django and provide user visual interface (accounts editing, filters, mail view, etc).

Contributing by MIT license. 

cli-part installation
----------------------------
No hardware requirements. 
Software requirements:
- nix-like OS
- MySQL 5+
- Python3-packages: mysql.connector, imapclient.
Unpack MS-cli. Make directories for attachments and letters bodies. Edit config.ini.  

web-part installation
-----------------------------
No hardware requirements. 
Software requirements:
- nix-like OS
- MySQL 5+
- Python3-packages: bs4, django, mysqlclient, django-cors-headers, django-tastypie, django-angular.
- Apache2 or other web-server which may work with Django.

If you want, after unpacking MS-web and install need packages, you may start Django debug web-server (./manage.py runserver) and start work. 
If need setup single web-server, see example below or read Django docs for your web-server. 

Mysql configuration may be found in my.cnf file. Directories for attachments and letters bodies you may specify in  ATTACHMENTS_PATH and BODIES_PATH variables in bottom of  mailsnoopyweb/settings.py file. 

After installation, you may find main page on URL http://HOST/msw/index/

Installation example in «clean» Ubuntu 16.04
----------------------------------------------------------------
    apt-get install mysql-server libmysqlclient-dev apache2 git python3-dev python3-pip python3-venv python3-django python3-django-uwsgi libapache2-mod-wsgi-py3 
Unpacking ms-web. Put it to /var/www/msw/. Go to /var/www/msw/ and make virtualenv:

    python3 -m venv myvenv

Activate it:

        source myvenv/bin/activate

Install python3 packages:

        pip3 install wheel
        pip3 install mysqlclient bs4
        pip3 install django django-cors-headers django-tastypie django-angular

Open /etc/apache2/sites-available/000-default.conf and put in bottom:

    WSGIScriptAlias / /var/www/msw/mailsnoopyweb/wsgi.py
    WSGIPythonPath /var/www/msw/:/var/www/msw/myvenv/lib/python3.5/site-packages/
    WSGIDaemonProcess example.com python-home=/var/www/msw/myvenv python-path=/var/www/msw/
    WSGIProcessGroup example.com

	Alias /static/ /var/www/msw/static/
	<Directory /var/www/msw/static>
	Require all granted
	</Directory>

Open file  mailsnoopyweb/settings.py and in variables  ATTACHMENTS_PATH and BODIES_PATH specify directories for attachments and letters bodies. 
In ALLOWED_HOSTS  put hostname which you will use. 
Restart web-server and open URL http://HOST/msw/index/

Work scheme
--------------------
Once in specified interval, MS check mail accounts for relevance. If authentification can't be done, MS write message about it and deactivate account. For activate account you mast change password or mark checkbox «Active» in web-part. 
If authentification is success, MS refresh folders list of every account. After that, for every folder MS get new mail. New mail getting by UIDs difference between server-side and MS-side. So, if some letter can't be received (connection troubles, etc) it will be received in next time. 
Every letter, in receiving process, will be parse of all filters. Matches will put to database and you can see it in web-part. Letters bodies and attachments put in HDD as usual files. 
If you make new filter, MS work with it for all letters from database. 

Filters
---------
Filters separates by types and targets. Types:

 - Search by phrase (substring) 
 - Search by regexp (PCRE)

Targets:

 - Subject 
 - Content 
 - From/To (email and name) 
 - Attachments (file name and mime-type)

Attachments
---------
All loaded attachments saves in directory on HDD with unique name. You can work with them by web-part. Attachments can be loaded from single letter, or from common extensions list.  

Logs
------
cli-part write logs in «logs»-directory. Inside it MS create sub-dirs with date of current day. In this sub-dirs you may find next files:

 - ex.log — log of unhandled exceptions. I be grateful if you post it as bug-report. 
 - err.log — errors log. For example, account can`t login. 
 - info.log — usual information. For example, letter successfully fetched.  
 - out.log — all output (all other logs summary)

Limitations and warnings
------------------------------------
MS was create how pet-project and training area for acquaintance with Django and AngularJS. If you are specialist of this frameworks, don't look in source codes. It`s may be dangerous for you mind. 

MS has troubles with parsing letters which has rare encodings, such as koi8-r or cp866. May be, it will be fixed in future.

Author / Links
--------------------
Kuzmin Anton http://anton-kuzmin.ru (ru) http://anton-kuzmin.pro (en)
 

