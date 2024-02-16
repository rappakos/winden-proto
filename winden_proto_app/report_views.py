# views.py
import aiohttp_jinja2
from aiohttp import web,streamer
from datetime import datetime
import pandas as pd
import io

from .db import get_report_data
from .views import redirect


REPORTS = {
    'schlepps_pro_wf': {
        'display_name': 'Schlepps pro Windenfahrer',
        'columns': ['Windenfahrer','Jahr','Gesamt'],
        'sql' : """SELECT s.wf_id, substr(s.[datum],1,4) , count(*) [count]
                FROM schlepps s
                GROUP BY s.wf_id, substr(s.[datum],1,4)
                ORDER BY substr(s.[datum],1,4) desc, count(*) desc
              """
    },
    'schlepps_pro_pilot': {
        'display_name': 'Schlepps pro Pilot',
        'columns': ['Pilot','Jahr','Gesamt'],                
        'sql' : """SELECT s.pilot_id, substr(s.[datum],1,4), count(*) [count]
                FROM schlepps s
                GROUP BY s.pilot_id, substr(s.[datum],1,4)
                ORDER BY substr(s.[datum],1,4) desc, count(*) desc
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
        selected_report['report_id'] = report_id
        data = await get_report_data(selected_report['columns'],selected_report['sql'])
        selected_report['data'] = data

    return {
            'reports': {k:v['display_name'] for  k,v in REPORTS.items()},
            'selected_report': selected_report
            }

@streamer
async def file_sender(writer, xlsx_data=None):
    #print(type(xlsx_data))
    with io.BytesIO(xlsx_data) as f:
        chunk = f.read(2 ** 16)
        while chunk:
            await writer.write(chunk)
            chunk = f.read(2 ** 16)

async def export(request):
    report_id = request.match_info['report_id']
    selected_report = REPORTS[report_id] if report_id in REPORTS else None
    if selected_report:
        headers = {
            "Content-disposition": f'attachment; filename={report_id}.{datetime.now().strftime("%Y%d%m.%H%M%S")}.xlsx'
        }

        data = await get_report_data(selected_report['columns'],selected_report['sql'])       
        df = pd.DataFrame(data, columns=selected_report['columns'])
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name=selected_report['display_name'],index=False)
       
        return web.Response(
                body=file_sender(xlsx_data=output.getvalue()),
                headers=headers
            )

    # temp
    else:
        raise redirect(request.app.router, 'reports')