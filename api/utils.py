from config import config
import boto3
import dateutil.parser as parser

def debug_log(msg):
    if config.get('debug_mode'):
        print('[DEBUG] {0}'.format(msg))


def error_log(msg):
    errMsg = '[ERROR] {0}'.format(msg)
    print(errMsg)
    return { 'error': msg }

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

def format_date(date):
    date = parser.parse(date).strftime("%Y-%m-%d")

    return date

# https://gist.github.com/pgolding/231f5ce02b7e1fd16a7edc656aa8433e
def build_update_expression(data):
    vals = {}
    exp = 'SET '
    attr_names = {}
    for key, value in data.items():
        vals[':{}'.format(key)] = value
        attr_names['#pf_{}'.format(key)] = key
        exp += '#pf_{} = :{},'.format(key, key)
    exp = exp.rstrip(",")
    return vals, exp, attr_names
