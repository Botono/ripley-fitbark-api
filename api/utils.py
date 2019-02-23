from config import config
import boto3
import dateutil.parser as parser

def debug_log(msg):
    if config.get('debug_mode'):
        print('[DEBUG] {0}'.format(msg))

def get_db():
    if config['db'] is None:
        config['db'] = boto3.resource('dynamodb', region_name=config['region'])

def safe_list_get(l, idx, default):
    try:
        return l[idx]
    except IndexError:
        return default

def is_date(s):
    try:
        date = parser.parse(s)
        return True
    except ValueError:
        debug_log('"{0}" is not a date'.format(s))
        return False

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        debug_log('"{0}" is not a number'.format(s))
        return False
