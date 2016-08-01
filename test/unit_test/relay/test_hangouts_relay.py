from unittest import TestCase

import hangups
from nose.plugins.attrib import attr

from obs.relay.hangouts_relay import HangoutsRelay


@attr(speed='fast')
class TestHangoutsRelay(TestCase):

    def test_is_not_duplicate(self):
        test_not_duplicate_msg = hangups.hangouts_pb2.StateUpdate(
            event_notification=hangups.hangouts_pb2.EventNotification(
                event=hangups.hangouts_pb2.Event(
                    conversation_id=hangups.hangouts_pb2.ConversationId(
                        id='convo'
                    ),
                    self_event_state=hangups.hangouts_pb2.UserEventState(
                        user_id=hangups.hangouts_pb2.ParticipantId(
                            chat_id='self_id',
                            gaia_id='self_id'
                        )
                    ),
                    sender_id=hangups.hangouts_pb2.ParticipantId(
                        chat_id='other_id',
                        gaia_id='other_id'
                    )
                )
            )
        )
        self.assertTrue(HangoutsRelay._is_not_duplicate(test_not_duplicate_msg))

    def test_is_duplicate(self):
        test_duplicate_msg = hangups.hangouts_pb2.StateUpdate(
            event_notification=hangups.hangouts_pb2.EventNotification(
                event=hangups.hangouts_pb2.Event(
                    conversation_id=hangups.hangouts_pb2.ConversationId(
                        id='convo'
                    ),
                    self_event_state=hangups.hangouts_pb2.UserEventState(
                        user_id=hangups.hangouts_pb2.ParticipantId(
                            chat_id='other_id',
                            gaia_id='other_id'
                        )
                    ),
                    sender_id=hangups.hangouts_pb2.ParticipantId(
                        chat_id='other_id',
                        gaia_id='other_id'
                    )
                )
            )
        )
        self.assertFalse(HangoutsRelay._is_not_duplicate(test_duplicate_msg))

    def test_is_in_conversation(self):
        conversation_id = 'our_id'
        sender_id = 'sender_id'
        test_in_conversation_msg = hangups.hangouts_pb2.StateUpdate(
            event_notification=hangups.hangouts_pb2.EventNotification(
                event=hangups.hangouts_pb2.Event(
                    conversation_id=hangups.hangouts_pb2.ConversationId(
                        id=conversation_id
                    ),
                    self_event_state=hangups.hangouts_pb2.UserEventState(
                        user_id=hangups.hangouts_pb2.ParticipantId(
                            chat_id=conversation_id,
                            gaia_id=conversation_id
                        )
                    ),
                    sender_id=hangups.hangouts_pb2.ParticipantId(
                        chat_id=sender_id,
                        gaia_id=sender_id
                    )
                )
            )
        )
        self.assertTrue(HangoutsRelay._is_in_conversation(test_in_conversation_msg, conversation_id))

    def test_is_not_in_conversation(self):
        conversation_id = 'our_id'
        not_in_conversation_id = 'their_id'
        sender_id = 'sender_id'
        test_not_in_conversation_msg = hangups.hangouts_pb2.StateUpdate(
            event_notification=hangups.hangouts_pb2.EventNotification(
                event=hangups.hangouts_pb2.Event(
                    conversation_id=hangups.hangouts_pb2.ConversationId(
                        id=not_in_conversation_id
                    ),
                    self_event_state=hangups.hangouts_pb2.UserEventState(
                        user_id=hangups.hangouts_pb2.ParticipantId(
                            chat_id=not_in_conversation_id,
                            gaia_id=not_in_conversation_id
                        )
                    ),
                    sender_id=hangups.hangouts_pb2.ParticipantId(
                        chat_id=sender_id,
                        gaia_id=sender_id
                    )
                )
            )
        )
        self.assertFalse(HangoutsRelay._is_in_conversation(test_not_in_conversation_msg, conversation_id))
