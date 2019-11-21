import base64
import configparser
from flask import Flask
from flask import request, jsonify, Response
from flasgger import Swagger
import psycopg2
from psycopg2.extras import RealDictCursor,DictCursor
from psycopg2.errors import UndefinedColumn, UniqueViolation
import json
from flask_caching import Cache
import configparser
import argparse

import sys
sys.path.append('../')

parser = argparse.ArgumentParser()
parser.add_argument("--prod", help="prod settings", action="store_true")
parser.add_argument("--dev", help="develop", action="store_true")
args = parser.parse_args()

config = configparser.ConfigParser()
config.read('../project_settings.ini')
HOST = config['Network']['host']
PORT = config['Network']['dev2_port']
if args.prod:
    PORT = 7000
elif args.dev:
    PORT = 7001

cache = Cache(config={'CACHE_TYPE': 'simple'})
app = Flask(__name__)
cache.init_app(app)
Swagger(app)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

SERVICES = {1: 'github', 2: 'screener', 3: 'community'}


def return_id_insert(user_hash, condition, service):
    with psycopg2.connect(dbname='', user='', password='', host='127.0.0.1') as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('insert into subscription(sub_hash, condition, service) values (%s, %s, %s)'
                        'on conflict(sub_hash) do update set upserted = TRUE returning id ;',
                        (user_hash, condition, service))
            subscription_id = cur.fetchone()['id']
    return subscription_id


def insert_in_users(user_id):
    with psycopg2.connect(dbname='', user='', password='', host='127.0.0.1') as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('insert into users values (%s) on conflict do nothing;', (user_id,))
    return 1


def in_contact_del_sub(user_id: str, channels: dict, subscription_id: int):
    ids = []
    with psycopg2.connect(dbname='', user='', password='', host='127.0.0.1') as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            channel_to_delete = tuple(channels.keys())
            # TODO check this
            cur.execute(f'delete from each_sub where user_id like %s and sub_id in (%s);',
                        (user_id, subscription_id))
            # channel_id - keys of channels dict
            for channel_id in channels:
                # username, email etc.
                data = channels[channel_id]
                cur.execute('select id from contacts where user_id = %s and ch_id = %s and data like %s;',
                            (user_id, int(channel_id), data))
                ch_id = cur.fetchone()
                if ch_id:
                    # we needn't contacts id that already exists ?
                    ids.append(ch_id['id'])
                    continue
                cur.execute('insert into contacts(user_id, data, ch_id) values (%s, %s, %s) returning id;',
                            (user_id, data, int(channel_id)))
                ids.append(cur.fetchone()['id'])
    return ids


def insert_in_each_sub(subscription_id, user_id, subscription_name, contact_ids: list, disposable):
    ids = []
    with psycopg2.connect(dbname='', user='', password='', host='127.0.0.1') as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            for c_id in contact_ids:
                cur.execute('insert into each_sub(contact_id, user_id, sub_id, user_sub_name, disposable) '
                            'values (%s,%s,%s,%s,%s) returning id;',
                            (c_id, user_id, subscription_id, subscription_name, disposable))
                ids.append(cur.fetchone()['id'])
    return ids


def insert_in_expire(each_sub_ids: list):
    with psycopg2.connect(dbname='', user='', password='', host='127.0.0.1') as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            for ids in each_sub_ids:
                cur.execute(f'insert into expire(each_sub_id, last_select) values (%s) returning id;', (ids, 0))
                ids = cur.fetchone()['id']
    return ids


