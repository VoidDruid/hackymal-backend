import asyncio
import base64
import math
import random
import struct
from collections import defaultdict
from functools import lru_cache
from typing import Tuple, Type

import aioredis
import networkx as nx
import numpy as np
import vrpy
from neo4j import Transaction

from dataplane import neo4j

from .consts import GRAPH_CACHE_KEY, GRAPH_MATRIX_CACHE_KEY, GRAPH_TTL
from .schemas import Resource, Order, big_ship, small_ship, Action


START = "Обь-Лопхари"
END = "Обь-Се-Яха"


class GraphSpec:
    name: str

    @staticmethod
    def q(tx: Transaction):
        pass


async def get_demands():
    towns = [
        "Азовы",
        "Аксарка",
        "Антипаюта",
        "Белоярск",
        "Восяхово",
        "Горки",
        "Зеленый Яр",
        "Катравож",
        "Кутопьюган",
        "Лабытнанги",
        "Лопхари",
        "Мужи",
        "Мыс Каменный",
        "Находка",
        "Новый Порт",
        "Нори",
        "Ныда",
        "Обь-Антипаюта",
        "Обь-Белоярск",
        "Обь-Белоярск 2",
        "Обь-Восяхово",
        "Обь-Катравож",
        "Обь-Кутопьюган",
        "Обь-Лопхари",
        "Обь-Мужи",
        "Обь-Ныда",
        "Обь-Питляр",
        "Обь-Се-Яха",
        "Обь-Яр-Сале",
        "Обь-Яр-Сале-2",
        "Овгорт",
        "Панаевск",
        "Питляр",
        "Салемал",
        "Салехард",
        "Самбург",
        "Се-Яха",
        "Харсайм",
        "Шурышкары",
        "Щучье",
        "Яр-Сале",
    ]
    low_end = 25
    high_end = 600
    k = 3
    demand = {}
    for town in towns:
        town_demand = {}
        for _ in range(random.randint(0, 2)):
            resource = random.choice(list(Resource))
            amount = int(
                math.floor(
                    low_end
                    + (high_end - low_end + 1) * (1.0 - random.random() ** (1.0 / k))
                )
            )
            town_demand[resource] = amount
        demand[town] = town_demand
    return demand


async def get_fleet():
    names = [
        "Пойма",
        "СТГН-12",
        "СТГН-14",
        "Наливная-2406",
        "Скала-3",
        "Заструга-1",
        "Шуга",
        "Пойма-2",
        "НС-1005",
        "Старица-2",
        "ГНБ-209",
        "Скала",
        "ГНБ-210",
        "Протока",
        "Дунай",
        "Алдан",
    ]
    i = -1

    def next_name():
        nonlocal i
        i += 1
        return names[i]

    return [big_ship(next_name()) for _ in range(6)], [small_ship(next_name()) for _ in range(10)]


async def get_supply():
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
    shape = struct.pack(">II", h, w)
    return shape + array.tobytes()


def ndarray_unpack(encoded):
    h, w = struct.unpack(">II", encoded[:8])
    return np.frombuffer(encoded[8:]).reshape(h, w)


def g_cache_key(name: str):
    return GRAPH_CACHE_KEY + "_" + name


def m_cache_key(name: str):
    return GRAPH_MATRIX_CACHE_KEY + "_" + name


async def invalidate_graph(redis: aioredis.Redis, graph_spec: Type[GraphSpec]):
    await redis.delete(g_cache_key(graph_spec.name), m_cache_key(graph_spec.name))


def build_matrix(G):
    matrix = np.zeros((len(G.nodes), len(G.nodes)), dtype=np.float64)

    for node_name in G.nodes:
        distances = nx.shortest_path_length(G, node_name, weight="weight")
        for target_name, dist in distances.items():
            index_j = node_to_index(G, target_name)
            matrix[node_to_index(G, node_name)][index_j] = dist

    return matrix


