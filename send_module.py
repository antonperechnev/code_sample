from DB.tables import LostMessages, Expire, EachSub, Contacts, Users, DelayMessages

from sqlalchemy import MetaData, desc, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.util import KeyedTuple
from sqlalchemy.pool import NullPool
from DB.tables import Channel

import configparser
import requests
import logging
import backoff
import json
import time
import sys
import os

vyselect = {1: sys.maxsize}

engine = create_engine('engine',
                       poolclass=NullPool)

config = configparser.ConfigParser()
config.read("../Config/project_settings.ini")
file = os.path.splitext(os.path.basename(__file__))[0]

logging.basicConfig(format='%(threadName)s - %(name)s - %(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    level=logging.INFO, filename=f'../logs/{file}.log')
logger = logging.getLogger(file)

Session = sessionmaker(engine)


class DBHandler:
    def __init__(self, subscription_id, channel_id: int = 0):
        self.sub_id = subscription_id
        self.ch_id = channel_id

    def create_contacts(self, disposable) -> dict:
        session = Session()
        query = session.query(EachSub) \
            .filter(EachSub.active == 1,
                    EachSub.sub_id == self.sub_id,
                    Expire.last_select < time.time() - EachSub.to_expire,
                    Contacts.ch_id == self.ch_id,
                    EachSub.disposable == disposable) \
            .join(EachSub.expire) \
            .join(EachSub.contacts)

        contacts = [c[0] for c in query.values(Contacts.data)]
        each_sub_id = [ids[0] for ids in query.values(EachSub.id)]
        sub_names = [name[0] for name in query.values(EachSub.user_sub_name)]
        contacts_id = {'contacts': contacts, 'ids': each_sub_id, 'sub_names': sub_names}
        session.close()
        return contacts_id

    def membership(self):
        session = Session()
        query = session.query(EachSub).filter(EachSub.sub_id == self.sub_id)\
            .join(EachSub.subscription).distinct(Users.subscription)
        members = [member.subscription for member in query.values(Users.subscription)]
        session.close()
        return members

    @staticmethod
    def update_expire(ids: list):
        session = Session()
        last_select = int(time.time())
        for each_sub_id in ids:
            session.query(Expire).filter(Expire.each_sub_id == each_sub_id).update(
                {Expire.last_select: last_select})
        session.commit()
        session.close()

    def make_unactive(self):
        session = Session()
        session.query(EachSub).filter(EachSub.sub_id == self.sub_id,
                                      Contacts.ch_id == self.ch_id,
                                      EachSub.disposable == 1)\
                              .update({EachSub.active: 0}, synchronize_session='fetch')
        session.commit()
        session.close()


class AlertHandler:
    def __init__(self, message, channel, addresses: list, wit_sub_name=1):
        self.url = config['Push Alert']['url']  # take from config
        self.message = message
        self.channel = channel
        self.addresses = addresses
        self.headers = {'Content-Type': 'application/json'}
        self.data = {'message': self.message, 'channel': self.channel, 'address': self.addresses,
                     'sub_names': wit_sub_name}

    @backoff.on_exception(backoff.expo, ConnectionError, max_tries=3)
    def send_alert(self):
        try:
            resp: requests.Response = requests.post(url=self.url, headers=self.headers,
                                                    json=self.data)
            if resp.status_code == 429:
                time.sleep(10)
                raise ConnectionError
            return resp.status_code
        # if API not allowed save data to db
        except requests.exceptions.RequestException as e:
            session = Session()
            lost = LostMessages(data=json.dumps(self.data))
            session.add(lost)
            session.commit()
            session.close()
            logger.warning(f'exception {e}, insert addresses to db')

    def simple_send(self):
        try:
            resp: requests.Response = requests.post(url=self.url, headers=self.headers,
                                                    json=self.data)
            return resp.status_code
        except requests.exceptions.RequestException:
            return 0


class Alert:
    def __init__(self, subscription_id, message):
        self.sub_id = subscription_id
        self.message = message

    def send(self, delay=0, screener: bool = False):
        session = Session()
        disposable = KeyedTuple(session.query(EachSub).distinct(EachSub.disposable).values(
            EachSub.disposable))
        channels = KeyedTuple(session.query(Channel).values(Channel.id))
        for channel in channels:
            for logic in disposable:

                ch_id = channel.id
                expire_logic = logic.disposable
                with_sub_name = 1

                db = DBHandler(subscription_id=self.sub_id, channel_id=ch_id)
                query: dict = db.create_contacts(expire_logic)
                contacts = query['contacts']
                each_sub_id = query['ids']
                user_sub_names = query['sub_names']
                # new block for BFG
                if ch_id == 2:
                    message = self.message['BFG']
                    with_sub_name = 0
                else:
                    message = [self.message['regular'].substitute(user_sub_name=sub) for sub in
                               user_sub_names]

                if delay and contacts:
                    self.delay_send(message=message, session=session,
                                    contacts=contacts, ch_id=ch_id)
                else:
                    alert = AlertHandler(message, ch_id, contacts, wit_sub_name=with_sub_name)
                    alert.send_alert()

                if screener:
                    continue
                db.make_unactive() if expire_logic else db.update_expire(each_sub_id)
        session.close()

    @staticmethod
    def delay_send(message, session, contacts, ch_id):
        send_time = int(time.time()) + int(config['Message Delay']['delay'])
        row = DelayMessages(contacts=contacts, send_time=send_time,
                            message=json.dumps(message), ch_id=ch_id)
        session.add(row)
        session.commit()
        

if __name__ == '__main__':
    pass
