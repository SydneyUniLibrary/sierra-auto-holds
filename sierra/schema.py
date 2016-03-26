from django.db.backends.signals import connection_created


def set_search_path(sender, **kwargs):
    conn = kwargs.get('connection')
    if conn is not None:
        conn_params = conn.get_connection_params()
        conn_database = conn_params.get('database')
        conn_port = conn_params.get('port')
        if conn_database == 'iii' and conn_port == 1032:
            cursor = conn.cursor()
            cursor.execute("SET search_path=sierra_view")


def hook_up_set_search_path():
    connection_created.connect(set_search_path)
