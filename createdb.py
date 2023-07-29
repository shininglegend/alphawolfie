import psycopg2 as pgsql

conn = pgsql.connect("dbname=alphawolfie user=postgres password=password")
curr = conn.cursor()
curr.execute('SELECT MAX(id) FROM sparklechannels')
for row in curr:
    suggestionid = row[0]
suggestionid = int(suggestionid) + 1
id1=0
print(suggestionid)
while id1 != suggestionid:
    try:
        curr.execute('INSERT INTO sparklechannels (guild, channel, minScore, maxScore) VALUES (%s, %s, %s, %s)', (123454321, 23521634, 64, 532))
        print(f"Added for {id1}")
        conn.commit()
    except Exception:
        print(f'Failed for {id1}')
        conn.rollback()
    id1+=1

curr.execute('DELETE FROM sparklechannels WHERE guild = %s', (123454321,))
conn.commit()
conn.close()