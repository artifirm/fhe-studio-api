import os
import pymongo
import mongomock
from flask import request
import requests
from expiringdict import ExpiringDict
import logging

cache = ExpiringDict(max_len=100000, max_age_seconds = 60 * 60)

database_url = os.environ.get("DATABASE_URL", "")
use_oauth2 = os.environ.get("USE_OAUTH2", "0")

if database_url != "":
    logging.info(f"- USING DATABASE- : {database_url}")
    myclient = pymongo.MongoClient(f"mongodb://{database_url}")
    mongo_db_instance_ = myclient["fhe_studio"]
else:
    logging.info("--- USING MOCK DATABASE ---")
    mongo_db_instance_ = mongomock.MongoClient().db


def eval_keys_path():
    return os.environ.get("EVAL_KEY_PATH", ".")

def mongo_db_instance():
    return mongo_db_instance_

def user_info():
    token = request.headers["authorization"]
    if token not in cache:
        cache[token] = user_info_impl(token)
    logging.debug(f'user_info: ${cache[token]}')
    return cache[token]

def user_sub_or_default(sub_default):
    token = request.headers.get("authorization", None)
    if token is None:
        return sub_default
    return user_info()['sub']

def user_info_impl(token):
    if use_oauth2 != '0':
        logging.debug(f'validating new token')
        headers = {'Accept': 'application/json',
                   'Authorization': token }
        response = requests.get('https://openidconnect.googleapis.com/v1/userinfo', headers = headers)
        if response.status_code!= 200:
            raise Exception("USER_NOT_AUTHORIZED")
        
        r = response.json()
        logging.debug(f'validated token, response: ${r}')
        return {
            'email': r['email'],
            'sub': r['sub'],
            'picture': r['picture'],
            'email_verified': r['email_verified'],
        }  
    else:
        return {
            'email': 'dev-user@example.com',
            'sub': 'dev-id',
            'picture': None,
            'email_verified': True
        }  

def user_sub():
    u = user_info()
    logging.debug(f'user: {str(u)}')
    return user_info()['sub']
