from unittest import TestCase
import hangups

from obs.relay.hangouts_relay import HangoutsRelay


class TestHangoutsRelay(TestCase):

    def test_is_not_duplicate(self):
        test_not_duplicate_msg = hangups.hangouts_pb2.StateUpdate(
            event_notification=hangups.hangouts_pb2.EventNotification(
                event=hangups.hangouts_pb2.Event(
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
