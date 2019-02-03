from config import config

def debug_log(msg):
    if config.get('debug_mode'):
        print('[DEBUG] {0}'.format(msg))


def safe_list_get(l, idx, default):
  try:
    return l[idx]
  except IndexError:
    return default
