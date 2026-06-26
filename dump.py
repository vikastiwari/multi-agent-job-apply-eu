import sqlite3
import pprint
with sqlite3.connect('jobs.db') as conn:
    print('Evaluation Queue:')
    pprint.pprint(conn.execute('SELECT * FROM evaluation_queue').fetchall())
    print('Review Queue:')
    pprint.pprint(conn.execute('SELECT * FROM review_queue').fetchall())
