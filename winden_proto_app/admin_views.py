# admin_views.py
import aiohttp_jinja2
from aiohttp import web

from os import listdir, remove
from os.path import isfile, join,getsize,getctime,dirname
from datetime import datetime
from shutil import copy

from .views import redirect
from . import db
from .models import Pilot,PILOT_STATUS

BACKUP_FOLDER = 'backups'

@aiohttp_jinja2.template('admin.html')
async def admin(request):

    return {
        'test': 'admin'
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
        if w.winde_id==winde_id:
            return {'winde': w.to_dict()}
    else:
       raise web.HTTPNotFound(text=f'{winde_id} not found')

@aiohttp_jinja2.template('piloten.html')
async def piloten(request):
    if request.method == 'GET':
        return {'piloten': await db.get_piloten()}
    else:
        raise NotImplementedError("POST (add pilot) is not implemented yet") 


@aiohttp_jinja2.template('pilot.html')
async def pilot(request):    
    pilot_id =  request.match_info['pilot_id']
    if request.method == 'GET':
        pilot = await db.get_pilot(pilot_id)
        #print(pilot)
        return {'pilot': pilot }
    if request.method == 'POST':
        form = await request.post()
        # validate ...
        if 'name' not in form or not form['name'] or form['name']=='':
            raise ValueError("Pilot name must not be empty")

        p = Pilot()
        p.id=pilot_id
        p.name=form['name']
        p.status = [k for k,v in PILOT_STATUS.items() if v==form['status']][0]
        p.zugkraft = form['zugkraft'] if int(form['zugkraft']) > 0 else None
        p.calendar_id = form['calendar_id']
        p.verein = form['verein']

        # save
        await db.save_pilot(p)

    raise web.HTTPFound(f'/piloten/{pilot_id}')
    
async def delete_pilot(request):
    pilot_id =  request.match_info['pilot_id']
    if request.method == 'POST':
        # only if they have no starts!
        await db.delete_guest_pilot(pilot_id)

    raise web.HTTPFound('/piloten')

@aiohttp_jinja2.template('backups.html')
async def backups(request):    
    backup_folder = join(request.app['PROJECT_ROOT'], BACKUP_FOLDER)
    #print(backup_folder)
    files = [{
                'name':f, 
                'size': getsize(join(backup_folder, f)),
                'created':datetime.fromtimestamp(getctime(join(backup_folder, f))).strftime('%Y-%m-%d %H:%M:%S') 
            } for f in listdir(backup_folder) if isfile(join(backup_folder, f))]

    return {'files': files}

async def create_backup(request):
    db_name = request.app['DB_NAME']
    source = join(dirname(request.app['PROJECT_ROOT']),db_name)
    target = join(request.app['PROJECT_ROOT'], BACKUP_FOLDER, f'{db_name}.{datetime.now().strftime("%Y%d%m.%H%M%S")}.bak' )

    print(source,target)
    copy(source,target)
    
    # done
    raise redirect(request.app.router, 'backups')

async def remove_backup(request):
    filename = request.rel_url.query.get('name', '')
    backup_folder = join(request.app['PROJECT_ROOT'], BACKUP_FOLDER)
    if filename:
        target=join(backup_folder, filename)
        if isfile(target):
            print(f'removing {target}')
            remove(target)

    # done
    raise redirect(request.app.router, 'backups')