@app.route('/cudSubscription', methods=['POST'])
def method_1():
    """
            API
            ---
            tags:
              - Return table of currency stats
            parameters:
              - name: info
                in: body
                type: json
                description: dict description in wrike
            responses:
              400:
                description: Bad request
              200:
                description: OK
              500:
                description: INTERNAL SERVER ERROR
              401:
                description: Unauthorized


    """
    data: dict = request.get_json()
    user_id, channels, service_id, condition, sub_name, disposable = \
        data['id'], data['channels'], data['service'], data['condition'], data['subscription_name'], data['disposable']
    encode_str = f'{SERVICES[service_id]}-{str(condition)}'.encode()
    user_hash = base64.b64encode(encode_str)
    json_condition = json.dumps(condition)  # maybe need return to rewrite condition
    service = SERVICES.get(service_id)

    subscription_id = return_id_insert(user_hash, json_condition, service)
    res_users = insert_in_users(user_id)
    contacts_ids = in_contact_del_sub(user_id, channels, subscription_id)
    each_sub_ids = insert_in_each_sub(subscription_id, user_id, sub_name, contacts_ids, disposable)

    if subscription_id and res_users and contacts_ids and each_sub_ids:
        return Response("OK", status=200)
    else:
        return Response("Not OK", status=500)


@app.route('/getChannels', methods=['GET'])
def method_2():
    """
            API
            ---
            tags:
              - Return table of currency stats
            parameters:
              - name: table
                in: query
                type: string
                description: services or channel you want
              - name: key
                in: query
                type: string
                description: key of service
            responses:
              499:
                description: Bad key in dict
              400:
                description: Bad request
              200:
                description: OK
              500:
                description: INTERNAL SERVER ERROR
              401:
                description: Unauthorized


    """
    table_name = request.args.get('table') or 'channel'
    key = request.args.get('key')
    with psycopg2.connect(dbname='', user='', password='', host='127.0.0.1') as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f'select * from {table_name}')
            data = cur.fetchall()
    temp = {raws['id']: raws['name_of_service'] for raws in data}
    if not isinstance(key, type(None)):
        try:
            return Response(json.dumps(temp[int(key)]), mimetype='application/json')
        except KeyError:
            return Response(response='bad key', status=499)
    return Response(json.dumps(temp), mimetype='application/json')


@app.route('/getMySubscribes', methods=['GET'])
def method_3():
    """
                API
                ---
                tags:
                  - Return table of currency stats
                parameters:
                  - name: user id
                    in: query
                    type: string
                    description: user id
                    required: True
                responses:
                  499:
                    description: Bad key in dict
                  400:
                    description: Bad request
                  200:
                    description: OK
                  500:
                    description: INTERNAL SERVER ERROR
                  401:
                    description: Unauthorized


        """
    # TODO need add validation and exception
    user_id = request.args.get('user id')
    with psycopg2.connect(dbname='', user='', password='', host='127.0.0.1') as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            sql = '''
                select each_sub.id as subscription_id, each_sub.user_sub_name, s.service, s.condition, c.data from each_sub
                inner join subscription s on each_sub.sub_id = s.id
                inner join contacts c on each_sub.contact_id = c.id;
                  '''
            cur.execute(sql)
            data = cur.fetchall()
    return json.dumps(data)


@app.route('/deleteSubscriptions', methods=['POST'])
def method_4():
    """
                API
                ---
                tags:
                  - Return table of currency stats
                parameters:
                  - name: to delete
                    in: body
                    type: json
                    description: dict {user_id:, subscription_id:[list]}
                responses:
                  499:
                    description: Bad key in dict
                  400:
                    description: Bad request
                  200:
                    description: OK
                  500:
                    description: INTERNAL SERVER ERROR
                  401:
                    description: Unauthorized


        """
    data = request.get_json()
    user_id = data['user_id']
    sub_id = data['subscription_id']
    with psycopg2.connect(dbname='', user='', password='', host='127.0.0.1') as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            for s_id in sub_id:
                cur.execute('delete from each_sub where id = %s and user_id like %s', (s_id, user_id))
    return Response('OK', status=200)


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=False)


'''
{"id": "1",
"channels": {"1": "", "0": ""},
"service":1,
"condition": {"value": 50},
"subscription_name": "test"}
'''


