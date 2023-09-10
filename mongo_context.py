import pymongo
from bson.objectid import ObjectId

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydatabase"]
ciruits = mydb["ciruits"]
keys = mydb["keys"]

def persist_ciruit(c):
    id_ = ciruits.insert_one(c)
    print(f'inserted ciruit with id {id_.inserted_id }')

def find_circuit(circuit_id):
    return ciruits.find_one(ObjectId(circuit_id))

def find_keys(eval_key_id):
    return keys.find_one(ObjectId(eval_key_id))

def persist_key(k):
    id_ = keys.insert_one(k)
    print(f'inserted key with id {id_.inserted_id }')
    return "OK"