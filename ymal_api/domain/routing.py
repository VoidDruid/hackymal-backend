import asyncio
import base64
from functools import lru_cache

import aioredis
import networkx as nx
import numpy as np
import struct
from neo4j import Transaction
from typing import Tuple

from dataplane import neo4j

from .consts import GRAPH_CACHE_KEY, GRAPH_TTL, GRAPH_MATRIX_CACHE_KEY


async def get_demands():
    pass


async def get_supply():
    pass


async def get_fleet():
    pass


@lru_cache(maxsize=2)
def nodes_list(G):
    return sorted(list(G.nodes))


@lru_cache(maxsize=128)
def node_to_index(G, node_name):
    nodes = nodes_list(G)
    return nodes.index(node_name)


@lru_cache(maxsize=128)
def index_to_node(G, ind):
    nodes = nodes_list(G)
    return nodes[ind]


def ndarray_pack(array):
    h, w = array.shape
    shape = struct.pack('>II', h, w)
    return shape + array.tobytes()


def ndarray_unpack(encoded):
    h, w = struct.unpack('>II', encoded[:8])
    return np.frombuffer(encoded[8:]).reshape(h,w)


async def invalidate_graph(redis: aioredis.Redis):
    await redis.delete(GRAPH_CACHE_KEY, GRAPH_MATRIX_CACHE_KEY)


async def get_graph(redis: aioredis.Redis) -> Tuple[nx.Graph, np.ndarray]:
    b64_dump, matrix_dump = await asyncio.gather(redis.get(GRAPH_CACHE_KEY), redis.get(GRAPH_MATRIX_CACHE_KEY))
    if b64_dump is not None and b64_dump != "":
        await asyncio.gather(
            redis.expire(GRAPH_CACHE_KEY, GRAPH_TTL),
            redis.expire(GRAPH_MATRIX_CACHE_KEY, GRAPH_TTL)
        )
        graph_dump = base64.b64decode(b64_dump).decode('utf-8')
        return nx.parse_graphml(graph_dump), ndarray_unpack(matrix_dump)

    def q(tx: Transaction):
        query = """
        MATCH (n)-[r]->(c)
        RETURN n, r, c
        """
        result = tx.run(query)
        return result.graph()

    result = await neo4j(q)
    G = nx.Graph()

    nodes = list(result._nodes.values())
    for node in nodes:
        G.add_node(node["name"], label=list(node.labels)[0], **dict(node))

    rels = list(result._relationships.values())

    for rel in rels:
        G.add_edge(
            rel.start_node["name"],
            rel.end_node["name"],
            key=rel.id,
            type=rel.type,
            **dict(rel),
        )

    matrix = np.zeros((len(G.nodes), len(G.nodes)), dtype=np.float64)

    for node_name in G.nodes:
        distances = nx.shortest_path_length(G, node_name, weight='weight')
        print(distances)
        for target_name, dist in distances.items():
            index_j = node_to_index(G, target_name)
            matrix[node_to_index(G, node_name)][index_j] = dist

    matrix_dump = ndarray_pack(matrix)

    linefeed = chr(10)
    graph_dump = linefeed.join(nx.generate_graphml(G))
    b64_dump = base64.b64encode(graph_dump.encode('utf-8'))

    await asyncio.gather(
        redis.set(GRAPH_CACHE_KEY, b64_dump, ex=GRAPH_TTL),
        redis.set(GRAPH_MATRIX_CACHE_KEY, matrix_dump, ex=GRAPH_TTL)
    )

    return G, matrix


async def calculate_paths(redis):
    G, matrix = await get_graph(redis)

    nodes = nodes_list(G)

    return None
