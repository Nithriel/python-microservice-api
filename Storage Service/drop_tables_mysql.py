import mysql.connector

db_conn = mysql.connector.connect(host="ec2-18-236-217-32.us-west-2.compute.amazonaws.com", user="root",
password="password", database="events", port= 3306)

db_cursor = db_conn.cursor()

db_cursor.execute('''
 DROP TABLE bug_report, player_report
''')

db_conn.commit()
db_conn.close()