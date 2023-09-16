import json
from RestrictedPython import safe_builtins, compile_restricted
from RestrictedPython.PrintCollector import PrintCollector
from concrete.fhe.extensions.tag import tag_context 
from mongo_context import persist_ciruit

_SAFE_MODULES = frozenset(("numpy","concrete"))


def _safe_import(name, *args, **kwargs):
    if name not in _SAFE_MODULES:
        raise Exception(f"Don't you even think about {name!r}")
    return __import__(name, *args, **kwargs)


def execute_user_code(user_code, user_func):
    my_globals = {
        "__builtins__": {
            **safe_builtins,
            "__import__": _safe_import,
        },
        '_print_': PrintCollector,
    }

    try:
        byte_code = compile_restricted(
            user_code, filename="<user_code>", mode="exec")
    except SyntaxError:
        # syntax error in the sandboxed code
        raise

    try:
        exec(byte_code, my_globals)
        return my_globals[user_func]
    except BaseException:
        # runtime error (probably) in the sandboxed code
        raise


def fhe_compile(id, usrData):
    src= f"""from concrete import fhe
{usrData['src']}
compiled_circuit = circuit.compile(inputset)
    """
    # bug in concrete
    tag_context.stack = []

    compiled_circuit = execute_user_code(src, "compiled_circuit")
    server = compiled_circuit.server;
    mlir = server._mlir
    json_config = json.dumps(server._configuration.__dict__)

    serialized_client_specs: str = server.client_specs.serialize().decode('utf-8')

    doc = { 
        "mlir": mlir, 
        "config": json_config, 
        "client_specs": serialized_client_specs
    }
    doc.update(usrData)

    print(doc)
    persist_ciruit(id, doc)
    

    return str("compiled_circuit")