import pathlib

from .views import index, alle_winden, winde,aufbau, piloten,schlepps,schlepp_start, schlepp
from .report_views import reports, report
from .admin_views import backups, create_backup, remove_backup


PROJECT_ROOT = pathlib.Path(__file__).parent


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/winden',alle_winden, name='winden')
    app.router.add_get('/winden/{winde_id}',winde, name='winde')
    app.router.add_get('/winden/{winde_id}/aufbau', aufbau, name='aufbau') # to load protocol questions
    app.router.add_post('/winden/{winde_id}/aufbau', aufbau, name='aufbau') # to submit protocol
    # TODO add abbau

    app.router.add_get('/piloten',piloten, name='piloten')
    app.router.add_get('/schlepps',schlepps, name='schlepps')
    app.router.add_post('/schlepps',schlepp, name='schlepp')
    app.router.add_get('/schlepps/start',schlepp_start, name='schleppstart')
    # ...
    
    app.router.add_get('/reports',reports, name='reports')
    app.router.add_get('/reports/{report_id}',report, name='report')
    
    # ADMIN?
    app.router.add_get('/backups',backups, name='backups')
    app.router.add_get('/backups/create',create_backup, name='create_backup')
    app.router.add_get('/backups/remove',remove_backup, name='remove_backup')

    setup_static_routes(app)


def setup_static_routes(app):
    app['PROJECT_ROOT'] = PROJECT_ROOT
    app.router.add_static('/static/',
                          path=PROJECT_ROOT / 'static',
                          name='static')
    app.router.add_static('/backups_dl/',
                          path=PROJECT_ROOT / 'backups',
                          name='backups_dl')