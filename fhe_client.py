from concrete import fhe 
from mongo_context import find_circuit, persist_key

def client_key_gen(circuit_id, sub):
    c = find_circuit(circuit_id)
    print(c['client_specs'])
    client_specs = fhe.ClientSpecs.deserialize(c['client_specs'])

    client = fhe.Client(client_specs)
    client.keys.generate(seed=111)
    serialized_evaluation_keys = client.evaluation_keys.serialize()
    print(f'serialized_evaluation_keys: {serialized_evaluation_keys}')


    persist_key({ "circuit": c,
                  "sub": sub,
                  "evaluation_keys": serialized_evaluation_keys
    })