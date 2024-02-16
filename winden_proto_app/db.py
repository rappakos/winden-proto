import aiosqlite
from datetime import datetime

from .process_model import Process, WindeStatus

DB_NAME = './winde-demo.db'
INIT_SCRIPT = './winden_proto_app/init_db.sql'

PILOT_STATUS = {
    'G': 'Gast',
    'NG': 'Nord-Gast',
    'M': 'Mitglied',
    'WIA': 'WindenFiA',
    'W': 'Windenfahrer',
    'WF': 'Windenfahrer',
    'EWF': 'EWF',
}


async def setup_db(app):
    app['DB_NAME'] = DB_NAME
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


async def get_process_status() -> Process:
    pr = Process()
    #pr.active_winde = 'Elowin'
    #pr.winde_status = WindeStatus.AUFGEBAUT
    #pr.active_wf = 'Akos'
    async with aiosqlite.connect(DB_NAME) as db:
        params  = {'flying_day': datetime.now().strftime("%Y-%m-%d")}
        async with db.execute("""SELECT
                                [flying_day],
                                [pilot_list],
                                w.winde_id [active_winde_id],
                                [winde_aufgebaut],
                                [winde_abgebaut],
                                [active_wf]
                            FROM [flying_days] d
                            LEFT JOIN winden w ON w.winde_id=d.active_winde_id --could be removed if FK is there
                            WHERE d.[flying_day]=:flying_day and d.[canceled]=0
                              """,params ) as cursor:
            async for row in cursor:
                pr.active_day = params['flying_day']
                pr.pilot_list = row[1]
                pr.active_winde = row[2]
                pr.winde_status = WindeStatus.AUFGEBAUT if row[3] and not row[4] else WindeStatus.GARAGE
                pr.active_wf = row[5]

    return pr


async def cancel_day():
    async with aiosqlite.connect(DB_NAME) as db:
        params  = {'flying_day': datetime.now().strftime("%Y-%m-%d")}
        await db.execute("""
                            UPDATE [flying_days] SET canceled=1 WHERE [flying_day] = :flying_day
                        """, params)
        await db.commit() #

# TODO this is temp solution 
async def close_day():
    async with aiosqlite.connect(DB_NAME) as db:
        params  = {'flying_day': datetime.now().strftime("%Y-%m-%d")}
        await db.execute("""
                        UPDATE [flying_days] SET canceled=1  WHERE [flying_day] = :flying_day
                    """, params)
        await db.commit() #

async def activate_winde(winde_id):
    async with aiosqlite.connect(DB_NAME) as db:
        params  = {'flying_day': datetime.now().strftime("%Y-%m-%d"), 'winde_id':winde_id}
        await db.execute("""
                            UPDATE [flying_days] SET active_winde_id=:winde_id 
                            WHERE [flying_day] = :flying_day and [canceled]=0
                        """, params)
        await db.commit() #

async def set_active_winde_status(status):
    async with aiosqlite.connect(DB_NAME) as db:
        params  = {'flying_day': datetime.now().strftime("%Y-%m-%d"), 
                    'winde_aufgebaut': status==WindeStatus.AUFGEBAUT,
                    'winde_abgebaut': status==WindeStatus.GARAGE }
        await db.execute("""
                            UPDATE [flying_days] SET winde_aufgebaut=:winde_aufgebaut, winde_abgebaut=:winde_abgebaut 
                            WHERE [flying_day] = :flying_day and [canceled]=0
                        """, params)
        await db.commit() #    
    
async def set_active_wf(pilot_id):
    async with aiosqlite.connect(DB_NAME) as db:
        params  = {'flying_day': datetime.now().strftime("%Y-%m-%d"), 'pilot_id':pilot_id}
        await db.execute("""
                            UPDATE [flying_days] SET active_wf=:pilot_id 
                            WHERE [flying_day] = :flying_day and [canceled]=0
                        """, params)
        await db.commit() #    

