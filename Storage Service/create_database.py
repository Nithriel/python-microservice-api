import sqlite3

conn = sqlite3.connect('reports.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE bug_report
          (id INTEGER PRIMARY KEY ASC, 
           title VARCHAR(100) NOT NULL,
           description VARCHAR(250) NOT NULL,
           location VARCHAR(50) NOT NULL,
           type VARCHAR(50) NOT NULL,
           date VARCHAR(100),
           date_created VARCHAR(100) NOT NULL)
          ''')

c.execute('''
          CREATE TABLE player_report
          (id INTEGER PRIMARY KEY ASC, 
           player_name VARCHAR(100) NOT NULL,
           description VARCHAR(250) NOT NULL,
           location VARCHAR(50) NOT NULL,
           type VARCHAR(50) NOT NULL,
           date VARCHAR(100),
           date_created VARCHAR(100) NOT NULL)
          ''')

conn.commit()
conn.close()
