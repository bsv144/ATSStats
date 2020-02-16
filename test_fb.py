import fdb

fdb.load_api("./fbclient.dll")
con = fdb.connect(dsn='192.168.1.40:c:/Program files (x86)/Inteltelecom/Infinity contact-center/servers/serverBD/Data/INFDATA.DAT', user='INFINITYUSER', password='wizard')

# Create a Cursor object that operates in the context of Connection con:
cur = con.cursor()

# Execute the SELECT statement:
cur.execute("select first 1 * from I_STATISTICS_CALL_INNER")

# Retrieve all rows as a sequence and print that sequence:
print(cur.fetchall())