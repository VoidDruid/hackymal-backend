from enum import Enum
from typing import List

from pydantic import BaseModel


### RESOURCES ###


class Resource(str, Enum):
    DT_A_TU = 'ДТ "А" ТУ'
    DT_Z = 'ДТ "З" ГОСТ'
    DT_A = 'ДТ "А" ГОСТ'
    DT_L = 'ДТ "Л" ГОСТ'
    AI_92 = "АИ-92-К5"


class ResourceCount(BaseModel):
    type: Resource
    amount: float  # tons


### PRODUCER - CONSUMER ###


class Location(BaseModel):
    name: str


class Consumer(Location):
    demand: List[ResourceCount]


class Producer(Location):
    supply: List[ResourceCount]


### SHIPS ###


class Traversal(str, Enum):
    ANY = "ANY"
    SMALL = "SMALL"


class Ship(BaseModel):
    name: str
    traversal_type: Traversal = Traversal.SMALL
    capacity: int  # tons
    cargo: int
    speed: float = 22  # km/h
    transfer_speed: float = 30  # tons/hour


big_ship = lambda name: Ship(
    name=name, traversal_type=Traversal.ANY, capacity=2500, cargo=2500, speed=20
)  # x8
small_ship = lambda name: Ship(
    name=name, traversal_type=Traversal.SMALL, capacity=1000, cargo=0, speed=25
)  # x8


class Action(str, Enum):
    UNLOAD = "unload"
    WAIT = "wait"
    LOAD = "load"


class Order(BaseModel):
    location: str
    action: Action
    time: int  # hour from the start of calculation
