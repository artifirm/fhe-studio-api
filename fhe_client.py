from concrete import fhe 
from mongo_context import find_circuit, persist_key, find_keys
import base64

def gen_client(client_specs, seed: int = 111):
    client = fhe.Client(client_specs)
    client.keys.generate(seed = seed)
    return client

def client_key_gen(circuit_id, sub):
    client_specs = fhe.ClientSpecs.deserialize(c['client_specs'].encode('utf-8'))
    client = gen_client(client_specs)

    serialized_evaluation_keys = client.evaluation_keys.serialize()
    print(f'serialized_evaluation_keys: {serialized_evaluation_keys}')


    persist_key({ "circuit": c,
                  "sub": sub,
                  "evaluation_keys": serialized_evaluation_keys
    })

def encrypt(key_id, value):
    k = find_keys(key_id)
    client_specs = fhe.ClientSpecs.deserialize(k['circuit']['client_specs'].encode('utf-8'))

    client = gen_client(client_specs)

    arg: fhe.Value = client.encrypt(value)
    serialized_arg: bytes = arg.serialize()
    return base64.b64encode(serialized_arg).decode("ascii")

def decrypt(key_id, valueB64):
    k = find_keys(key_id)
    client_specs = fhe.ClientSpecs.deserialize(k['circuit']['client_specs'].encode('utf-8'))

    client = gen_client(client_specs)

    value: fhe.Value = fhe.Value.deserialize(base64.b64decode(valueB64))
    decrypted_value = client.decrypt(value)
    return [decrypted_value]

