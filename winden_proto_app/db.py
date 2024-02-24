# db.py
import os
import aiosqlite
from datetime import datetime
from typing import List

from .models import Process, WindeStatus, PILOT_STATUS,Winde, Pilot

DB_NAME = './winde-demo.db'
INIT_SCRIPT = './winden_proto_app/init_db.sql'

PAGE_SIZE = 20

async def setup_db(app) -> None:
    app['DB_NAME'] = DB_NAME
    async with aiosqlite.connect(DB_NAME) as db:
        # only test
        async with db.execute("SELECT 'check OK'") as cursor:
            async for row in cursor:
                print(row[0])

        # 
        if os.environ.get("RESET_DB", 0)=='1':
            print("resetting db")
            for stmt in [   "DROP TABLE IF EXISTS flying_days;",
                            "DROP TABLE IF EXISTS pilot_list;",
                            "DROP TABLE IF EXISTS schlepps;",
                            "DROP TABLE IF EXISTS protocolanswers;",
                            "DROP TABLE IF EXISTS protocol;",
                            "DROP TABLE IF EXISTS piloten;"]:
                await db.execute(stmt)
                await db.commit()            
        #
        with open(INIT_SCRIPT, 'r') as sql_file:
            sql_script = sql_file.read()
            await db.executescript(sql_script)
            await db.commit()

        if os.environ.get("PRINT_PILOTS", 0)=='1':
            async with db.execute("SELECT * FROM piloten") as cursor:
                async for row in cursor:
                    print(row)
        if os.environ.get("PRINT_DAYS", 0)=='1':
            async with db.execute("SELECT * FROM [flying_days] ORDER BY [create_timestamp] DESC LIMIT 10 ") as cursor:
                async for row in cursor:
                    print(row)                    


async def get_process_status() -> Process:
    pr = Process()

    async with aiosqlite.connect(DB_NAME) as db:
        params  = {'datum': datetime.now().strftime("%Y-%m-%d")}
        async with db.execute("""SELECT
                                d.[datum],
                                d.[pilot_list],
                                d.[active_winde_id],
                                d.[winde_aufgebaut],
                                d.[winde_abgebaut],
                                d.[active_wf],
                                d.[active_ewf]
                            FROM [flying_days] d
                            WHERE d.[datum]=:datum and d.[closed] is null
                              """,params ) as cursor:
            async for row in cursor:
                pr.active_day = params['datum']
                pr.pilot_list = row[1]
                pr.active_winde = row[2]
                if row[4]:
                    pr.winde_status = WindeStatus.ABGEBAUT
                elif row[3]:
                    pr.winde_status = WindeStatus.AUFGEBAUT
                else:
                    pr.winde_status = WindeStatus.GARAGE
                pr.active_wf = row[5]
                pr.active_ewf = row[6]

    return pr


async def close_day() -> None:
    async with aiosqlite.connect(DB_NAME) as db:
        params  = {'datum': datetime.now().strftime("%Y-%m-%d")}
        await db.execute("""
                        UPDATE [flying_days] SET closed=current_timestamp WHERE [datum] = :datum -- all !
                    """, params)
        await db.commit() #

async def activate_winde(winde_id:str) -> None:
    async with aiosqlite.connect(DB_NAME) as db:
        params  = {'datum': datetime.now().strftime("%Y-%m-%d"), 'winde_id':winde_id}
        await db.execute("""
                            UPDATE [flying_days] SET active_winde_id=:winde_id 
                            WHERE [datum] = :datum and [closed] is null
                        """, params)
        await db.commit() #

async def set_active_winde_status(status:WindeStatus) -> None:
    async with aiosqlite.connect(DB_NAME) as db:
        params  = {'datum': datetime.now().strftime("%Y-%m-%d"), 
                    'winde_aufgebaut': status==WindeStatus.AUFGEBAUT or status==WindeStatus.ABGEBAUT,
                    'winde_abgebaut': status==WindeStatus.ABGEBAUT }
        await db.execute("""
                            UPDATE [flying_days] SET winde_aufgebaut=current_timestamp
                            WHERE [datum] = :datum and [closed] is null and :winde_aufgebaut=1;
                         """, params)
        await db.execute("""        
                            UPDATE [flying_days] SET winde_abgebaut=current_timestamp
                            WHERE [datum] = :datum and [closed] is null and :winde_abgebaut=1;
                        """, params)
        await db.commit() #    
    
