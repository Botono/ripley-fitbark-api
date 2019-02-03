from google.oauth2 import service_account

from config import config
import utils


def load_credentials(api):
    SERVICE_ACCOUNT_FILE = 'credentials.json'
    scopes = []
    if api == 'sheets':
        scopes.append('https://www.googleapis.com/auth/spreadsheets')

    try:
        if not config.get('googleAPICreds'):
            utils.debug_log('Getting new Google Creds')
            credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=scopes)
            config['googleAPICreds'] = credentials
        else:
            utils.debug_log('Using cached Google Credentials. Expiry: {0}'.format(
                config.get('googleAPICreds').expiry))
    except Exception as e:
        raise e
