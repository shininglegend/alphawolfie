import sqlite3

con = sqlite3.connect('data1.db')
cur = con.cursor()
#db['reactions']={"wolfie": "755447204654874696", "wingy": "771542730916364338", "ereg": "827739388058140713", "wolfy": "844992590361526272", "wofy": "844992590361526272", "marsh": "826259233309196348", "dasani": "834052568271159297", "delta": "792770838113026058", "pog": "706201125275303950", "andokrin": "762753253016338512", "jeff": "767221910374318150"}

cur.execute('CREATE TABLE sparklesc(userid INTEGER, serverid INTEGER, score INTEGER)')
#reactions = {'wolfie': '<:wolfygun:755447204654874696>', 'wingy': '<:wingyafterashower:771542730916364338>', 'ereg': '<:ninjathonk:827739388058140713>', 'wolfy': '<:wolfyrpg:844992590361526272>', 'wofy': '<:wolfyrpg:844992590361526272>', 'marsh': '<:marshyhappy:826259233309196348>', 'dasani': '<:sunglase:834052568271159297>', 'delta': '<:whot:792770838113026058>', 'jeff': '<:blink:767221910374318150>', 'abuse': '<:catstare:850751387889434624>', 'sensei': '<:thumbsup:851910615168974878>', 'morgy': '<:thumbsup:851910615168974878>', 'bear': '<a:SaucyBear:762798329250709534>', 'demon': '<:YOURFEET:853123667314999317>', 'sparkle': '<:SPARKELS:853036933684658176>', 'mercury': '<:Mercury:881922010123468831>', 'lawliet': '<:lawliet:889270565007921253>', 'melk': '<:melk:889536269074456593>', 'hayley': '<:Kanna_sip:762753253016338512>'}
scores = {'585991293377839114': 4, '509874745567870987': 20, '717869696959119383': 29, '474238346869342220': 3, '635246786243592211': 1}

for r in scores:
    m = scores[r]
    print(f"{r} : {m}")
    cur.execute(f'INSERT INTO sparklesc(userid, serverid, score) VALUES (?, 850110799070363668, ?)', (int(r), int(m)))

con.commit()
for row in cur.execute('SELECT * FROM sparklesc'):
    print(row)
