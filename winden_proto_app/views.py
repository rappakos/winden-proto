# views.py
import aiohttp_jinja2
from aiohttp import web

#from . import db

mock_menu =  [
            'Winden',
            'Piloten',
            'Schlepps'
            ]

mock_winden =  [
        {   
            'winde_id': 'Kella',
            'name': 'Kella',
            'baujahr': '1975',
            'active': False
        },
        {   
            'winde_id': 'Elowin',
            'name': 'Elowin',
            'baujahr': '2022',
            'active': True
        },
    ]

mock_piloten = [
        {
            'id': 'Akos',
            'name': 'Akos',
            'status': 'W'
        },
        {
            'id': 'Orsi',
            'name': 'Orsi',
            'status': 'W'
        },        
        {
            'id': 'Helmut',
            'name': 'Helmut',
            'status': 'EWF'
        }
    ]

mock_schlepps = [
        {
            'winden_id': 'Elowin',
            'wf_id': 'Orsi',
            'ewf_id': None,
            'pilot_id': 'Akos',
            'datum': '2023-08-05',
            'status': 'finished',
            'schlepp_start': '2023-08-05T12:34:56.789Z',
            'status_date': '2023-08-05T12:36:56.789Z',
        },
        {
            'winden_id': 'Elowin',
            'wf_id': 'Orsi',
            'ewf_id': None,
            'pilot_id': 'Helmut',
            'datum': '2023-08-05',
            'status': 'finished',
            'schlepp_start': '2023-08-05T12:45:56.789Z',
            'status_date': '2023-08-05T12:47:56.789Z',
        }
    ]


@aiohttp_jinja2.template('index.html')
async def index(request):
    menu = mock_menu
    return {'menu': menu}


@aiohttp_jinja2.template('alle_winden.html')
async def alle_winden(request):
    # mock
    winden = mock_winden
    return {'winden': winden}

@aiohttp_jinja2.template('piloten.html')
async def piloten(request):
    piloten = mock_piloten
    return {'piloten': piloten}

@aiohttp_jinja2.template('schlepps.html')
async def schlepps(request):
    # mock
    schlepps = mock_schlepps
    return {'schlepps': schlepps}