async def add_pilot_list(pilot_list):
    async with aiosqlite.connect(DB_NAME) as db:
        params  = {
                    'flying_day': datetime.now().strftime("%Y-%m-%d"),
                    'pilot_list': len(pilot_list) > 0
                }
        await db.execute("""
                            INSERT INTO [flying_days] ([flying_day],[pilot_list])
                            SELECT :flying_day, :pilot_list 
                        """, params)
        
        # TODO save also pilot_list for the day ?

        await db.commit() #    

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

async def get_protocol_questions(winde_id:str, type:str):
    res = []
    async with aiosqlite.connect(DB_NAME) as db:
        params = {'winde_id':winde_id, 'type':type}
        async with db.execute("""SELECT question_id, question 
                                 FROM protocolquestions 
                                 WHERE [type]=:type 
                                 ORDER BY question_id """, params) as cursor:
            async for row in cursor:
                res.append({
                        'id':f'q-{row[0]}',
                        'question':row[1]
                        })
    return res

async def get_wf_list():
    res = []
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("""SELECT p.[pilot_id],p.[name],p.[status_txt]
                              FROM piloten p
                              WHERE p.[status_txt] in ('W','EWF','WIA') 
                              
                        """) as cursor:
            async for row in cursor:
                #print(row)
                res.append({
                        'id':row[0],
                        'name':row[1],
                        'status':row[2],
                        'ewf': [] # should get filled
                        })
    return res

async def set_schlepp_status(schlepp_id, status):
    async with aiosqlite.connect(DB_NAME) as db:
        params  = {'schlepp_id': schlepp_id, 'status':status}
        await db.execute("""
                            UPDATE [schlepps] SET status=:status
                            WHERE [schlepp_id] = :schlepp_id and [status]='started'
                        """, params)
        await db.commit() #    


async def get_active_schlepp():
    async with aiosqlite.connect(DB_NAME) as db:
        params  = {'datum': datetime.now().strftime("%Y-%m-%d"), 'status':'started'}
        res = []
        async with db.execute("""
                            SELECT  
                                s.schlepp_id
                                ,s.winde_id
                                ,s.wf_id
                                ,s.ewf_id
                                ,s.pilot_id
                                ,s.datum
                                ,s.status
                                , count(s2.schlepp_id) [schlepps_heute]
                                , dense_rank() over(partition by s.pilot_id, s.datum order by s.schlepp_id ) [schlepp_no]
                                , p.zugkraft
                                ,  p.status_txt
                            FROM schlepps s
                            INNER JOIN piloten p ON s.pilot_id=p.pilot_id
                            LEFT JOIN schlepps s2 ON s2.pilot_id=s.pilot_id and s.datum=s2.datum
                            WHERE s.[datum] = :datum and s.[status]=:status
                            GROUP BY s.schlepp_id
                                ,s.winde_id
                                ,s.wf_id
                                ,s.ewf_id
                                ,s.pilot_id
                                ,s.datum
                                ,s.status                              
                                , p.zugkraft
                                ,  p.status_txt
                            ORDER BY s.schlepp_id DESC
                            LIMIT 1
                            """, params) as cursor:
            async for row in cursor:
                res.append({
                        'schlepp_id':row[0],
                        'winde_id':row[1],
                        'wf_id':row[2],
                        'ewf_id':row[3],
                        'pilot_id': row[4],
                        'datum': row[5],
                        'status': row[6],
                        'schlepps_heute': row[7],
                        'schlepp_no':  row[8],
                        'zugkraft': row[9],
                        'pilot_status': PILOT_STATUS[row[10]]
                    })
    return res

#
# OLD PROCESS / DB SCHEMA
#

