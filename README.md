Bind9-with-mysql-based-configuration
====================================

This document summarizes  how to install and configure Bind9, with a MySQL database as backend instead of configuration files. The repo contains also a simplified API to connect with the DNS via webservices and change its configuration remotely (add Zone, delete zone ...). The API was created for testing purpuses.

Why? 
Working  on a Domain name server means that you will be frequently editing configuration files. As a consequence you need to restart the server each time you modify or change parameters in these files. Moving to a MySQL-based-configuration is a better solution to avoid this flip out. Instead of working on Configuration files, all records will be saved on a database and  then easily updated and accessed via simple Mysql queries. Restartig the sever is no more required every time the congfigration is updated. 

 
##Steps:
**To prepare the environment and install the missing packages on ubuntu, please follow the steps below**

1/ Install mysql:
<pre>
	sudo apt-get install mysql-client mysql-server libmysqlclient-dev
</pre>


2/ install openSSL
<pre>
	sudo apt-get install libssl-dev
	sudo apt-get install openssl
</pre>


**Environment configuration**

3/ Restrict the MySQL daemon to localhost
<pre>
	cd /etc/mysql
	sudo vi my.cnf
</pre>

4/ add this to the configuration file 
<pre>
	bind-address=127.0.0.1
</pre>

5/ restart database server and apply changes
<pre>
service mysqld restart
</pre>

6/Create a database and proceed with the security process
<pre>
	mysql -u root -p
	create database zones;
</pre>

7/install Bind9 package (source code)
<pre>
	wget ftp://ftp.isc.org/isc/bind9/cur/9.7/bind-9.7.7.tar.gz
</pre>

8/ Download the latest version BIND/MySQL SDB driver from the official website (http://mysql-bind.sourceforge.net/)

9/ Extract both files
<pre>
	tar xzf bind-9.7.7.tar.gz
	tar xzf mysql-bind.tar.gz
</pre>



10/Deploy the driver in the right directories
<pre>
	cp mysql-bind/mysqldb.c bind-9.7.7/bin/named/
	cp mysql-bind/mysqldb.h bind-9.7.7/bin/named/include/
</pre>



11/ editing the make file :
<pre>
	cd bind-9.7.7/bin/named/
	vi Makefile.in
</pre>

Make these changes:
<pre>
DBDRIVER_OBJS = mysqldb.@O@
DBDRIVER_SRCS = mysqldb.c
</pre>

12/In the latter file :
check the message returned by this command (Hopefully it does return something if you really followed the steps above :p ) 
<pre>
	mysql_config --cflags
</pre> 
and copy/paste it in the file **[DBDRIVER_INCLUDES = (Paste here)]**

13/In the same file :
check the message returned by this command  
<pre>
	mysql_config --libs 
</pre> 
and copy/paste it in the file  **[DBRIVER_LIBS = (Paste here)]**

14/Add driver's include into Bind's code
<pre>
	sudo vi main.c
</pre>

add this header
**#include "mysqldb.h"**

also search for '**ns_server_create**' and add **mysqldb_init** just before
<pre>
	mysqldb_init();
	ns_server_create(ns_g_mctx, &ns_g_server);
</pre>


also search for '**ns_server_destroy**' and add mysqldb_clear just after
<pre>
	ns_server_destroy(&ns_g_server);
	mysqldb_clear();
</pre>

15/Change include Statement in the same directory
<pre>
	vi mysqldb.c
</pre>

change,
**#include <named/mysqldb.h>**
by
**#include "include/mysqldb.h"**


16/Compile the customized version of Bind9 via the command line
<pre>
   ./configure
	make clean
	make
	make install
</pre>



17/ Create the configuration file and use the API to configure the server
<pre>
	sudo touch /etc/named.conf
</pre>



PS: to launch the server after configuration use this command :
<pre>
	sudo /usr/local/sbin/named
</pre>





 



