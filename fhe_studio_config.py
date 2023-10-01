import os
import pymongo
import mongomock

database_url = os.environ.get("DATABASE_URL", "")

if database_url != "":
    print(f"- USING DATABASE- : {database_url}")
    myclient = pymongo.MongoClient(f"mongodb://{database_url}")
    mongo_db_instance_ = myclient["fhe_studio"]
else:
    print("--- USING MOCK DATABASE ---")
    mongo_db_instance_ = mongomock.MongoClient().db


def eval_keys_path():
    return os.environ.get("EVAL_KEY_PATH", ".")

def mongo_db_instance():
    return mongo_db_instance_