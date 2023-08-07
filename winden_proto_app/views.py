# views.py
import aiohttp_jinja2
from aiohttp import web

from . import db

mock_menu =  [
            'Winden',
            'Piloten',
            'Schlepps'
            ]

def redirect(router, route_name):
    location = router[route_name].url_for()
    return web.HTTPFound(location)


@aiohttp_jinja2.template('index.html')
async def index(request):
    menu = mock_menu
    return {'menu': menu}


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
    if request.method == 'POST':
        form = await request.post()
        # TODO save
        for key in form.keys():
            print(key, form[key])

        raise redirect(request.app.router, 'winden')
        
    if request.method == 'GET':
        winde_id = request.match_info['winde_id']
        # 
        protocol = [{'id': f'q-{j}', 'label': f'frage {j}'} for j in range(10)]

        return {
                'winde_id': winde_id,
                'protocol': protocol}


@aiohttp_jinja2.template('piloten.html')
async def piloten(request):
    return {'piloten': await db.get_piloten()}

@aiohttp_jinja2.template('schlepps.html')
async def schlepps(request):
    return {'schlepps': await db.get_schlepps()}

async def schlepp(request):
    data = await request.post()
    print(data)
    # validate
    try:
        winden_id = data['winden_id'] # compare to DB
        #print(winden_id)
        wf_id = data['windenfahrer'] # compare to DB
        ewf_id = data['ewf'] # compare to DB
        pilot_id = data['pilot'] # compare to DB
        gewicht = data['gewicht'] # compare to DB
    except (KeyError, TypeError, ValueError) as e:
        raise web.HTTPBadRequest(
               text='Some values are not correct') from e
    # save
    await db.add_schlepp(winden_id, wf_id, ewf_id, pilot_id, gewicht)
    # redirect
    router = request.app.router
    url = router['schlepps'].url_for()
    raise web.HTTPFound(location=url)

@aiohttp_jinja2.template('schleppstart.html')
async def schlepp_start(request):
    piloten = await db.get_piloten()
    windenfahrer = [p for p in piloten if p['status'] in ['W','EWF','WIA'] ]
    #
    data = {
        'winde_id': 'ELOWIN',
        'windenfahrer': windenfahrer,
        'piloten': piloten
    }

    return {'data': data}