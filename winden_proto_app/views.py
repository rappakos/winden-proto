# views.py
import aiohttp_jinja2
from aiohttp import web
import numpy as np
import pandas as pd
import json

from . import db
from .process_model import Process, WindeStatus

def redirect(router, route_name):
    location = router[route_name].url_for()
    return web.HTTPFound(location)

@aiohttp_jinja2.template('index.html')
async def index(request):
    pr = Process()
    pr.active_day = '2024-02-04' # temp
    pr.pilot_list = True # temp
    pr.active_winde = 'Elowin'
    pr.winde_status = WindeStatus.AUFGEBAUT
    pr.active_wf = 'Akos'

    return pr.to_dict()

@aiohttp_jinja2.template('admin.html')
async def admin(request):

    return {
        'test': 'admin'
    }


#
#  old views below this
#


@aiohttp_jinja2.template('calendar.html')
async def calendar(request):
    from datetime import date, timedelta
    time_now = date.today()
    statuses = ['yes','no','maybe']
    days = [time_now + timedelta(days=i) for i in range(7)]
    dayparts = ["10:00","13:00"] # could be some hours too
    piloten = await db.get_piloten()
    entries = []
    # should come from DB
    for day in days:
        for daypart in dayparts:
            entries.extend([(
                    day,
                    daypart,
                    p,
                    np.random.choice(statuses, p=[0.5,0.3,0.2])
                ) for p in np.random.choice([p['id'] for p in piloten],5,replace=False)
            ])
    # 
    pilot_map = {p['id']: p['status'] for p in piloten }
    df = pd.DataFrame(entries,columns=['day','daypart','pilot_id','status'])    
    df['pilot_type'] = df.apply(lambda p: pilot_map[p['pilot_id']] ,axis=1 )
    #print(df.head())
    f = df['status']=='yes'
    aggr =  df[f][['day','daypart','pilot_type']].pivot_table(index=['day','daypart'],columns=['pilot_type'], aggfunc=len).reset_index()
    #print(aggr.head())
    aggr = json.loads(aggr.to_json(orient='records', date_format='iso'))

    return {
        'days': days,
        'dayparts': dayparts,
        'piloten': piloten,
        'entries': entries,
        'aggr': aggr
        }


@aiohttp_jinja2.template('alle_winden.html')
async def alle_winden(request):
    winden = await db.get_winden()
    return {'winden': winden}

@aiohttp_jinja2.template('winde.html')
async def winde(request):    
    winde_id = request.match_info['winde_id']
    #print('requested',winde_id)
    for w in await db.get_winden():
        if w['winde_id']==winde_id:
            return {'winde': w}
    else:
       raise web.HTTPNotFound(text=f'{winde_id} not found')


@aiohttp_jinja2.template('aufbau.html')
async def aufbau(request):
    winde_id = request.match_info['winde_id']
    # is this a good design? same route, different methods?
    if request.method == 'POST':
        form = await request.post()
        # ? validate       
        protocol = await db.get_aufbau_fragen(winde_id=winde_id)
        #
        type = 'aufbau'
        questions = [ [q['question'], (form[q['id']]=='on') if q['id'] in form else False ] for q in protocol ]
        kommentar = form['kommentar']
        pilot_id = form['aufgebaut-von']
        # 
        await db.save_protocol(winde_id,pilot_id, type, questions, kommentar )

        raise redirect(request.app.router, 'winden')
        
    if request.method == 'GET':
        # 
        protocol = await db.get_aufbau_fragen(winde_id=winde_id)
        piloten = await db.get_piloten()

        return {
                'winde_id': winde_id,
                'piloten': [p for p in piloten if p['status'] in ['W','EWF','WIA','M'] ],
                'protocol': protocol}


@aiohttp_jinja2.template('piloten.html')
async def piloten(request):
    return {'piloten': await db.get_piloten()}

@aiohttp_jinja2.template('schlepps.html')
async def schlepps(request):
    winde_id, wf_id = await db.get_last_schlepp_data()
    return {
        'winde_id': winde_id ,
        'wf_id': wf_id,
        'schlepps': await db.get_schlepps()
        }

async def schlepp(request):
    data = await request.post()
    #print(data)
    # validate
    try:
        winde_id = data['winde_id'] # compare to DB
        if not winde_id or winde_id=="None":
            raise ValueError("Invalid winde_id: must not be empty")
        #print(winde_id)
        wf_id = data['windenfahrer'] # compare to DB
        ewf_id = data['ewf'] # compare to DB
        pilot_id = data['pilot'] # compare to DB? could be new
        zugkraft = data['zugkraft'] # compare to DB
    except (KeyError, TypeError, ValueError) as e:
        raise web.HTTPBadRequest(
               text=f'Some values are not correct\n {e}') from e
    # save
    await db.add_schlepp(winde_id, wf_id, ewf_id, pilot_id, zugkraft)
    # redirect
    router = request.app.router
    url = router['schlepps'].url_for()
    raise web.HTTPFound(location=url)

@aiohttp_jinja2.template('schleppstart.html')
async def schlepp_start(request):
    piloten = await db.get_piloten()
    windenfahrer = [p for p in piloten if p['status'] in ['W','EWF','WIA'] ]
    winde_id, wf_id = await db.get_last_schlepp_data()
    winden = await db.get_winden()
    data = {
        'winde_id': winde_id ,
        'wf_id': wf_id,
        'aktive_winden': [w for w in winden if w['active']],
        'windenfahrer': windenfahrer,
        'piloten': piloten
    }

    return {'data': data}