import aiosqlite
from datetime import datetime

DB_NAME = './winde-demo.db'
INIT_SCRIPT = './winden_proto_app/init_db.sql'

async def setup_db(app):
    async with aiosqlite.connect(DB_NAME) as db:
        # only test
        async with db.execute("SELECT 'check'") as cursor:
            async for row in cursor:
                print(row[0])

        #
        with open(INIT_SCRIPT, 'r') as sql_file:
            sql_script = sql_file.read()
            await db.executescript(sql_script)
            await db.commit()

        #async with db.execute("SELECT * FROM piloten") as cursor:
        #    async for row in cursor:
        #        print(row)


async def get_piloten():
    res = []
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM piloten") as cursor:
            async for row in cursor:
                #print(row)
                res.append({
                        'id':row[0],
                        'name':row[1],
                        'status':row[2]
                        })
    return res

async def get_winden():
    res = []
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM winden") as cursor:
            async for row in cursor:
                #print(row)
                res.append({
                        'winde_id':row[0],
                        'name':row[1],
                        'active':row[2],
                        'baujahr':row[3]
                        })
    return res

async def get_aufbau_fragen(winde_id:str):
    res = []
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("""SELECT question_id, question 
                                 FROM protocolquestions 
                                 WHERE [type]='aufbau' 
                                 ORDER BY question_id """) as cursor:
            async for row in cursor:
                res.append({
                        'id':f'q-{row[0]}',
                        'question':row[1]
                        })
    return res

async def save_protocol(winde_id:str,pilot_id:str, type:str, questions, kommentar:str ):
    async with aiosqlite.connect(DB_NAME) as db:
        protocol_id = await db.execute_insert("""
                INSERT INTO protocol (winden_id, pilot_id, type, kommentar)
                VALUES (?,?,?,?)
            """, (winde_id, pilot_id, type, kommentar))
        print(protocol_id)
        for q in questions:
            await db.execute_insert("""
                INSERT INTO protocolanswers (protocol_id, question, answer)
                VALUES (?,?,?)
            """, (protocol_id, q[0], q[1]))


async def get_schlepps():
    res = []
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("""
                            SELECT * 
                            FROM schlepps s
                            ORDER BY schlepp_id DESC
                            LIMIT 20
                            """) as cursor:
            async for row in cursor:
                #print(row)
                res.append({
                        'schlepp_id':row[0],
                        'winden_id':row[1],
                        'wf_id':row[2],
                        'ewf_id':row[3],
                        'pilot_id': row[4],
                        'datum': row[5],
                        'status': row[6]
                    })
    return res

async def add_schlepp(winden_id:str, wf_id:str, ewf_id:str, pilot_id:str, gewicht:int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO schlepps ([winden_id],[wf_id],[ewf_id],[pilot_id],[datum])
            VALUES (?,?,?,?,?)
            """, (winden_id,wf_id,ewf_id,pilot_id,datetime.today().strftime('%Y-%m-%d')))
        
        await db.commit()