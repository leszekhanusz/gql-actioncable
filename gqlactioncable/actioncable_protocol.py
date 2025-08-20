import json
import logging
from gql import GraphQLRequest
from gql.transport.common.adapters.connection import AdapterConnection
from gql.transport.common.base import SubscriptionTransportBase
from gql.transport.exceptions import TransportProtocolError
from graphql import ExecutionResult
from typing import Any, Dict, Optional, Tuple, Union

log = logging.getLogger(__name__)


class ActionCableProtocolTransportBase(SubscriptionTransportBase):
    """gql transport used to execute GraphQL queries on
    servers with a websocket connection implementing the ActionCable protocol.

    This transport uses asyncio and the provided websockets adapter library
    in order to send requests on a websocket connection.
    """

    ACTIONCABLE_SUBPROTOCOL = "actioncable-v1-json"

    def __init__(
        self,
        *,
        adapter: AdapterConnection,
        connect_timeout: Optional[Union[int, float]] = 10,
        keep_alive_timeout: Optional[Union[int, float]] = None,
    ) -> None:
        """Initialize the transport with the given parameters.

        :param adapter: The connection dependency adapter
        :param connect_timeout: Timeout in seconds for the establishment
            of the websocket connection. If None is provided this will wait forever.
        :param keep_alive_timeout: Optional Timeout in seconds to receive
            a sign of liveness from the server.
        """

        # Initialize the generic SubscriptionTransportBase parent class
        super().__init__(
            adapter=adapter,
            connect_timeout=connect_timeout,
            close_timeout=0,
            keep_alive_timeout=keep_alive_timeout,
        )

        adapter.subprotocols = [self.ACTIONCABLE_SUBPROTOCOL]

    async def _send_query(
        self,
        request: GraphQLRequest,
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

        payload: Dict[str, Any] = request.payload
        payload["action"] = "execute"

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

        response_headers = self.response_headers
        self.subprotocol = response_headers.get("sec-websocket-protocol")
        log.debug(f"backend subprotocol returned: {self.subprotocol!r}")
