import mysql.connector

db_conn = mysql.connector.connect(host="localhost", user="root",
password="P@ssw0rd", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
    CREATE TABLE bug_report
        (id INT NOT NULL AUTO_INCREMENT,
        title VARCHAR(100) NOT NULL,
        description VARCHAR(250) NOT NULL,
        location VARCHAR(50) NOT NULL,
        type VARCHAR(50) NOT NULL,
        date VARCHAR(100),
        date_created VARCHAR(100) NOT NULL,
        CONSTRAINT bug_report_pk PRIMARY KEY (id))
 ''')

db_cursor.execute('''
    CREATE TABLE player_report
        (id INT NOT NULL AUTO_INCREMENT,
        player_name VARCHAR(100) NOT NULL,
        description VARCHAR(250) NOT NULL,
        location VARCHAR(50) NOT NULL,
        type VARCHAR(50) NOT NULL,
        date VARCHAR(100),
        date_created VARCHAR(100) NOT NULL,
        CONSTRAINT player_report_pk PRIMARY KEY (id))
 ''')

db_conn.commit()
db_conn.close()