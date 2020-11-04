import sqlite3

conn = sqlite3.connect('reports.sqlite')

c = conn.cursor()
c.execute('''
          DROP TABLE bug_report;
          ''')
c.execute('''
          DROP TABLE player_report;
          ''')
conn.commit()
conn.close()
