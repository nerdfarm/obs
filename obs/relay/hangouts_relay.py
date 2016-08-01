# pylint: disable=attribute-defined-outside-init
""" Google Hangouts Relay """

import os
import logging
import asyncio
import threading

import hangups

from .relay import Relay

LOG = logging.getLogger(__name__)


class HangoutsRelay(Relay):
    """ Hangouts Relay implementation that handles relays to and from an mq service. """

    RELAY_ARG_WHITELIST = ['auth_token_path', 'relay_client_id', 'hangouts_conversation_id']

    def __init__(self, auth_token_path, relay_client_id, hangouts_conversation_id, mq_client):
        self._auth_token_path = os.path.expanduser(auth_token_path)
        self._relay_client_id = relay_client_id
        self._hangouts_conversation_id = hangouts_conversation_id
        self._mq_client = mq_client
        super(HangoutsRelay, self).__init__()

    def get_relay_client_id(self):
        """ Return relay_client_id """
        return self._relay_client_id

    def _init_sub_client(self):
        """ Initialize the mq subscribing client """
        self._mq_client.subscribe(on_relay_out=self.relay_out)

    def run(self):
        """
        Called to run this module. This is blocking for the life of the application in order to keep clients alive
        """
        LOG.info("Running relay")
        self._init_sub_client()
        self._connect()

    def stop(self):
        """ Called to stop this module. Should do any relay clean up here. """
        LOG.info("Stopping relay")
        self._mq_client.unsubscribe()
        if self._client:
            self._client.disconnect()

    def _connect(self):
        """
        Contains logic for setting up hangups client (Hangouts unofficial API module). Runs for the duration of the app.
        """
        # This will run in a thread w/o an instantiated event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        cookies = hangups.get_auth_stdin(self._auth_token_path)
        client = hangups.Client(cookies)
        client.on_connect.add_observer(self._on_connect)
        client.on_state_update.add_observer(self._on_state_update)

        self._client = client
        loop.run_until_complete(self._client.connect())
        # client.on_connect
        # client.on_disconnect
        # client.on_reconnect

    def _on_connect(self):
        """ Log client info on hangups client connect """
        self_info = hangups.hangouts_pb2.GetSelfInfoRequest(request_header=self._client.get_request_header(),)
        LOG.info("Hangouts self info: " + str(self_info))

    def _on_state_update(self, state_update):
        """
        This callback runs for any updates from Hangouts, from messages to hover events. Therefore we filter just for
        new messages.
        """
        LOG.debug("state_update: " + str(state_update))
        if state_update.HasField('conversation') and \
                HangoutsRelay._is_in_conversation(state_update, self._hangouts_conversation_id):
            segments = list(state_update.event_notification.event.chat_message.message_content.segment)
            self.relay_in({"message": "".join([x.text for x in segments])})

    @staticmethod
    def _is_not_duplicate(state_update):
        """
        With the Hangouts unofficial API, we need to dedupe messages from our sending to Hangouts, and legitimate
        messages from other parties. This checks for relevant necessary information to make sure a new message
        is not simply an earlier relay_out message.
        """
        return state_update.HasField('event_notification') and \
            state_update.event_notification.HasField('event') and \
            state_update.event_notification.event.HasField('self_event_state') and \
            state_update.event_notification.event.self_event_state.HasField('user_id') and \
            state_update.event_notification.event.self_event_state.user_id.HasField('chat_id') and \
            state_update.event_notification.event.HasField('sender_id') and \
            state_update.event_notification.event.sender_id.HasField('chat_id') and \
            str(state_update.event_notification.event.self_event_state.user_id.chat_id) != \
            str(state_update.event_notification.event.sender_id.chat_id)

    @staticmethod
    def _is_in_conversation(state_update, conversation_id):
        """ Only relay chats in the conversation_id configured for this relay """
        return HangoutsRelay._is_not_duplicate(state_update) and \
            str(state_update.event_notification.event.sender_id.chat_id) == str(conversation_id)

    def relay_out(self, payload):
        """ Builds request to send as Hangouts message """
        LOG.info("relay_out for payload")
        request = hangups.hangouts_pb2.SendChatMessageRequest(
            request_header=self._client.get_request_header(),
            event_request_header=hangups.hangouts_pb2.EventRequestHeader(
                conversation_id=hangups.hangouts_pb2.ConversationId(
                    id=self._hangouts_conversation_id
                ),
                client_generated_id=self._client.get_client_generated_id(),
            ),
            message_content=hangups.hangouts_pb2.MessageContent(
                segment=[hangups.ChatMessageSegment(payload["message"]).serialize()],
            ),
        )
        thread = threading.Thread(target=self._send_message, args=(request,))
        thread.start()

    def _send_message(self, request):
        """ hangups logic for sending a message """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._client.send_chat_message(request))
        loop.close()

    def relay_in(self, payload):
        """ Publishing client that publishes and disconnects from mq service """
        LOG.info("relay_in for payload")
        if self._client:
            LOG.info("mq client found, publishing")
            self._mq_client.publish(payload)
        else:
            raise Exception("Relay has not yet been run, call run()")
