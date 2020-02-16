import psycopg2
from psycopg2.extensions import AsIs 
from psycopg2 import sql

HOST     = ''
PORT     = ''
DBNAME   = ''
USER     = ''
PASSWORD = ''

con = psycopg2.connect( dbname= DBNAME, user= USER,
                        password= PASSWORD, host= HOST, port= PORT)


# Create a Cursor object that operates in the context of Connection con:
cur = con.cursor()

# Execute the SELECT statement:
#cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
t1 = AsIs('public."C_ACDQueuesMembers"')
sql = "select * from %s"
cur.execute(sql , [t1])
# Retrieve all rows as a sequence and print that sequence:
print(cur.fetchall())

cur.close()
con.close()


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