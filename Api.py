from flask import Flask
from flask import request
from flask import jsonify
import requests
import json
import random
from flasgger import Swagger
from flasgger.utils import swag_from
import psycopg2
from datetime import datetime, timezone
app = Flask(__name__)
Swagger(app)


@app.route('/api/table', methods=['GET'])
def stats_return():
    """
            This is awesome API
            Call this api passing a language name and get back its features
            ---
            tags:
              - Return table of tickers stats
            parameters:
              - name: sorted_by
                in: query
                type: string
                description: example 1y, all
              - name: limit
                in: query
                type: integer
                format: int64
                description: 100
              - name: offset
                in: query
                type: integer
                format: int64
                description: 0
            responses:
              500:
                description: Server Error!
              200:
                description: ticker stats
                schema:
                  id: 123
                  properties:
                    body:
                      type: array
                      description: table of tickers
                      default: None


            """
    try:
        conn = psycopg2.connect(dbname='api_test', user='postgres', password='Anton1995', host='127.0.0.1')
        cur = conn.cursor()

        sorted_by = ['1y', '1m', '1w', 'star', 'forks', 'all']
        sql_sorted_by = ['year', 'month', 'week', 'star', 'forks', 'all_commits']

        limit = 100  # default limit
        offset = 0  # default offset
        sort_name = 'year'  # default column for sort
        ind_in_sql = 0
        if request.args.get('sorted_by'):
            sort_name = request.args.get('sorted_by')
        if isinstance(request.args.get('sorted_by'), type(None)):
            column_name = 'year'
        else:
            ind_in_sql = sorted_by.index(sort_name)
            column_name = sql_sorted_by[ind_in_sql]        
        if request.args.get('limit'):
            limit = request.args.get('limit')
        if request.args.get('offset'):
            offset = request.args.get('offset')

        sql = f'select ticker, full_name, all_commits, year, month, week, forks, star from tickers ' \
            f'order by {column_name} desc limit {limit} offset {offset};'
        cur.execute(sql)
        data = cur.fetchall()
        return jsonify(data)
    except ValueError:
        return 'Valid period is ["1y", "1m", "1w", "star", "forks", "all"]'


@app.route('/api/ticker', methods=['GET'])
def stat_return():
    """
        This is awesome API
        Call this api passing a language name and get back its features
        ---
        tags:
          - Return one ticker stat in on year
        parameters:
          - name: ticker_name
            in: query
            type: string
            description: something
            required: true
          - name: timestamp_1
            in: query
            type: integer
            format: int64
            description: something
          - name: timestamp_2
            in: query
            type: integer
            format: int64
            description: something
        responses:
          500:
            description: Server Error!
          200:
            description: ticker stats
            schema:
              id: 123
              properties:
                language:
                  type: string
                  description: The ticker name
                  default: None


        """
    year = int(datetime.now(tz=timezone.utc).strftime('%d/%m/%Y').split('/')[-1])
    month = int(datetime.now(tz=timezone.utc).strftime('%d/%m/%Y').split('/')[-2])
    day = int(datetime.now(tz=timezone.utc).strftime('%d/%m/%Y').split('/')[0])
    timestamp_now = datetime.timestamp(datetime(year, month, day, tzinfo=timezone.utc))

    conn = psycopg2.connect(dbname='api_test', user='postgres', password='Anton1995', host='127.0.0.1')
    cur = conn.cursor()

    ping = None
    time_1 = timestamp_now # default limit
    time_2 = 1  # default offset
    sort_name = 'year'  # default column for sort
    arg = 'name_'
    ping = 0
    if request.args.get('timestamp_1'):
        ping = 1
        time_1 = request.args.get('timestamp_1')
    if request.args.get('timestamp_2'):
        ping = 2
        time_2 = request.args.get('timestamp_2')
    if time_1 and time_2:#ping == 2 or ping == 0:
        print(0)
        sql = f'select * from {arg+request.args.get("ticker_name")} where date between {time_2} and {time_1} order by date desc;'
        cur.execute(sql)
    if ping == 1:
        sql = f'select * from {arg+request.args.get("ticker_name")} where date <= {time_1} order by date desc ;'
        cur.execute(sql)
        print(1)
    if (ping == 2) and isinstance(request.args.get('timestamp_1'), type(None)):
        sql = f'select * from {arg+request.args.get("ticker_name")} where date >= {time_2} order by date desc ;'
        cur.execute(sql)
        print(2)
    data = cur.fetchall()
    return jsonify(data)


if __name__ == '__main__':
    app.run()  # 127.0.0.1/apidocs
