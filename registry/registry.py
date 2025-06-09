from datetime import datetime, timedelta
import uuid
from resources import *
from utils import *
from fastapi import FastAPI, Query, HTTPException, Body

app = FastAPI()

nodes = []
tokens = {}
ttl = get_config_value('token_ttl_minutes')


@app.post("/nodes")
async def post_nodes(new_node: Node):
    log(f'Registry: received post @ nodes with new node: {new_node.to_dict()}')
    if not new_node.check_sanity():
        raise HTTPException(status_code=400, detail="Provided addr or type is not valid")

    token = str(uuid.uuid4())
    tokens[token] = datetime.now()

    _hash = new_node.get_hash()
    new_node.token = token
    found = False

    for node in nodes:
        if node.hash == _hash:
            tokens.pop(node.token)
            node.token = token
            found = True
            break

    if not found:
        nodes.append(new_node)

    return {
        "token": token
    }


@app.post("/tokens")
async def post_tokens(token: str = Body(..., embed=True)):
    log(f'Registry: received post @ tokens with token {token}')
    for tkn, datetm in tokens.items():
        if tkn == token and datetm + timedelta(minutes=ttl) > datetime.now():
            return {
                "message": "valid"
            }

    return {
        "message": "invalid"
    }

@app.get("/nodes")
async def get_nodes(type: str = Query(default='all')):
    log(f'Registry: received get @ nodes with type: {type}')
    if re.match('front|back|all', type) is None:
        raise HTTPException(status_code=400, detail="Specified node type is invalid")

    lst = []
    try:
        for node in nodes:
            if (type == 'all' or node.type == type) and tokens[node.token] +  timedelta(minutes=ttl) > datetime.now():
                lst.append(node.to_dict())
    except KeyError:
        log('Registry: get_nodes() token not found in tokens')

    tokens_to_pop = []
    for token, time in tokens.items():
        if time +  timedelta(minutes=ttl) <= datetime.now():
            tokens_to_pop.append(token)

    for token in tokens_to_pop:
        del tokens[token]

    return {
        "nodes": lst,
        "collection": type
    }

@app.delete("/nodes/{token}")
async def delete_node(token: str):
    log(f'Registry: received delete @ nodes with token: {token}')
    node_idx = None
    for idx, node in enumerate(nodes):
        if node.token == token:
            node_idx = idx
            break

    if node_idx is not None:
        del tokens[token]
        del nodes[node_idx]
        return {  }
    else:
        log(f'Registry: failed to delete node')

    raise HTTPException(status_code=400, detail="No node matches specified token")


if __name__ == "__main__":
    import uvicorn
    addr = get_my_ip()
    port = get_config_value('registry_port')
    put_value_in_config('registry_addr', addr)
    log(f'Registry: running at addr: {addr} port: {port} ttl: {ttl}')
    uvicorn.run(app, host=addr, port=port)