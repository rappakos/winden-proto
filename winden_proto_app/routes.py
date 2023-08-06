import pathlib

from .views import index, alle_winden, winde,aufbau, piloten,schlepps


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
    # ...
    setup_static_routes(app)


def setup_static_routes(app):
    app.router.add_static('/static/',
                          path=PROJECT_ROOT / 'static',
                          name='static')