async def get_graph(
    redis: aioredis.Redis, graph_spec: Type[GraphSpec]
) -> Tuple[nx.Graph, np.ndarray]:
    b64_dump, matrix_dump = await asyncio.gather(
        redis.get(g_cache_key(graph_spec.name)), redis.get(m_cache_key(graph_spec.name))
    )
    if b64_dump is not None and b64_dump != "":
        if matrix_dump is None or matrix_dump == "":
            await invalidate_graph(redis, graph_spec)
        else:
            await asyncio.gather(
                redis.expire(g_cache_key(graph_spec.name), GRAPH_TTL),
                redis.expire(m_cache_key(graph_spec.name), GRAPH_TTL),
            )
            graph_dump = base64.b64decode(b64_dump).decode("utf-8")
            return nx.parse_graphml(graph_dump), ndarray_unpack(matrix_dump)

    result = await neo4j(graph_spec.q)
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

    matrix = build_matrix(G)
    matrix_dump = ndarray_pack(matrix)

    linefeed = chr(10)
    graph_dump = linefeed.join(nx.generate_graphml(G))
    b64_dump = base64.b64encode(graph_dump.encode("utf-8"))

    await asyncio.gather(
        redis.set(g_cache_key(graph_spec.name), b64_dump, ex=GRAPH_TTL),
        redis.set(m_cache_key(graph_spec.name), matrix_dump, ex=GRAPH_TTL),
    )

    return G, matrix


class FullGraph(GraphSpec):
    name = "full"

    @staticmethod
    def q(tx: Transaction):
        query = """
        MATCH (n)-[r]->(c)
        RETURN n, r, c
        """
        result = tx.run(query)
        return result.graph()


class AnyTraversalGraph(GraphSpec):
    name = "any-traversal"

    @staticmethod
    def q(tx: Transaction):
        query = """
        MATCH (n)-[r:Path{traversal:"any"}]-(c)
        RETURN n, r, c
        """
        result = tx.run(query)
        return result.graph()


class SmallTraversalGraph(GraphSpec):
    name = "small-traversal"

    @staticmethod
    def q(tx: Transaction):
        query = """
        MATCH (n)-[r:Path{traversal:"small"}]-(c)
        RETURN n, r, c
        """
        result = tx.run(query)
        return result.graph()


