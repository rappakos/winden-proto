# views.py
import aiohttp_jinja2
from aiohttp import web

from .db import get_report_data



REPORTS = {
    'schlepps_pro_wf': {
        'display_name': 'Schlepps pro Windenfahrer',
        'columns': ['Windenfahrer','Jahr','Gesamt'],
        'sql' : """SELECT s.wf_id, substr(s.[datum],1,4) , count(*) [count]
                FROM schlepps s
                GROUP BY s.wf_id, substr(s.[datum],1,4)
                ORDER BY count(*) desc
              """
    },
    'schlepps_pro_pilot': {
        'display_name': 'Schlepps pro Pilot',
        'columns': ['Pilot','Jahr','Gesamt'],                
        'sql' : """SELECT s.pilot_id, substr(s.[datum],1,4), count(*) [count]
                FROM schlepps s
                GROUP BY s.pilot_id, substr(s.[datum],1,4)
                ORDER BY count(*) desc
              """
    }
}

@aiohttp_jinja2.template('reports.html')
async def reports(request):    
    #print(REPORTS)
    return {
            'reports': {k:v['display_name'] for  k,v in REPORTS.items()},
            'selected_report': None
            }

@aiohttp_jinja2.template('reports.html')
async def report(request):
    report_id = request.match_info['report_id']

    selected_report = REPORTS[report_id] if report_id in REPORTS else None
    if selected_report:
        #print("get data")
        data = await get_report_data(selected_report['columns'],selected_report['sql'])
        selected_report['data'] = data

    return {
            'reports': {k:v['display_name'] for  k,v in REPORTS.items()},
            'selected_report': selected_report
            }
