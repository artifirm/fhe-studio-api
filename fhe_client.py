from concrete import fhe 
from mongo_context import find_circuit, persist_key, find_keys
import base64
from fhe_studio_config import eval_keys_path
import logging
import os

MAX_COMPLEXITY = int(os.environ.get("MAX_COMPLEXITY", "0"))

def gen_client(client_specs, seed: int = 111):
    client = fhe.Client(client_specs)
    client.keys.generate(seed = seed)
    return client

def client_key_gen(circuit_id, sub):
    c = find_circuit(circuit_id)
    
    logging.debug(f"polynomial_size: {c['polynomial_size']}, complexity: {c.get('complexity',0)}")
    if MAX_COMPLEXITY > 0 and c['complexity'] > MAX_COMPLEXITY:
         raise Exception(f'complexity needs to be less then {MAX_COMPLEXITY}. You can run a fhe-studio docker container locally for bigger circuits')
    
    client_specs = fhe.ClientSpecs.deserialize(c['client_specs'].encode('utf-8'))
    client = gen_client(client_specs)

    serialized_evaluation_keys = client.evaluation_keys.serialize()
    #print(f'serialized_evaluation_keys: {serialized_evaluation_keys}')
    key_id = persist_key({ "circuit": c,
                  "sub": sub,
#                  "evaluation_keys": serialized_evaluation_keys
                    })
    # todo: rethink the vault workflow
    # f = open(f"{eval_keys_path()}/{key_id}.eval", "wb")
    # f.write(serialized_evaluation_keys)
    # f.close()


def encrypt(client_specs_b64: str, values: [str], key_id):
    #k = find_keys(key_id, sub)
    #client_specs = fhe.ClientSpecs.deserialize(k['circuit']['client_specs'].encode('utf-8'))
    client_specs = fhe.ClientSpecs.deserialize(base64.b64decode(client_specs_b64))

    client = gen_client(client_specs)
    # todo: rethink the vault workflow
    if not os.path.isfile(f"{eval_keys_path()}/{key_id}.eval"):
        serialized_evaluation_keys = client.evaluation_keys.serialize()
        f = open(f"{eval_keys_path()}/{key_id}.eval", "wb")
        f.write(serialized_evaluation_keys)
        f.close()

    int_values = values
    #print(f'int_values to :::::::::::: ${int_values}')
    args = client.encrypt(*int_values)
    
    try:
        iter(args)
    except TypeError as te:
        args = [args]

    encoded = []
    for arg in args:
        serialized_arg: bytes = arg.serialize()
        encoded.append(base64.b64encode(serialized_arg).decode("ascii"))
    return encoded

def decrypt(client_specs_b64: dict, valueB64):
    #k = find_keys(key_id, sub)
    client_specs = fhe.ClientSpecs.deserialize(base64.b64decode(client_specs_b64))
    #client_specs = fhe.ClientSpecs.deserialize(k['circuit']['client_specs'].encode('utf-8'))

    client = gen_client(client_specs)

    value: fhe.Value = fhe.Value.deserialize(base64.b64decode(valueB64))
    decrypted_value = client.decrypt(value)
    return [decrypted_value]

