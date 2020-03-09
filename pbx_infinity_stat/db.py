import os
import psycopg2
import json
from psycopg2.extensions import AsIs 
from psycopg2 import sql
from dotenv import load_dotenv
import pandas as pd


#Загружаем переменные среды с файла
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

HOST     = os.environ.get('HOST')
PORT     = os.environ.get('PORT')
DBNAME   = os.environ.get('DBNAME')
USER     = os.environ.get('USER')
PASSWORD = os.environ.get('PASSWORD')

def get_ACDQueuesMembers():
	con_Configuration = psycopg2.connect( dbname= DBNAME, user= USER, password= PASSWORD, host= HOST, port= PORT)
	con_Security = psycopg2.connect( dbname= 'Cx_Security', user= USER, password= PASSWORD, host= HOST, port= PORT)

	# Create a Cursor object that operates in the context of Connection con:
	#cur = con.cursor(cursor_factory=RealDictCursor)
	cur = con_Configuration.cursor()
	cur_Security = con_Security.cursor()
	# Execute the SELECT statement:
	#cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
	t1 = AsIs('public."C_ACDQueuesMembers"')
	t2 = AsIs('public."U_Users"')
	sql1 = "select * from %s"
	cur.execute(sql1 , [t1])
	cur_Security.execute(sql1 , [t2])
	# Retrieve all rows as a sequence and print that sequence:
	#print(cur.fetchall())
	json_out = json.dumps(cur.fetchall())
	##json_out = json.dumps(cur_Security.fetchall())
	cur.close()
	cur_Security.close()
	sq_Users = pd.read_sql_query(
		'''
		select * from public."U_Users"
		'''
	, con_Security)
	sq_ACDQueuesMembers = pd.read_sql_query(
		'''
		select qm."IDACDQueue", qm."IDMember",
		case
			when qm."IDACDQueue" = 5000049053 then 'Колл-Центр (61-05-25)'
			when qm."IDACDQueue" = 5014846675 then 'Приём показаний (61-02-05)'
		end as "Name"
		from public."C_ACDQueuesMembers" as qm
		where qm."IDACDQueue" in (5000049053,5014846675)
		'''
	, con_Configuration)
	con_Configuration.close()
	con_Security.close()

	df_Users 			= pd.DataFrame(sq_Users)
	df_ACDQueuesMembers = pd.DataFrame(sq_ACDQueuesMembers)
	result = pd.merge(df_ACDQueuesMembers, df_Users, how='left', left_on='IDMember', right_on='ID')
	#result_groups = result.groupby('IDACDQueue').apply(lambda x: x.to_json(orient='records'))
	# print(sq_Users)
	# print(sq_ACDQueuesMembers)
	# print(result)
	#json_out = result_groups.to_json(orient='records')
	#json_out = result_groups.to_json()
	print( result )
	result_groups = result.groupby('Name')
	#Создаём словарь с данными для дальнейшего вывода в формате json
	json_out = {"CallGroups" : []}
	for name, group in result_groups:
		json_out["CallGroups"].append({"groupname" : name, "members" : group.to_json(orient='records')})
	
	json_out = json.dumps(json_out)
	return json_out

'''
SELECT 
  *
FROM "Cx_Configuration".public."C_ACDQueuesMembers" as aqm
JOIN "Cx_Configuration".public."C_ACDQueues" as aq on aqm."IDACDQueue" = aq."ID"
--JOIN ( SELECT * FROM dblink( 'dbname="Cx_Security"','select ID,Login,Name_F,Name_I,Name_O from public."U_Users"') as 
JOIN ( SELECT * FROM dblink( 'select ID,Login,Name_F,Name_I,Name_O from "Cx_Security".public."U_Users"') as 
uu(	"ID" bigint, 
	"Login" character varying(100),
	"Name_F" character varying(128),
	"Name_I" character varying(64),
	"Name_O" character varying(128)
)
) as uu on uu."ID" = aqm."IDMember"
WHERE aq."Name" = 'Прием показаний'
 ;



SELECT * FROM dblink( 'host=localhost port=10000 dbname="Cx_Security"','select ID,Login,Name_F,Name_I,Name_O from public."U_Users"') as 
uu(	"ID" bigint, 
	"Login" character varying(100),
	"Name_F" character varying(128),
	"Name_I" character varying(64),
	"Name_O" character varying(128)
)

'''