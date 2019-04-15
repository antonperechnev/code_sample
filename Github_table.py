import requests
from requests import Session
from requests.auth import HTTPProxyAuth
import random
from random import randint, choice
import json
from datetime import datetime
import psycopg2
import time
import urllib.parse
from threading import Thread
import threading
from bs4 import BeautifulSoup
import schedule
import smtplib
from email.message import EmailMessage

'''Работа с Api Github'''

with open('https_proxy.json') as f:
        da = json.load(f)


def notification(dic, auth):
    msg = EmailMessage()
    msg.set_content({0: f'i am {auth}, all fine'}.get(len(dic), f'check me, i am {auth}'))
    msg['Subject'] = 'Table'
    s = smtplib.SMTP('smtp.yandex.ru')
    s.starttls()
    s.login('StipsOc@yandex.ru', 'StipsOCULUS1')
    s.sendmail('StipsOc@yandex.ru', 'perechnev@stips.io', msg.as_string())
    s.quit()


def create_data_for_db(data, user, repo, total_commit, month_commit):
    api_url = [f'https://your_login:your_password@api.github.com/repos/{user}/{repo}/stats/participation',
               f'https://your_login:your_password@api.github.com/repos/{user}/{repo}/stats/participation',
               f'https://your_login:your_password@api.github.com/repos/{user}/{repo}/stats/participation'][choice([0,1,2])]
    resp = requests.get(api_url)#, proxies=proxies)
    try:
        d_52 = resp.json()
        data.append(sum(d_52["all"]))
        data.append(sum(d_52["all"][-4:]))
        data.append(d_52["all"][-1])
        data.sort(reverse=True)
        return {'data': data[:3], 'code': resp.status_code, 'error': 0}
    except TypeError:
        return {'data': d_52, 'code': resp.status_code, 'error': 1}
    except json.decoder.JSONDecodeError:  # РѕР±СЂР°Р±РѕС‚РєР° РїСѓСЃС‚РѕРіРѕ СЂРµРїРѕР·РёС‚РѕСЂРёСЏ
        return {'data': '', 'code': resp.status_code, 'error': 2}
    except IndexError:
        return {'data': d_52, 'code': resp.status_code, 'error': 3}
    except KeyError:
        return {'data': d_52, 'code': resp.status_code, 'error': 4}


def auto_proxy(x):
    list_of_proxy = []
    with open('https_proxy.json') as f:
        dat = json.load(f)
        for i in dat:
            list_of_proxy.append(i.rstrip('\n').split(':'))
    return [':'.join(i[:2]) for i in list_of_proxy][x]


def stat_year(user, repo):
    data = []
    total_commit = []
    month_commit = []
    data_and_stat = create_data_for_db(data, user, repo, total_commit, month_commit)
    if data_and_stat['code'] is 200:
        return data_and_stat#, resp)
    elif data_and_stat['code'] is 202:
        return create_data_for_db(data, user, repo, total_commit, month_commit)
    elif data_and_stat['code'] is 204:
        return data_and_stat
    else:
        return data_and_stat


def db_ins():
    f = open('data_test.json')
    data = json.load(f)
    for i in data:
        if i:
            try:
                print(i[0], stat_year(i[0])['data'])
            except TypeError:
                a, b , c, d = stat_year(i[0])['data']
            a, b, c, d = stat_year(i[0])['data']
            ins(i[0].split('/')[-1], a, b, c, d)
        else:
            print(i)
            continue


def ins(name, a, b, c, d):
    with psycopg2.connect(dbname='api', user='postgres', password='Anton1995', host='127.0.0.1') as conn:
        with conn.cursor() as cur:
            cur.execute('insert into tickers values (%s,%s,%s,%s,%s);', (name, a, b, c, d))


def repos_for_hub(user: str):
    if not user.isalpha():
        user = user.split('?')[0]
    api_url = f'https://your_login:your_password@api.github.com/users/{user}/repos'
    resp = requests.get(api_url)  # , proxies=proxies)
    d = resp.json()
    if resp.status_code is 202:
        time.sleep(2)
        resp = requests.get(api_url)  # , proxies=proxies)
    if (resp.status_code is not 200) or not d:
        return {"code": 404,
                "message": d,
                "true code": resp.status_code}

    user = d[0]["full_name"].split('/')[-2]
    repo = []
    forks = []
    stargazers = []
    if len(d) == 1:
        repo.append(d[0]["full_name"].split('/')[-1])
        forks.append(d[0]["forks_count"])
        stargazers.append(d[0]["stargazers_count"])
    else:
        for i in range(len(d)):
            repo.append(d[i]["full_name"].split('/')[-1])
            forks.append(d[i]["forks_count"])
            stargazers.append(d[i]["stargazers_count"])
    return {
            "user": user,
            "repo": repo,
            "length": len(d),
            "forks": sum(forks),
            "stargazers": sum(stargazers),
            "code": resp.status_code
            }


