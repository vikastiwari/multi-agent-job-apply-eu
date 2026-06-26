import sqlite3
with sqlite3.connect('jobs.db') as conn:
    conn.execute('DELETE FROM evaluation_queue')
    conn.execute('DELETE FROM review_queue')
    conn.commit()
print("Database cleared.")
