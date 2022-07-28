import json
import logging
from ssl import SSLContext
from typing import Any, Dict, Optional, Tuple, Union, cast

from gql.transport.exceptions import TransportProtocolError
from gql.transport.websockets_base import WebsocketsTransportBase
from graphql import DocumentNode, ExecutionResult, print_ast
from websockets.datastructures import HeadersLike
from websockets.typing import Subprotocol

log = logging.getLogger(__name__)


class ActionCableWebsocketsTransport(WebsocketsTransportBase):
    """gql transport used to execute GraphQL queries on
    servers with a websocket connection implementing the ActionCable protocol.

    This transport uses asyncio and the websockets library in order to send
    requests on a websocket connection.
    """

    def __init__(
        self,
        url: str,
        headers: Optional[HeadersLike] = None,
        ssl: Union[SSLContext, bool] = False,
        connect_timeout: Optional[Union[int, float]] = 10,
        keep_alive_timeout: Optional[Union[int, float]] = None,
        connect_args: Dict[str, Any] = {},
    ) -> None:
        """Initialize the transport with the given parameters.

        :param url: The GraphQL server URL: Example: "wss://ws.sorare.com/cable"
        :param headers: Dict of HTTP Headers.
        :param ssl: ssl_context of the connection. Use ssl=False to disable encryption
        :param connect_timeout: Timeout in seconds for the establishment
            of the websocket connection. If None is provided this will wait forever.
        :param keep_alive_timeout: Optional Timeout in seconds to receive
            a sign of liveness from the server.
        :param connect_args: Other parameters forwarded to websockets.connect
        """

        init_payload: Dict[str, Any] = {}
        close_timeout = None
        ack_timeout = None

        super().__init__(
            url,
            headers,
            ssl,
            init_payload,
            connect_timeout,
            close_timeout,
            ack_timeout,
            keep_alive_timeout,
            connect_args,
        )

        self.supported_subprotocols = [
            cast(Subprotocol, "actioncable-v1-json"),
        ]

    async def _send_query(
        self,
        document: DocumentNode,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> int:
        """Send a query to the provided websocket connection.

        We use an incremented id to reference the query.

        Returns the used id for this query.
        """

        query_id = self.next_query_id

        identifier = json.dumps(
            {
                "channel": "GraphqlChannel",
                "id": str(self.next_query_id),
            }
        )

        self.next_query_id += 1

        subscribe_command = json.dumps(
            {
                "command": "subscribe",
                "identifier": identifier,
            }
        )

        await self._send(subscribe_command)

        payload: Dict[str, Any] = {
            "query": print_ast(document),
            "action": "execute",
        }

        if variable_values:
            payload["variables"] = variable_values

        if operation_name:
            payload["operationName"] = operation_name

        message_command = json.dumps(
            {
                "command": "message",
                "identifier": identifier,
                "data": json.dumps(payload),
            }
        )

        await self._send(message_command)

        return query_id

    def _parse_answer_actioncable(
        self, json_answer: Dict[str, Any]
    ) -> Tuple[str, Optional[int], Optional[ExecutionResult]]:
        """
        Returns a list consisting of:
            - the answer_type:
              ('data', 'complete', 'welcome', 'ping', 'confirm_subscription')
            - the answer id (Integer) if received or None
            - an execution Result if the answer_type is 'data' or None
        """

        answer_type: str = ""
        answer_id: Optional[int] = None
        execution_result: Optional[ExecutionResult] = None

        try:

            answer_type = str(json_answer.get("type"))

            if answer_type == "confirm_subscription":
                pass

            elif answer_type == "welcome":
                pass

            elif answer_type == "ping":
                pass

            else:
                message = json_answer.get("message")

                if message is None:
                    raise ValueError

                identifier_serialized = json_answer.get("identifier")

                if identifier_serialized is None:
                    raise ValueError

                identifier = json.loads(identifier_serialized)

                answer_id = int(identifier.get("id"))
                answer_type = "data"

                result = message.get("result")
                data = result.get("data")
                errors = result.get("errors")

                if data or errors:

                    execution_result = ExecutionResult(
                        errors=errors,
                        data=data,
                        extensions=None,
                    )

            if self.check_keep_alive_task is not None:
                self._next_keep_alive_message.set()

        except ValueError as e:
            raise TransportProtocolError(
                f"Server did not return a GraphQL result: {json_answer}"
            ) from e

        return answer_type, answer_id, execution_result

    def _parse_answer(
        self, answer: str
    ) -> Tuple[str, Optional[int], Optional[ExecutionResult]]:
        try:
            json_answer = json.loads(answer)
        except ValueError:
            raise TransportProtocolError(
                f"Server did not return a GraphQL result: {answer}"
            )

        return self._parse_answer_actioncable(json_answer)

    async def _after_connect(self):

        response_headers = self.websocket.response_headers
        self.subprotocol = response_headers.get("Sec-WebSocket-Protocol")
        log.debug(f"backend subprotocol returned: {self.subprotocol!r}")