def commits_all(user, repo):
    url = f'https://github.com/{user}/{repo}'
    proxi = random.choices(da, [1, 1, 1, 1, 1, 1])[0]
    proxie = {'https': 'https://eefuosho:0WnTysAp@{}:51689/'.format(proxi)}
    d = ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0',
         'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
         'Mozilla/4.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'][random.randint(0, 2)]
    headers = {
        'User-Agent': d
               }
    resp = requests.get(url, proxies=proxie, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    commits = soup.find('span', class_="num text-emphasized")
    if resp.status_code == 200:
        return int(commits.get_text().strip().replace(',', ''))
    else:
        print(resp.status_code, proxie, user, repo)


def func_year(ind=None, lst=None):
    with open('nice.json') as f:
        dat = json.load(f)[ind:lst]
        error_list = []
        log_list = []
        for i in dat:
            if len(i) > 1 and len(i[1]) == 2:
                try:
                    user = i[1][0]
                    repo = i[1][1]
                    a = stat_year(user, repo)
                    if a['error'] is 0:
                        forks_star = repos_for_hub(user)
                        all_commits = commits_all(user, repo)
                        if isinstance(all_commits, type(None)):
                            log_list.append((user, repo))
                            all_commits = a['data'][0]
                        try:
                            stargazers = forks_star['stargazers']
                            forks = forks_star['forks']

                            conn = psycopg2.connect(dbname='db_name', user='user', password='password',
                                                    host='127.0.0.1')
                            cur = conn.cursor()

                            #cur.execute('insert into tickers values (%s, %s, %s, %s, %s, %s, %s, %s)', (i[0], user, a['data'][0], a['data'][1], a['data'][2], forks, stargazers, all_commits))
                            cur.execute('update tickers set year=%s, month=%s, week=%s, forks=%s, star=%s, all_commits=%s where full_name like %s',
                                        (a['data'][0], a['data'][1], a['data'][2], forks, stargazers, all_commits, user))
                            conn.commit()
                            cur.close()
                            conn.close()
                        except KeyError:
                            forks_star = repos_for_hub(user)
                            print(i, forks_star)
                            if forks_star['code'] == 404:
                                print('not valid')
                                continue
                            stargazers = forks_star['stargazers']
                            forks = forks_star['forks']
                            conn = psycopg2.connect(dbname='db_name', user='user', password='password',
                                                    host='127.0.0.1')
                            cur = conn.cursor()

                            #cur.execute('insert into tickers values (%s, %s, %s, %s, %s, %s, %s, %s)', (i[0], user, a['data'][0], a['data'][1], a['data'][2], forks, stargazers, all_commits))
                            cur.execute('update tickers set year=%s, month=%s, week=%s, forks=%s, star=%s, all_commits=%s where full_name like %s',
                                        (a['data'][0], a['data'][1], a['data'][2], forks, stargazers, all_commits, user))
                            conn.commit()
                            cur.close()
                            conn.close()
                            error_list.append(user)
                            continue
                        except psycopg2.Error as e:
                            print(i, e.pgerror)
                            continue
                    else:
                        continue
                except requests.exceptions.ConnectionError:
                    log_list.append(i)
            if len(i) > 1 and len(i[1]) == 1:
                ticker = i[0]
                user = i[1][0]
                temp_d = []
                a = []
                b = []
                c = []
                all_comm = []
                repos = repos_for_hub(user)
                if repos["code"] is 202:
                    repos_for_hub(user)
                if repos["code"] is not 200:
                    continue
                repo = repos['repo']  # data from dict repos_for_hub
                for j in range(repos['length']):
                    stat = stat_year(user, repo[j])
                    if stat['error'] is not 0:
                            continue
                    temp_d.append(stat['data'])
                    all_commits = commits_all(user, repo[j])
                    if isinstance(all_commits, type(None)):
                        all_comm.append(stat['data'][0])
                        log_list.append((user, repo[j]))
                    else:
                        all_comm.append(all_commits)
                for j in temp_d:
                    try:
                        a.append(j[0])
                        b.append(j[1])
                        c.append(j[2])
                    except KeyError:
                        print(temp_d)
                        break
                fork = repos['forks']
                stargazer = repos['stargazers']
                try:
                    conn = psycopg2.connect(dbname='api_test', user='postgres', password='Anton1995',
                                            host='127.0.0.1')
                    cur = conn.cursor()
                    #cur.execute('insert into tickers values (%s, %s, %s, %s, %s, %s, %s, %s)', (ticker, user, sum(a), sum(b), sum(c), fork, stargazer, sum(all_comm)))
                    cur.execute(
                        'update tickers set year=%s, month=%s, week=%s, forks=%s, star=%s, all_commits=%s where full_name like %s',
                        (sum(a), sum(b), sum(c), fork, stargazer, sum(all_comm), user))
                    conn.commit()
                    cur.close()
                    conn.close()
                except psycopg2.Error as e:
                    print(i, e.pgerror)
                    continue
        notification(log_list, ind)
        with open(f'error{ind}.json', 'w') as h:
            json.dump(log_list, h)


def run_threaded(func, args):
    job_thread = threading.Thread(target=func, args=args)
    job_thread.start()
    print(job_thread)


schedule.every().day.at("05:00").do(run_threaded, func_year, (0, 300))
schedule.every().day.at("05:00").do(run_threaded, func_year, (301, 600))
schedule.every().day.at("05:00").do(run_threaded, func_year, (601, 900))
schedule.every().day.at("05:00").do(run_threaded, func_year, (901, 1200))
schedule.every().day.at("05:00").do(run_threaded, func_year, (1201, 1500))
schedule.every().day.at("05:00").do(run_threaded, func_year, (1501, ))


schedule.every().day.at("11:00").do(run_threaded, func_year, (0, 300))
schedule.every().day.at("11:00").do(run_threaded, func_year, (301, 600))
schedule.every().day.at("11:00").do(run_threaded, func_year, (601, 900))
schedule.every().day.at("11:00").do(run_threaded, func_year, (901, 1200))
schedule.every().day.at("11:00").do(run_threaded, func_year, (1201, 1500))
schedule.every().day.at("11:00").do(run_threaded, func_year, (1501, ))


schedule.every().day.at("17:00").do(run_threaded, func_year, (0, 300))
schedule.every().day.at("17:00").do(run_threaded, func_year, (301, 600))
schedule.every().day.at("17:00").do(run_threaded, func_year, (601, 900))
schedule.every().day.at("17:00").do(run_threaded, func_year, (901, 1200))
schedule.every().day.at("17:00").do(run_threaded, func_year, (1201, 1500))
schedule.every().day.at("17:00").do(run_threaded, func_year, (1501, ))


schedule.every().day.at("02:00").do(run_threaded, func_year, (0, 300))
schedule.every().day.at("02:00").do(run_threaded, func_year, (301, 600))
schedule.every().day.at("02:00").do(run_threaded, func_year, (601, 900))
schedule.every().day.at("02:00").do(run_threaded, func_year, (901, 1200))
schedule.every().day.at("02:00").do(run_threaded, func_year, (1201, 1500))
schedule.every().day.at("02:00").do(run_threaded, func_year, (1501, ))


while 1:
    schedule.run_pending()
    time.sleep(1)


#thread1 = Thread(target=func_year, args=(0, 300))
#thread5 = Thread(target=func_year, args=(301, 600))
#thread2 = Thread(target=func_year, args=(601, 900))  # С‚РѕР¶Рµ РјРµРґР»РµРЅРЅРѕ СЂР°Р±РѕС‚Р°РµС‚
#thread6 = Thread(target=func_year, args=(901, 1200))
#thread3 = Thread(target=func_year, args=(1201, 1500))
#thread4 = Thread(target=func_year, args=(1501, ))
#thread7 = Thread(target=func_year, args=(1501, ))


#thread1.start()
#print(thread1)
#thread2.start()
#print(thread2)
#thread3.start()
#print(thread3)
#thread4.start()
#print(thread4)
#thread5.start()
#print(thread5)
#thread6.start()
#print(thread6)
#thread7.start()
#print(thread7)


#thread1.join()
#print(thread1, threading.active_count())
#thread2.join()
#print(thread2, threading.active_count())
#thread3.join()
#print(thread3, threading.active_count())
#thread4.join()
#print(thread4, threading.active_count())
#thread5.join()
#print(thread5, threading.active_count())
#thread6.join()
#print(thread6, threading.active_count())
#thread7.join()
#print(thread7, threading.active_count())

#print(time.time()-start)