async def get_piloten():
    res = []
    async with aiosqlite.connect(DB_NAME) as db:
        params  = {'datum': datetime.now().strftime("%Y-%m-%d")}
        async with db.execute("""SELECT
                               p.[pilot_id],p.[name],p.[status_txt]
                                , IFNULL(p.[zugkraft] ,0) [zugkraft] 
                               , count(s.schlepp_id) [schlepp_count]
                              FROM piloten p 
                              LEFT JOIN schlepps s ON s.[datum]= :datum and s.[pilot_id]=p.[pilot_id]
                              GROUP BY p.[pilot_id],p.[name],p.[status_txt], p.[zugkraft]
                              """,params) as cursor:
            async for row in cursor:
                #print(row)
                res.append({
                        'id':row[0],
                        'name':row[1],
                        'status':row[2],
                        'zugkraft':row[3],
                        'schlepp_count': row[4]
                        })
    return res


async def save_protocol(winde_id:str,pilot_id:str, type:str, questions, kommentar:str ):
    #print(winde_id, pilot_id, type, kommentar)
    async with aiosqlite.connect(DB_NAME) as db:
        protocol_id = await db.execute_insert("""
                INSERT INTO protocol (winde_id, pilot_id, type, kommentar)
                VALUES (?,?,?,?)
            """, (winde_id, pilot_id, type, kommentar))
        #print(protocol_id)
        for q in questions:
            await db.execute_insert("""
                INSERT INTO protocolanswers (protocol_id, question, answer)
                VALUES (?,?,?)
            """, (protocol_id[0], q[0], q[1]))


async def get_schlepps():
    res = []
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("""
                            SELECT 
                                s.schlepp_id
                                ,s.winde_id
                                ,s.wf_id
                                ,s.ewf_id
                                ,s.pilot_id
                                ,s.datum
                                ,s.status
                                , count(s2.schlepp_id) [schlepps_heute]
                                , dense_rank() over(partition by s.pilot_id, s.datum order by s.schlepp_id ) [schlepp_no]
                            FROM schlepps s
                            LEFT JOIN schlepps s2 ON s2.pilot_id=s.pilot_id and s.datum=s2.datum
                            GROUP BY s.schlepp_id
                                ,s.winde_id
                                ,s.wf_id
                                ,s.ewf_id
                                ,s.pilot_id
                                ,s.datum
                                ,s.status
                            ORDER BY s.schlepp_id DESC
                            LIMIT 20
                            """) as cursor:
            async for row in cursor:
                #print(row)
                res.append({
                        'schlepp_id':row[0],
                        'winde_id':row[1],
                        'wf_id':row[2],
                        'ewf_id':row[3],
                        'pilot_id': row[4],
                        'datum': row[5],
                        'status': row[6],
                        'schlepps_heute': row[7],
                        'schlepp_no':  row[8]
                    })
    return res


async def get_last_schlepp_data():
    async with aiosqlite.connect(DB_NAME) as db:
        winde_id, wf_id=None, None
        async with db.execute("""
                            SELECT s.winde_id,s.wf_id
                            FROM schlepps s
                            WHERE s.[datum] = ?
                            ORDER BY schlepp_id DESC
                            LIMIT 1
                            """, (str(datetime.today().strftime('%Y-%m-%d')),)) as cursor:
            async for row in cursor:
                winde_id, wf_id = row[0], row[1]
        if not winde_id:
            print("no schlepps today")
            # todo load from protocol?!
    return winde_id, wf_id
        

async def add_schlepp(winde_id:str, wf_id:str, ewf_id:str, pilot_id:str, zugkraft:int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO schlepps ([winde_id],[wf_id],[ewf_id],[pilot_id],[datum])
            VALUES (?,?,?,?,?)
            """, (winde_id,wf_id,ewf_id,pilot_id,datetime.today().strftime('%Y-%m-%d')))
        await db.execute("""
            UPDATE piloten SET zugkraft = :zugkraft
            WHERE pilot_id=:pilot_id and (zugkraft is null or zugkraft <> :zugkraft)
            """, (zugkraft,pilot_id))
        
        await db.commit()


async def get_report_data(columns, sql:str):
    res = []
    async with aiosqlite.connect(DB_NAME) as db:
         async with db.execute(sql) as cursor:
             async for row in cursor:
                datarow = [row[j] for j,_ in enumerate(columns) ]
                res.append(datarow)

    return res