async def set_active_wf(pilot_id:str) -> None:
    async with aiosqlite.connect(DB_NAME) as db:
        params  = {'datum': datetime.now().strftime("%Y-%m-%d"), 'pilot_id':pilot_id}
        await db.execute("""
                            UPDATE [flying_days] SET active_wf=:pilot_id 
                            WHERE [datum] = :datum and [closed] is null
                        """, params)
        await db.commit() # 

async def set_active_ewf(pilot_id:str) -> None:
    async with aiosqlite.connect(DB_NAME) as db:
        params  = {'datum': datetime.now().strftime("%Y-%m-%d"), 'pilot_id':pilot_id}
        await db.execute("""
                            UPDATE [flying_days] SET active_ewf=:pilot_id 
                            WHERE [datum] = :datum and [closed] is null
                        """, params)
        await db.commit() #    


# useful?
def guess_pilot_id(display_name:str):
    res = None
    parts = display_name.split(' ')
    if len(parts) > 1:
        res = parts[0][0].upper() + parts[0][1:].lower() + parts[1][0].upper()
    if len(parts)==1:
        res = parts[0][0].upper() + parts[0][1:].lower()

    #print(display_name, res)
    return res

async def add_guest_pilot(name:str, calendar_id:str=None) -> str:
    res = None
    if not name or name=='':
        raise ValueError("Pilot name must not be empty!")
    
    new_id = guess_pilot_id(name)
    async with aiosqlite.connect(DB_NAME) as db:
        params  = {
            'pilot_id': new_id,
            'name': name,
            'status_txt': 'G',
            'calendar_id': calendar_id
        }
        async with db.execute("""SELECT count(*) FROM piloten WHERE pilot_id= :pilot_id""", params) as cursor:
            row = await cursor.fetchone()
            if row[0]==0:
                # all cool, add
                rowid = await db.execute_insert(""" 
                            INSERT INTO [piloten](pilot_id,name,status_txt,calendar_id)
                            SELECT :pilot_id,:name,:status_txt,:calendar_id
                        """, params )
                if rowid[0] > 0:
                    res=new_id

                await db.commit()
            else:
                raise ValueError("We cannot use this user id")

    return res



async def add_pilot_list(pilot_list:List[str]):
    async with aiosqlite.connect(DB_NAME) as db:
        params  = {
                    'datum': datetime.now().strftime("%Y-%m-%d"),
                    'pilot_list': len(pilot_list) > 0
                }
        #print('add_pilot_list', params)
        await db.execute_insert("""
                            INSERT INTO [flying_days] ([datum],[pilot_list])
                            SELECT :datum, :pilot_list 
                        """, params)
        
        for pilot_id in pilot_list:
            params['pilot_id'] = pilot_id
            await db.execute_insert("""
                            INSERT OR IGNORE INTO [pilot_list] ([datum],[pilot_id])
                            SELECT :datum, :pilot_id 
                        """, params)

        await db.commit() #    

async def get_winden() -> List[Winde] :
    res = []
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM winden") as cursor:
            async for row in cursor:
                w  = Winde()
                w.winde_id = row[0]
                w.name = row[1]
                w.active = row[2]
                w.baujahr = row[3]
                
                res.append(w)
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
                              WHERE p.[status_txt] in ('W','WF','EWF','WIA') 
                              
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

async def set_schlepp_status(schlepp_id, status) -> None:
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
                               , p.name
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
                        'pilot_status': PILOT_STATUS[row[10]],
                        'pilot_name': row[11]
                    })
    return res