async def calculate_paths(redis):
    await asyncio.gather(
        invalidate_graph(redis, FullGraph),
        invalidate_graph(redis, AnyTraversalGraph),
        invalidate_graph(redis, SmallTraversalGraph),
    )

    demands = await get_demands()
    big_fleet, small_fleet = await get_fleet()

    full_g, full_matrix = await get_graph(redis, FullGraph)
    for node in full_g.nodes:
        demand = sum(demands.get(node, {'_': 0}).values())
        full_g.nodes[node]['demand'] = demand

    any_g, any_matrix = await get_graph(redis, AnyTraversalGraph)

    spine = nx.shortest_path(any_g, START, END, weight="weight")
    spine_g = any_g.copy()
    spine_g.remove_nodes_from(set(any_g.nodes) - set(spine))

    spine_data = {}
    for ind in range(len(spine)):
        source = spine[ind]
        full_g_copy = full_g.copy()
        full_g_copy.remove_nodes_from([*spine[:ind], *spine[ind + 1 :]])

        node_set = set(nx.dfs_preorder_nodes(full_g_copy, source=source))
        if len(node_set) == 1:
            region_demand = sum(demands[source].values())
            region_traversal_length = 0
        else:
            node_set.add(source)
            path = nx.approximation.traveling_salesman_problem(
                full_g_copy, weight="weight", nodes=node_set, cycle=False
            )

            region_demand = 0  # TODO
            region_traversal_length = 0

            prev = path[0]
            for cur in path[1:]:
                edge = full_g_copy[prev][cur]
                region_traversal_length += edge["weight"]
                region_demand += sum(demands[cur].values())
                prev = cur

        spine_data[source] = {
            "demand": region_demand,
            "traversal": region_traversal_length,
        }

    for spine_node, attrs in spine_data.items():
        for key, value in attrs.items():
            spine_g.nodes[spine_node][key] = value

    topology = list(nx.dfs_preorder_nodes(spine_g, START))
    if START == topology[-1]:
        topology = topology[::-1]

    traversal_nodes = set(
        node for node in spine_g.nodes if spine_g.nodes[node]["traversal"] != 0
    )
    point_nodes = set(spine_g.nodes) - traversal_nodes

    spine_dig = nx.DiGraph()

    SYMBOLS = (
        "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
        "abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA",
    )
    tr = {ord(a): ord(b) for a, b in zip(*SYMBOLS)}
    def _graph_name(name: str):
        return name.translate(tr).replace("-", "").replace(" ", "").replace('_', '')

    def add_edges(topo, prev):
        nonlocal spine_dig

        for cur in topo:
            if prev == 'Source' or cur == 'Sink' or cur == 'Source' or prev == 'Sink':
                cost = 0
            else:
                cost = spine_g[prev][cur]['weight']

            if cur != 'Source' and prev != 'Sink':
                spine_dig.add_edge(_graph_name(prev), _graph_name(cur), cost=cost)
            if cur not in ('Source', 'Sink'):
                spine_dig.nodes[_graph_name(cur)]['demand'] = spine_g.nodes[cur]['demand']
                spine_dig.nodes[_graph_name(cur)]['name'] = cur

            prev = cur

    add_edges((*topology, 'Sink'), 'Source')
    add_edges(['Source', *topology][::-1], 'Sink')

    cvrp_problem = vrpy.VehicleRoutingProblem(
        spine_dig,
        load_capacity=big_fleet[0].capacity,
        num_vehicles=len(big_fleet),
        use_all_vehicles=True,
    )
    cvrp_problem.solve(
        heuristic_only=True,
        time_limit=30
    )
    routes = cvrp_problem.best_routes

    longest_route = max([len(v) for v in routes.values()])
    for route in routes.values():
        len_route = len(route)
        if len_route >= longest_route:
            continue
        route.extend([None] * (longest_route - len_route))

    destinations_lists = list(zip(*routes.values()))[1:]

    max_unloading = 0
    for destinations in destinations_lists:
        unloading = 0
        for destination in destinations:
            if destination in ('Sink', 'Source', None):
                continue
            name = spine_dig.nodes[destination]['name']
            if spine_g.nodes[name]['traversal'] != 0:
                unloading += 1

        if unloading > max_unloading:
            max_unloading = unloading

    small_per_sector = len(small_fleet) // max_unloading

    def solve_sector(node_name):
        ind = spine.index(node_name)
        sector_dig = nx.DiGraph()
        sector_g = full_g.copy()
        sector_g.remove_nodes_from([*spine[:ind], *spine[ind + 1:]])

        print(_graph_name(node_name), 'Sink')
        sector_dig.add_edge(_graph_name(node_name), 'Sink', cost=0)
        sector_dig.add_edge('Source', _graph_name(node_name), cost=0)
        sector_dig.nodes[_graph_name(node_name)]['name'] = node_name

        for edge in nx.dfs_edges(sector_g, node_name):
            sector_dig.add_edge(_graph_name(edge[0]), _graph_name(edge[1]), cost=sector_g[edge[0]][edge[1]]['weight'])
            sector_dig.add_edge(_graph_name(edge[1]), _graph_name(edge[0]), cost=sector_g[edge[0]][edge[1]]['weight'])
            sector_dig.nodes[_graph_name(edge[0])]['demand'] = sector_g.nodes[edge[0]]['demand']
            sector_dig.nodes[_graph_name(edge[1])]['demand'] = sector_g.nodes[edge[1]]['demand']
            sector_dig.nodes[_graph_name(edge[0])]['name'] = edge[0]
            sector_dig.nodes[_graph_name(edge[1])]['name'] = edge[1]


        cvrp_problem = vrpy.VehicleRoutingProblem(
            sector_dig,
            load_capacity=small_fleet[0].capacity,
            num_vehicles=small_per_sector,
            use_all_vehicles=True,
        )
        cvrp_problem.solve(
            heuristic_only=True,
            time_limit=10
        )

        sector_routes = cvrp_problem.best_routes


        
    return solve_sector('Обь-Питляр')
