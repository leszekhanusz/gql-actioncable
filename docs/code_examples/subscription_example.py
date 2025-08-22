import asyncio
import logging  # noqa: F401
from gql import Client, gql

from gqlactioncable import ActionCableWebsocketsTransport

logging.basicConfig(level=logging.DEBUG)


async def main():

    transport = ActionCableWebsocketsTransport(
        url="wss://ws.sorare.com/cable",
        keep_alive_timeout=60,
    )

    async with Client(transport=transport) as session:

        subscription = gql(
            """
            subscription onAnyCardUpdated {
              anyCardWasUpdated {
                card {
                  name
                  grade
                }
              }
            }
        """
        )

        nb_results = 0

        async for result in session.subscribe(subscription):
            print(result["anyCardWasUpdated"])
            nb_results += 1

            if nb_results >= 5:
                break


asyncio.run(main())
