BIND9 with MySQL based configuration


	This document summarizes  how to install and configure Bind9, with a MySQL database as backend instead of configuration files.

	Why ? Working  on a Domain name server means that you will be frequently editing configuration files. As a consequence you need to restart the server each time you modify or change parameters in these files. Moving to a MySQL Database Backend is a perfect solution to avoid this. Instead of working on Configuration files, all records will be saved on a database and easily updated and accessed via Database queries. No need to restart the server once a modification was done. 

 
	Steps:
---install missing packages

1/ Install mysql:

sudo apt-get install mysql-client mysql-server libmysqlclient-dev


2/ install openSSL
sudo apt-get install libssl-dev
sudo apt-get install openssl

---configuration

3/ Restrict the MySQL daemon to localhost
cd /etc/mysql
sudo vi my.cnf

4/ add this to the configuration file 
bind-address=127.0.0.1

5/ restart database server and apply changes
service mysqld restart

5/Create a database and proceed with the security process
mysql -u root -p
create database zones;

6/install Bind9 package (source code)
wget ftp://ftp.isc.org/isc/bind9/cur/9.7/bind-9.7.7.tar.gz

7/ Get the latest version BIND/MySQL SDB driver from the official website (http://mysql-bind.sourceforge.net/)

8/ Extract both files
tar xzf bind-9.7.7.tar.gz
tar xzf mysql-bind.tar.gz


9/Deploy the driver in the right directories
cp mysql-bind/mysqldb.c bind-9.7.7/bin/named/
cp mysql-bind/mysqldb.h bind-9.7.7/bin/named/include/


10/ editing the make file :
cd bind-9.7.7/bin/named/
vi Makefile.in

change,
DBDRIVER_OBJS = mysqldb.@O@
DBDRIVER_SRCS = mysqldb.c


11/In the same file :
check what returns [ mysql_config --cflags ]
and copy/paste it to [DBDRIVER_INCLUDES = (Paste here)]

12/In the same file :
check what returns [ mysql_config --libs ]
and copy/paste it to [DBRIVER_LIBS = (Paste here)]

13/Add driver's include into Bind's code
sudo vi main.c

add,
#include "mysqldb.h"

also search for 'ns_server_create' and add mysqldb_init just before,
mysqldb_init();
ns_server_create(ns_g_mctx, &ns_g_server);

also search for 'ns_server_destroy' and add mysqldb_clear just after,
ns_server_destroy(&ns_g_server);
mysqldb_clear();


14/Change include Statement in the same directory

vi mysqldb.c

change,
#include <named/mysqldb.h>,
by,
#include "include/mysqldb.h"


15/compile Bind9

   ./configure
make clean
make
make install


16/ Create the configuration file and use the API to configure the server

sudo touch /etc/named.conf





PS: to launch the server after configuration use this command :
sudo /usr/local/sbin/named





 


