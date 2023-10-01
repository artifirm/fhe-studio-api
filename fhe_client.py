from concrete import fhe 
from mongo_context import find_circuit, persist_key, find_keys
import base64
from fhe_studio_config import eval_keys_path

def gen_client(client_specs, seed: int = 111):
    client = fhe.Client(client_specs)
    client.keys.generate(seed = seed)
    return client

def client_key_gen(circuit_id, sub):
    c = find_circuit(circuit_id)
    
    if c['polynomial_size'] > 248:
        raise Exception('polynomial_size needs to be less then 2048')
    
    client_specs = fhe.ClientSpecs.deserialize(c['client_specs'].encode('utf-8'))
    client = gen_client(client_specs)

    serialized_evaluation_keys = client.evaluation_keys.serialize()
    #print(f'serialized_evaluation_keys: {serialized_evaluation_keys}')
    key_id = persist_key({ "circuit": c,
                  "sub": sub,
#                  "evaluation_keys": serialized_evaluation_keys
                    })
    f = open(f"{eval_keys_path()}/{key_id}.eval", "wb")
    f.write(serialized_evaluation_keys)
    f.close()


def encrypt(key_id: str, values: [str]):
    k = find_keys(key_id)
    client_specs = fhe.ClientSpecs.deserialize(k['circuit']['client_specs'].encode('utf-8'))

    client = gen_client(client_specs)
    int_values = list(map(lambda a: int(a), values))
    args = client.encrypt(*int_values)
    
    try:
        iter(args)
    except TypeError as te:
        args = [args]

    encoded = []
    for arg in args:
        serialized_arg: bytes = arg.serialize()
        encoded.append(base64.b64encode(serialized_arg).decode("ascii"))
    return encoded;

def decrypt(key_id, valueB64):
    k = find_keys(key_id)
    client_specs = fhe.ClientSpecs.deserialize(k['circuit']['client_specs'].encode('utf-8'))

    client = gen_client(client_specs)

    value: fhe.Value = fhe.Value.deserialize(base64.b64decode(valueB64))
    decrypted_value = client.decrypt(value)
    return [decrypted_value]

