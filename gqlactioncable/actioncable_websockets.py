from ssl import SSLContext

from gql.transport.common.adapters.websockets import WebSocketsAdapter
from typing import Any, Dict, Optional, Union
from websockets.datastructures import HeadersLike

from .actioncable_protocol import ActionCableProtocolTransportBase


class ActionCableWebsocketsTransport(ActionCableProtocolTransportBase):
    """:ref:`Async Transport <async_transports>` used to execute GraphQL queries on
    remote servers with websocket connection.

    This transport uses asyncio and the websockets library in order to send requests
    on a websocket connection.
    """

    def __init__(
        self,
        url: str,
        *,
        headers: Optional[HeadersLike] = None,
        ssl: Union[SSLContext, bool] = False,
        connect_timeout: Optional[Union[int, float]] = 10,
        keep_alive_timeout: Optional[Union[int, float]] = None,
        connect_args: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the transport with the given parameters.

        :param url: The GraphQL server URL. Example: 'wss://server.com:PORT/graphql'.
        :param headers: Dict of HTTP Headers.
        :param ssl: ssl_context of the connection. Use ssl=False to disable encryption
        :param connect_timeout: Timeout in seconds for the establishment
            of the websocket connection. If None is provided this will wait forever.
        :param keep_alive_timeout: Optional Timeout in seconds to receive
            a sign of liveness from the server.
        :param connect_args: Other parameters forwarded to
            `websockets.connect <https://websockets.readthedocs.io/en/stable/reference/\
            client.html#opening-a-connection>`_
        """

        # Instanciate a WebSocketAdapter to indicate the use
        # of the websockets dependency for this transport
        self.adapter: WebSocketsAdapter = WebSocketsAdapter(
            url=url,
            headers=headers,
            ssl=ssl,
            connect_args=connect_args,
        )

        # Initialize the ActionCableProtocolTransportBase parent class
        super().__init__(
            adapter=self.adapter,
            connect_timeout=connect_timeout,
            keep_alive_timeout=keep_alive_timeout,
        )

    @property
    def headers(self) -> Optional[HeadersLike]:
        return self.adapter.headers

    @property
    def ssl(self) -> Union[SSLContext, bool]:
        return self.adapter.ssl
