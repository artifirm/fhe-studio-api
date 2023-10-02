import pymongo
import json
from bson.objectid import ObjectId
from datetime import datetime
from fhe_studio_config import mongo_db_instance

MAX_FETCH_LIMIT=1024

# init
circuits = mongo_db_instance()["circuits"]
keys = mongo_db_instance()["keys"]

def persist_ciruit(id, c):
    c['created_time'] = datetime.utcnow()
    c['deleted'] = False    
    if id is None:
        id_ = circuits.insert_one(c).inserted_id
        print(f'inserted ciruit with id {id_ }')
    else:
        circuits.update_one({'_id':ObjectId(id)}, 
                           { "$set": c }, False)
        id_ = id
        print(f'updated ciruit with id {id_ }')
    return str(id_)

def delete_circuit(id, sub):
    result = circuits.update_one({'_id':ObjectId(id),"sub": sub }, 
                           { "$set": {
                               "deleted": True,
                               "deleted_at": datetime.utcnow()
                            }}, False)
    if result.matched_count != 1:
        raise Exception("no record found")
    return "{}"

def find_circuit(circuit_id):
    return circuits.find_one(ObjectId(circuit_id))

def find_circuits(subname):
    cond = {"deleted": False}
    if subname != '':
        cond["name"] = {"$regex" : subname}
    return circuits.find(cond).limit(MAX_FETCH_LIMIT)

def find_keys(eval_key_id, sub):
    return keys.find_one({'_id':ObjectId(eval_key_id),"sub": sub })

def persist_key(k):
    k['created_time'] = datetime.utcnow()
    k['deleted'] = False
    id_ = keys.insert_one(k)
    print(f'inserted key with id {id_.inserted_id }')
    return id_.inserted_id

def vault(sub):
    return keys.find({"deleted": False, "sub": sub}).limit(MAX_FETCH_LIMIT)

def client_specs(id, sub):
    r = keys.find_one({"_id": ObjectId(id), "deleted": False, "sub": sub})
    json_str = r['circuit']['client_specs']
    print(json_str)
    return json.loads(json_str)


def delete_vault_item(id, sub):
    result = keys.update_one({'_id':ObjectId(id),"sub": sub }, 
                           { "$set": {
                               "deleted": True,
                               "deleted_at": datetime.utcnow()
                            }}, False)
    if result.matched_count != 1:
        raise Exception("no record found")
    return "{}"