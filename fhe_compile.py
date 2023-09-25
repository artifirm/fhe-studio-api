import json
from RestrictedPython import safe_builtins, compile_restricted
from RestrictedPython.PrintCollector import PrintCollector
from concrete.fhe.extensions.tag import tag_context 
from mongo_context import persist_ciruit
from multiprocessing import Process, Manager
from concrete import fhe

_SAFE_MODULES = frozenset(("numpy","concrete"))


def _safe_import(name, *args, **kwargs):
    if name not in _SAFE_MODULES:
        raise Exception(f"Don't you even think about {name!r}")
    return __import__(name, *args, **kwargs)


def execute_user_code_local(user_code, user_func, return_dict):
    my_globals = {
        "__builtins__": {
            **safe_builtins,
            "__import__": _safe_import,
            "_getitem_": fhe.LookupTable.__getitem__,
        },
        '_print_': PrintCollector,
    }

    try:
        byte_code = compile_restricted(
            user_code, filename="<user_code>", mode="exec")
        exec(byte_code, my_globals)
        server = my_globals[user_func].server;

        return_dict['value'] = { 
            "mlir": server._mlir, 
            "config": json.dumps(server._configuration.__dict__), 
            "client_specs": server.client_specs.serialize().decode('utf-8')
        }

    except Exception as e:
        err_str = str(e)
        print (err_str)
        return_dict['value'] = {'exception': err_str }


def execute_user_code(user_code, user_func, time_out_sec = 10):
    manager = Manager()
    return_dict = manager.dict()

    p = Process(target=execute_user_code_local, args=(user_code, user_func, return_dict), 
                kwargs={})
    p.start()
    p.join(time_out_sec)  # sec
    if p.is_alive():
        p.terminate()
        raise Exception(f"Exceeded execution limit")
    print('return_dict:', return_dict)
    return return_dict['value']

def fhe_compile(id, usrData):
    src= f"""from concrete import fhe
{usrData['src']}
compiled_circuit = circuit.compile(inputset)
    """
    # bug in concrete
    tag_context.stack = []

    print(src)
    doc = execute_user_code(src, "compiled_circuit")
    if 'exception' in doc:
        return doc['exception']
    
    new_doc = { **doc, **usrData }

    print(new_doc)
    persist_ciruit(id, new_doc)
    
    return None