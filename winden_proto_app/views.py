# views.py
import os
import aiohttp_jinja2
from aiohttp import web
import numpy as np
import pandas as pd
import json

from . import db
from .models import CalPilot, WindeStatus, PILOT_STATUS
from .calendar_loader import GscSuedheideLoader, DummyCalendarLoader

def redirect(router, route_name):
    location = router[route_name].url_for()
    return web.HTTPFound(location)

@aiohttp_jinja2.template('index.html')
async def index(request):
    pr = await db.get_process_status()

    res = pr.to_dict()

    # always?
    res['winden'] = await db.get_winden()

    print(res)

    return res

async def cancel_day(request):
    if request.method == 'POST':
        form = await request.post()
        # 
        await db.close_day()

        raise web.HTTPFound('/')
    else:
        raise NotImplementedError("cancel_day should be POST")

async def activate_winde(request):
    if request.method == 'POST':
        form = await request.post()
        winde_id = form['winde_id']
        # 
        await db.activate_winde(winde_id)

        raise web.HTTPFound('/')
    else:
        raise NotImplementedError("activate_winde should be POST")


@aiohttp_jinja2.template('pilot_list.html')
async def pilot_list(request):
    if request.method=='GET':   
        pr = await db.get_process_status()
        res = pr.to_dict()
        res['pilots'] = await db.get_pilot_list()
        res['not_registered'] = await db.get_not_registered_pilots()
        return res
    elif request.method=='POST':
        form = await request.post()
        pilot_id = form['pilot_id']
        # 
        await db.add_pilot_to_list(pilot_id)

        return web.Response(status=200)
    else:
        raise NotImplementedError("pilot_list should be GET or POST")    

@aiohttp_jinja2.template('calendar_list.html')
async def calendar_list(request):


    skip_pilot_list = request.rel_url.query.get('skip',False)
    if skip_pilot_list:
        await db.add_pilot_list([])
        raise web.HTTPFound('/')

    pr = await db.get_process_status()
    calendar_list = []
    if not pr.pilot_list and not skip_pilot_list:
        calendar_list = DummyCalendarLoader().load_pilots() if os.environ.get("USE_DUMMY_CALENDAR",0)=="1" else GscSuedheideLoader().load_pilots()
        pilots = await db.get_piloten() # all
        pilot_cal_ids = {p.calendar_id:p.id for p in pilots}
        for cp in calendar_list:
            cp.identified = cp.calendar_id in pilot_cal_ids
            db.guess_pilot_id(cp.name)


    #print(calendar_list)
    res = pr.to_dict()
    res['calendar_list'] = [p.to_dict() for p in calendar_list]
    res['calendar_list_json'] = CalPilot.schema().dumps(calendar_list, many=True)
    return res

async def add_calendar_list(request):
    if request.method == 'POST':
        form = await request.post()
        calendar_list = CalPilot.schema().loads(form['pilot_list'], many=True)
        #print(calendar_list)
        pilots = await db.get_piloten() # all 
        pilot_cal_ids = {p.calendar_id:p.id for p in pilots}        
        pilot_list = []
        for cp in calendar_list:
            if cp.calendar_id in pilot_cal_ids:
                pilot_list.append(pilot_cal_ids[cp.calendar_id])
            else:
                #print(cp)
                new_id = await db.add_guest_pilot(cp.name, cp.calendar_id)
                if new_id:
                    pilot_list.append(new_id)

        print(pilot_list)
        await db.add_pilot_list(pilot_list)

        raise web.HTTPFound('/')
    else:
        raise NotImplementedError("start_day should be POST")

@aiohttp_jinja2.template('wf_list.html')
async def select_wf(request):
    pr = await db.get_process_status()
    res = pr.to_dict()
    if request.method == 'POST':
        form = await request.post()
        pilot_id = form['active_wf']
        await db.set_active_wf(pilot_id)

        raise web.HTTPFound('/')
    
    if request.method == 'GET':

        res['wf_list']= await db.get_wf_list()

        # TODO for WIA set EWF

        return res

