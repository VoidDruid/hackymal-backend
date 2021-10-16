from enum import Enum

from pydantic import BaseModel
from typing import List


### RESOURCES ###


class Resource(str, Enum):
    pass


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
    ANY = 'ANY'
    SMALL = 'SMALL'


class Ship(BaseModel):
    name: str
    traversal_type: Traversal = Traversal.SMALL
    capacity: float  # tons
    speed: float = 22  # km/h
    transfer_speed: float = 30  # tons/hour


big_ship = lambda name: Ship(name=name, traversal_type=Traversal.ANY, capacity=2500, speed=20)  # x8
small_ship = lambda name: Ship(name=name, traversal_type=Traversal.SMALL, capacity=1000, speed=25)  # x8
