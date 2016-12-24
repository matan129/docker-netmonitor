import sys
import socket
import potsdb
import urllib2
import pyspeedtest
import logbook
from tornado.ioloop import PeriodicCallback, IOLoop


log = logbook.Logger('')
log.handlers.append(logbook.StreamHandler(sys.stdout, bubble=True))

client = potsdb.Client('tsdb')
st = pyspeedtest.SpeedTest()


def internet(host='8.8.8.8', port=53, timeout=1000):
    s = None
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        value = 1
    except Exception as ex:    
        log.exception()
        value = 0
    finally:
        if s is not None:
            s.close()
    
    client.send('internet.connection', value)


def download():
    value = 0

    try:
        value = st.download()
    except Exception as ex:
        log.exception()

    client.send('internet.download', value)
    log.info('internet.download: {}', value)


def upload():
    value = 0

    try:
        value = st.upload()
    except Exception as ex:
        log.exception()

    client.send('internet.upload', value)
    log.info('internet.upload: {}', value)


def ping():
    value = 0

    try:
        value = st.ping()
    except Exception as ex:
        log.exception()

    client.send('internet.ping', value)
    log.info('internet.ping: {}', value)


log.info('Test run...')
internet()
download()
upload()
ping()

log.info('Registering callbacks')
PeriodicCallback(internet, 1).start()
PeriodicCallback(download, 120000).start()
PeriodicCallback(upload, 120000).start()
PeriodicCallback(ping, 120000).start()

log.info('Starting loop')
IOLoop.instance().start()
