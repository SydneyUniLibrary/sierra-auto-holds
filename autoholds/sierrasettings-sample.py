# TODO: Copy this file to sierrasettings.py and
# edit the setting towards the bottom of this file


class SierraApiSettings:

    def __init__(self, **kwargs):
        self.base_url = kwargs['base_url']
        self.client_key = kwargs['client_key']
        self.client_secret = kwargs['client_secret']

    def __str__(self):
        return str(self.base_url)

    def __repr__(self):
        return 'SierraApiSettings(base_url=%r)' % self.base_url


class SierraSqlSettings:

    def __init__(self, **kwargs):
        self.host = kwargs['host']
        self.port = kwargs['port']
        self.user = kwargs['user']
        self.password = kwargs['password']

    def __str__(self):
        return str(self.host)

    def __repr__(self):
        return 'SierraSqlSettings(host=%r, port=%r)' % (self.host, self.port)


SIERRA_API = SierraApiSettings(
        base_url='https://sierra-app-server.mylibrary.url/iii/sierra-api',
        client_key='ABCDefgh1234',
        client_secret='password',
)


SIERRA_SQL = SierraSqlSettings(
    host='sierra-db-server.mylibrary.url',
    port=1032,
    user='sql-enabled-sierra-user',
    password='password',
)
