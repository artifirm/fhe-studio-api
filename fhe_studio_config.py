import os
import pymongo

database_url = os.environ.get("DATABASE_URL", "localhost")
myclient = pymongo.MongoClient(f"mongodb://{database_url}")
mongo_db_instance_ = myclient["fhe_studio"]

def eval_keys_path():
    return os.environ.get("EVAL_KEY_PATH", ".")

def mongo_db_instance():
    return mongo_db_instance_