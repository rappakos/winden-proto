import aiosqlite

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