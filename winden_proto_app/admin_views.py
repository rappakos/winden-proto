# admin_views.py
import aiohttp_jinja2
from aiohttp import web

from os import listdir, remove
from os.path import isfile, join,getsize,getctime,dirname
from datetime import datetime
from shutil import copy

from .views import redirect


BACKUP_FOLDER = 'backups'


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