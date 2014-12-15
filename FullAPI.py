
from bottle import *
import MySQLdb
import json
import sys
import os
#Connection to the zones database
#To edit mysql connection parameters, edit the following variable
Connection = MySQLdb.connect(host ='127.0.0.1', user= 'root', passwd='wicem', db= 'zones')



##############################################################################
#################Zones Funtions#############################################



#get_db_name:this function is used to get the Database table name from a zone name
def get_db_name(zone):
        table = list(zone)
        index = zone.find(".")
        table[index]= "_"
        ZoneDB = "".join(table)
	return ZoneDB



@post('/addZone')

def AddNewZone():
	Values = request.json

#Data parsing
	Zone=Values["Zone"]
	Notify = Values["Notify"]
	Type = Values["Type"]
	ZoneDB = get_db_name(Zone)
 	DBUSER = Values["DBUSER"]
	DBPASS = Values["DBPASS"]
#Modify the configuratiion file
	try:
		with open("/etc/named.conf", "a") as f:
     			f.write("\n\nzone "+Zone+" {\n")
			f.write("type "+Type+"; \n")
			f.write("notify "+ Notify+";\n")
			f.write('''database "mysqldb zones '''+ZoneDB+''' 127.0.0.1 '''+DBUSER+''' '''+ DBPASS +'''"; \n } ;''')
	
			print "done with conf file" 
	except:
		
		return {"Error": str(sys.exc_info()[0]) }
#Connection to database
	cursor=Connection.cursor()
#insert a new line in the database
	try:
		Querry="create table "+ ZoneDB + " (id MEDIUMINT NOT NULL AUTO_INCREMENT Primary Key, name varchar(255) default NULL,ttl int(11) default NULL,rdtype varchar(255) default NULL,rdata varchar(255) default NULL) Engine=MyISAM;"
		cursor.execute(Querry)
		cursor.close()
	except MySQLdb.Error, e:
		return {"Error "+str(e.args[0])+" " :e.args[1]}
		
	return { "Message": Zone+" was added to BIND Database"}


@post('/deleteZone')
def DeleteZone():
	Values = request.json
	ZoneName= Values["Zone"]
	output = []
	i=0	
	#Delete the zone name from the configuration file("/etc/nemed.conf"):
	try: 
		with open("/etc/named.conf", "r") as f:
			
    			start = "zone "+ ZoneName
			for line in f:
				if not line.startswith(start) and (i == 0 or i>5)  :
        				output.append(line)
				else:
					i += 1
		f = open("/etc/named.conf", "w")
		f.writelines(output)
		f.close()
		print "Deleted from configuration file"
	except:
		return {"Message": str(sys.exec_info()[0])}
				
	#Connection to database
        cursor=Connection.cursor()
	#Delete from Database
        try:
                Querry="drop table "+ get_db_name(ZoneName)+";"
                cursor.execute(Querry)
		cursor.close()
	except MySQLdb.Error, e:		
		return {"Error"+str(e.argv[0])+" ":e.argv[1] }
	
	return {"Message": ZoneName+" Succefully deleted from BIND Database"}



@post('/updateZone')
def updateZone():
	values=request.json
	zone = values["Zone"]
	field = values["Field"]
	value= values ["Value"]
	
	#reset counter
	i=0
	try:
		with open("/etc/named.conf", "r") as f:
			temp= open("/etc/named.conf.temp","w+a")
			start = "zone "+str(zone)
			line = f.readline() 
			while line:
				if line.startswith(start) or (i != 0 or i<5):
					if line.startswith(field):
						aux= field+" "+value+";\n"
						temp.write(aux)
						i=5
					else:
						temp.write(line)
						i+=1
						#pdb.set_trace()
				else:
					temp.write(line)
				line = f.readline() 


				
		temp.close
		os.remove("/etc/named.conf")
		os.rename('/etc/named.conf.temp','/etc/named.conf')
		return {"Message":"Successful update on "+ str(zone) }
	except:
		return {"Message":"Error while updating the file" }


@post('/checkZoneDetails')
def checkZoneDetails():
	zone=request.json
	zone_name= zone["Zone"]
	#Get Zone Name 
	start = "zone "+str(zone_name)
	zoneDetails = {}

	try:
		#open configuration file and retrieve zone details
		with open("/etc/named.conf", "r") as f:
			line = f.readline()
			while line:
				if line.startswith(start):
					values= line.split()
					zone= values[1]
					line = f.readline()
					values= line.split()
					typ = values[1]
					line = f.readline()
					values= line.split()
					notify = values[1]
					line = f.readline()
					values= line.split("\"")
					database = values[1]
					zoneDetails.update({
					zone :{
						"type": typ.split(";")[0],
						"notify": notify.split(";")[0],
						"database": database.split(";")[0],
								}
					})
					
				else:
					line = f.readline()
			return zoneDetails
	except:
		return {"error":"error while opening file"}
		
