import asyncio
from typing import Any, Callable

from mypy_extensions import KwArg, VarArg
from neo4j import GraphDatabase, Transaction

from settings import neo4j_settings


class AsyncNeo4j:
    _driver = None

    @classmethod
    def get_driver(cls):
        if cls._driver is None:
            cls._driver = GraphDatabase.driver(
                neo4j_settings.url,
                auth=(neo4j_settings.user, neo4j_settings.password),
            )
        return cls._driver

    @property
    def driver(self):
        return self.get_driver()

    async def __call__(
        self,
        statement: Callable[[Transaction, VarArg(Any), KwArg(Any)], Any],
        *args,
        **kwargs
    ):
        def run():
            with self.driver.session() as session:
                result = session.write_transaction(statement, *args, **kwargs)
            return result

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, run)

    def run_sync(
        self,
        statement: Callable[[Transaction, VarArg(Any), KwArg(Any)], Any],
        *args,
        **kwargs
    ):
        with self.driver.session() as session:
            return session.write_transaction(statement, *args, **kwargs)


neo4j = AsyncNeo4j()
