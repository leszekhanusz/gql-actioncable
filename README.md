# gql-actioncable

This is a [graphql-python/gql](https://github.com/graphql-python/gql) transport
for the ActionCable websockets protocol.

## Installation

You can install the transport with:

    pip install gqlactioncable

## Usage

Here is an example using the sorare.com GraphQL websockets backend:

```python
import asyncio

from gql import Client, gql

from gqlactioncable import ActionCableWebsocketsTransport


async def main():

    transport = ActionCableWebsocketsTransport(
        url="wss://ws.sorare.com/cable",
    )

    async with Client(transport=transport) as session:

        subscription = gql(
            """
            subscription onAnyCardUpdated {
              aCardWasUpdated {
                slug
              }
            }
        """
        )

        async for result in session.subscribe(subscription):
            print(result)


asyncio.run(main())
```

## License

[MIT License](https://github.com/graphql-python/gql/blob/master/LICENSE)