@aiohttp_jinja2.template('protocol.html')
async def protocol(request):
    winde_id = request.match_info['winde_id']
    type = request.match_info['type']
    print(winde_id, type)
    if request.method == 'POST':
        form = await request.post()
        # ? validate       
        protocol = await db.get_protocol_questions(winde_id=winde_id, type=type)
        #        
        questions = [ [q['question'], (form[q['id']]=='on') if q['id'] in form else False ] for q in protocol ]
        kommentar = form['kommentar']
        pilot_id = form['person']
        # 
        await db.save_protocol(winde_id,pilot_id, type, questions, kommentar )

        if type=='abbau':
            w_status = WindeStatus.ABGEBAUT
        elif type=='aufbau':
            w_status = WindeStatus.AUFGEBAUT
        else:
            w_status = WindeStatus.GARAGE

        await db.set_active_winde_status(w_status) #

        if w_status == WindeStatus.GARAGE:
            await db.close_day()


        raise web.HTTPFound('/')    
    if request.method == 'GET':
        # 
        protocol = await db.get_protocol_questions(winde_id=winde_id, type=type)
        piloten = await db.get_pilot_list() # those who are there
        #print(piloten)

        return {
                'type': type,
                'winde_id': winde_id,
                'piloten': [p for p in piloten if p.status not in [PILOT_STATUS['G'],PILOT_STATUS['NG']] ],
                'protocol': protocol}       


@aiohttp_jinja2.template('gastpiloten.html')
async def gastpiloten(request):

    return {
        'gastpiloten': await db.get_gastpiloten()
    }


@aiohttp_jinja2.template('schleppstart.html')
async def schlepp_start(request):
    pr = await db.get_process_status()
    res = pr.to_dict()
    # those who are there plut WF should be removed
    res['pilots'] = [p.to_dict() for p in await db.get_pilot_list() if p.id != pr.active_wf] # 
    
    return res

async def schlepp(request):
    if request.method == 'POST':
        data = await request.post()
        pr = await db.get_process_status()
        try:
            winde_id = pr.active_winde
            wf_id = pr.active_wf
            ewf_id = None # TODO
            pilot_id = data['pilot_id'] # compare to DB? could be new
            zugkraft = data['zugkraft'] # compare to DB
        except (KeyError, TypeError, ValueError) as e:
            raise web.HTTPBadRequest(
                text=f'Some values are not correct\n {e}') from e
        # save
        await db.add_schlepp(winde_id, wf_id, ewf_id, pilot_id, zugkraft)
        # redirect
        router = request.app.router
        url = router['schlepp_active'].url_for()
        raise web.HTTPFound(location=url)
    
async def set_schlepp_status(request):
    schlepp_id=request.match_info['schlepp_id']
    if request.method == 'POST':
        data = await request.post()
        status = data['status'] # validate

        await db.set_schlepp_status(schlepp_id, status)

        raise web.HTTPFound('/')


@aiohttp_jinja2.template('help.html')
async def help(request):
    pr = await db.get_process_status()

    return pr.to_dict()

@aiohttp_jinja2.template('schlepp_active.html')
async def schlepp_active(request):
    if request.method == 'GET':
        pr = await db.get_process_status()
        res = pr.to_dict()

        res['schlepp'] = await db.get_active_schlepp()
        
        return res


@aiohttp_jinja2.template('schlepps.html')
async def schlepps(request):
    page_index = int(request.rel_url.query.get('p',0))

    return {
        'totals': await db.get_schlepp_totals(),
        'schlepps': await db.get_schlepps(page_index)
        }


#
#  obsolete
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
                ) for p in np.random.choice([p.id for p in piloten],5,replace=False)
            ])
    # 
    pilot_map = {p.id: p.status for p in piloten }
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