async def get_gastpiloten():
    res = []
    async with aiosqlite.connect(DB_NAME) as db:
        params  = {'datum': datetime.now().strftime("%Y-%m-%d")}
        async with db.execute("""SELECT
                                    p.[pilot_id]
                                    ,p.[name]
                                    , count(s.schlepp_id) [schlepp_count]
                              FROM piloten p 
                              LEFT JOIN schlepps s ON  s.[pilot_id]=p.[pilot_id]
                              WHERE p.[status_txt] in ('G') AND s.[datum]= :datum
                              GROUP BY p.[pilot_id],p.[name],p.[status_txt], p.[zugkraft]
                              """,params) as cursor:
            async for row in cursor:
                #print(row)
                res.append({
                        'id':row[0],
                        'name':row[1],
                        'schlepp_count': row[2]
                        })
    return res

#
# OLD PROCESS / DB SCHEMA
#

async def get_piloten() -> List[Pilot]:
    res = []
    async with aiosqlite.connect(DB_NAME) as db:
        params  = {'datum': datetime.now().strftime("%Y-%m-%d")}
        async with db.execute("""SELECT
                               p.[pilot_id],p.[name],p.[status_txt]
                                , IFNULL(p.[zugkraft] ,0) [zugkraft] 
                                , p.[calendar_id]
                                , p.[verein]
                               , count(s.schlepp_id) [schlepp_count]
                              FROM piloten p 
                              LEFT JOIN schlepps s ON s.[datum]= :datum and s.[pilot_id]=p.[pilot_id]
                              GROUP BY p.[pilot_id],p.[name],p.[status_txt], p.[zugkraft] , p.[calendar_id], p.[verein]
                              """,params) as cursor:
            async for row in cursor:
                p = Pilot()
                p.id = row[0]
                p.name = row[1]
                p.status = PILOT_STATUS[row[2]]
                p.zugkraft = row[3]
                p.calendar_id = row[4]
                p.verein = row[5]
                p.schlepp_count = row[6]
                
                res.append(p)
    return res

async def get_pilot(pilot_id:str) -> Pilot:
    res = Pilot()
    async with aiosqlite.connect(DB_NAME) as db:
        params  = {'datum': datetime.now().strftime("%Y-%m-%d"),'pilot_id': pilot_id}
        async with db.execute("""SELECT
                               p.[pilot_id],p.[name],p.[status_txt]
                                , IFNULL(p.[zugkraft] ,0) [zugkraft] 
                                , p.[calendar_id]
                                , p.[verein]
                               , count(s.schlepp_id) [schlepp_count]
                              FROM piloten p 
                              LEFT JOIN schlepps s ON s.[datum]= :datum and s.[pilot_id]=p.[pilot_id]
                              WHERE p.pilot_id = :pilot_id
                              GROUP BY p.[pilot_id],p.[name],p.[status_txt], p.[zugkraft] , p.[calendar_id], p.[verein]
                              """,params) as cursor:
            row = await cursor.fetchone()
            res.id = row[0]
            res.name = row[1]
            res.status = PILOT_STATUS[row[2]]
            res.zugkraft = row[3]
            res.calendar_id = row[4]
            res.verein = row[5]
            res.schlepp_count = row[6]
                
                
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


async def get_schlepp_totals():
    totals = 0
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("""SELECT count(*) FROM schlepps """) as cursor:
            row = await cursor.fetchone()
            totals = row[0]

    return {
        'totals': totals,
        'page_size': PAGE_SIZE
    }

async def get_schlepps(page_index: int):
    res = []
    async with aiosqlite.connect(DB_NAME) as db:
        params = {'limit': PAGE_SIZE, 'offset': page_index*PAGE_SIZE}
        async with db.execute("""
                            SELECT 
                                s.schlepp_id
                                ,s.winde_id
                                ,s.wf_id
                                ,s.ewf_id
                                ,s.pilot_id
                                ,s.datum
                                , dense_rank() over(partition by s.datum order by s.schlepp_id ) [schlepp_no_daily]
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
                            LIMIT :limit OFFSET :offset
                            """, params) as cursor:
            async for row in cursor:
                #print(row)
                res.append({
                        'schlepp_id':row[0],
                        'winde_id':row[1],
                        'wf_id':row[2],
                        'ewf_id':row[3],
                        'pilot_id': row[4],
                        'datum': row[5],
                        'schlepp_no_daily': row[6],
                        'status': row[7],
                        'schlepps_heute': row[8],
                        'schlepp_no':  row[9]
                    })
    return res

# UNUSED?
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
