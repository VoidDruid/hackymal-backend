import logging
import time

from database import SyncSession


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60  # 1 minute
wait_seconds = 1


def check_db_connection() -> None:
    current_error = None
    for _ in range(max_tries):
        try:
            pg = SyncSession()
            pg.execute("SELECT 1")
            break
        except Exception as e:
            logger.error(e)
            current_error = e
        time.sleep(wait_seconds)
    else:
        raise current_error


if __name__ == "__main__":
    check_db_connection()
    print("Pre start checks passed")
