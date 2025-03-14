class Config:
    SECRET_KEY = 'WERYLONGSECRETKEYHAHAHAHAHHAHAHEOTIHJ*#%IDTH*#%Y@(#$T*HUEBGNSJDGB($#*@^Y(_&%^Y_(@&^Y$_(&T*YWOGHU:LJKSDGNPUIO$^YTdktjOITHJSODIH:SJNV:JOSDHGIUHEPTUIHSDJH(*$@#%((@_#%(@_#%(KGNSDKLGN"KLDGNSDLKGNSDGKLNSKLDGN))))))))))'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  # Example for SQLite
    SQLALCHEMY_TRACK_MODIFICATIONS = False
from celery import Celery

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)
    return celery