#This function returns the zone name from a database name
def get_zone_name(zone):
        table = list(zone)
        index = zone.find("_")
        table[index]= "."
        ZoneName = "".join(table)
	return ZoneName


@get('/showZones')
def show():
#transform the domain name to a database name
    cursor=Connection.cursor()
    

#Execute database querry 
    try:
    	cursor.execute("show tables;" )
    	rows = cursor.fetchall()
    	Zones={}
    	i=1
    	if rows:
     		for row in rows:
       			zone_name = row[0]
       			zone_name = get_zone_name(str(zone_name))
       			Zones.update({
     			 	"zone "+ str(i): {
               		 	"zone name" : zone_name,
							}
      			 })
      			i+=1
	#Return Results
    	return Zones
    except MySQLdb.Error, e:
	return {"Error "+ str (e.args[0])+ "":e.args[1]}
	
	
	
	
 
##############################################################################
#################Records Funtions#############################################

@post('/addRecord')
def insert():
	Data = request.json

#Data parsing 
	zone = Data["Zone"]
	#table = list(Zone["DN"])
    #	index = Zone["DN"].find(".")
    #	table[index]= "_"
    #	DN = "".join(table)
	zone = get_db_name(zone)
  	name = Data["name"]
	ttl = Data["ttl"]
	rdtype = Data["rdtype"]
	rdata = Data["rdata"] 

#Connection to database
	cursor=Connection.cursor()
#insert a new line in the database
	try:
		Querry = "insert into " + zone + " values (NULL, '" + name +"',"+ ttl + " , '" +rdtype+"','" + rdata +"');"
		cursor.execute(Querry)
		cursor.close()
	except MySQLdb.Error, e:
		return {"Error "+str(e.args[0])+" " :e.args[1]}
		
	return { "Message": name +" added to the Database"}


@post('/checkRecord')
def showRecord():
    Record = request.json
    item = get_db_name(str(Record["Zone"]) )
    Name = Record["Name"]
#Execute database querry 
    cursor=Connection.cursor()
    try:
    	Querry="SELECT * from "+ item+" where name ='"+Name+"';"
	cursor.execute(Querry)
    	rows = cursor.fetchall()
    	domains={}
    	if rows:
     		for row in rows:
       			ids , name, ttl, rdtype, rdata = row
       			domains.update({
     			 	name: {
               		 	"id" : ids,
               		 	#"name": name,
			 	"ttl": ttl,
			 	"rdtype": rdtype,
			 	"rdata": rdata,


           		     }
      			 })
	#Return Results
    	return domains
    except MySQLdb.Error, e:
		return {"Error "+ str (e.args[0])+ "":e.args[1]}


@post('/deleteRecord')

def deleteRecord():
	Values = request.json

#Data parsing
	
	zone = get_db_name(str(Values["Zone"]))
	Id = Values["Id"]

#Connection to database
	cursor=Connection.cursor()
#insert a new line in the database
	try:
		Querry="Delete from "+zone+" WHERE id = "+Id+";"	
		cursor.execute(Querry)
		cursor.close()
	except MySQLdb.Error, e:
		return {"Error "+str(e.args[0])+" " :e.args[1]}
		
	return { "Message": "Record deleted"}
	
@post('/updateRecord')

def updateRecord():
	NewValues = request.json

#Data parsing

	zone = get_db_name(str(NewValues["Zone"]) )
	Id = NewValues["Id"]
  	Field = NewValues["Field"]
	Value = NewValues["Value"] 

#Connection to database
	cursor=Connection.cursor()
#insert a new line in the database
	try:
		Querry="UPDATE "+zone+" SET "+Field+"="+Value+" WHERE id = "+Id+";"	
		cursor.execute(Querry)
		cursor.close()
	except MySQLdb.Error, e:
		return {"Error "+str(e.args[0])+" " :e.args[1]}
		
	return { "Message":"Record Updated"}


@get('/show/<item>')
def show(item = "wicem_com"):
    
	item = get_db_name(str(item))

	#connection to database
	cursor=Connection.cursor()
	cursor.execute("SELECT * from " + item )
	rows = cursor.fetchall()

	#Records will contain all all the records related to the zone mentioned above (Variable item)
	Records={}

	  
	if rows:


		 for row in rows:
			ids , name, ttl, rdtype, rdata = row
			Records.update({
				 name: {
					 "id" : ids,
					 "name": name,
			 "ttl": ttl,
			 "rdtype": rdtype,
			 "rdata": rdata,
					 }
				 })
	return Records
run(host='192.168.1.211', port=8080, debug=True, reloader=True)
