import sys
import socket
import potsdb
import pyspeedtest
import functools
import logbook
from tornado.ioloop import PeriodicCallback, IOLoop

log = logbook.Logger('')
log.handlers.append(logbook.StreamHandler(sys.stdout, bubble=True))

client = potsdb.Client('tsdb')
st = pyspeedtest.SpeedTest()


def internet_connection(host='8.8.8.8', port=53, timeout=1000):
    s = None
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        return 1
    finally:
        if s is not None:
            s.close()


def generic_metric(metric_name, value_supplier):
    value = 0
    
    try:
        value = value_supplier()
    except KeyboardInterrupt:
        log.critical('Interrupted while collecting {}, exiting...', metric_name)
        sys.exit(2)
    except:
        log.exception('Error collecting {}:', metric_name)

    send_and_log(metric_name, value)


def send_and_log(metric_name, value):
    client.send(metric_name, value)
    log.debug('{}: {}', metric_name, value)


def main():    
    log.info('Starting...')
    log.debug('Registering callbacks')
    PeriodicCallback(functools.partial(generic_metric, 'internet.connection', internet_connection), 500).start()
    PeriodicCallback(functools.partial(generic_metric, 'internet.download', st.download), 120000).start()
    PeriodicCallback(functools.partial(generic_metric, 'internet.upload', st.upload), 120000).start()
    PeriodicCallback(functools.partial(generic_metric, 'internet.ping', st.ping), 120000).start()

    log.info('Starting loop')
    IOLoop.instance().start()


if __name__ == '__main__':        
    main()
