""" """

import os
import sys
import asyncio
import time
import functools
import threading
import logging
from datetime import datetime

import hangups
import paho.mqtt.client as mqtt

from obs.__main__ import main as obs_main
from obs.__main__ import parse_config_args

LOG = logging.getLogger(__name__)


def main(argv):
    parsed_args = parse_config_args(argv, ['config=', 'conversation_id=', 'auth_token_path='])
    config_path = parsed_args['--config']
    conversation_id = parsed_args['--conversation_id']
    auth_token_path = parsed_args['--auth_token_path']
    if not config_path or not conversation_id or not auth_token_path:
        raise RuntimeError("Encountered null or empty config path, conversation id, or auth_token_path "
                           "exiting; config_path: %s, conversation_id: %s, auth_token_path:%s, args: %s",
                           config_path, conversation_id, auth_token_path, str(argv))

    # Start obs
    LOG.info("Starting obs...")
    obs_main_thread = threading.Thread(target=functools.partial(obs_main, argv=['--config=' + config_path]))
    obs_main_thread.setDaemon(True)
    obs_main_thread.start()
    time.sleep(5)

    try:
        LOG.info("Starting test_hangouts_message_to_mq")
        test_send_message = "test_send_message_" + str(datetime.now())

        LOG.info("Starting test_hangouts_message_to_mq mq_client")
        mq_client = mqtt.Client(client_id="test_mq_client", clean_session=False)

        mq_client.on_message = functools.partial(assert_message, message2=test_send_message)
        rc = mq_client.connect(host="localhost", port=1883)
        LOG.info("MQ client connect returned rc: %s", str(rc))
        if int(rc) is not 0:
            LOG.info("Failed to connect to mq host")
            sys.exit(1)
        mq_client.subscribe(topic="obs/hangouts_to_pub", qos=2)
        client_thread = threading.Thread(target=mq_client.loop_forever)
        client_thread.setDaemon(True)
        client_thread.start()

        LOG.info("Starting test_hangouts_message_to_mq hangups sending test message")
        thread = threading.Thread(
            target=send_hangouts_message_loop,
            args=(os.path.expanduser(auth_token_path), conversation_id, test_send_message,)
        )
        thread.setDaemon(True)
        thread.start()
    except Exception as error:
        LOG.error("test_hangouts_message_to_mq failed: %s" + str(error))
        sys.exit(1)

    time.sleep(20)
    LOG.error("Failed to send hangouts_to_mosquitto message")
    sys.exit(1)


def send_hangouts_message_loop(auth_token_path, conversation_id, test_send_message):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    cookies = hangups.get_auth_stdin(auth_token_path)
    client = hangups.Client(cookies)
    thread = threading.Timer(5, hangups_send_hangouts_message, args=(client, conversation_id, test_send_message,))
    thread.start()
    LOG.info("Connecting hangups client")
    loop.run_until_complete(client.connect())


def hangups_send_hangouts_message(sender, conversation_id, message):
    request = hangups.hangouts_pb2.SendChatMessageRequest(
        request_header=sender.get_request_header(),
        event_request_header=hangups.hangouts_pb2.EventRequestHeader(
            conversation_id=hangups.hangouts_pb2.ConversationId(
                id=conversation_id
            ),
            client_generated_id=sender.get_client_generated_id(),
        ),
        message_content=hangups.hangouts_pb2.MessageContent(
            segment=[hangups.ChatMessageSegment(message).serialize()],
        ),
    )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    LOG.info("Sending hangups message")
    loop.run_until_complete(sender.send_chat_message(request))
    loop.close()
    sender.disconnect()


def assert_message(client, user_data, msg, message2):
    received_message = msg.payload.decode(encoding='utf-8', errors='ignore')
    LOG.info(received_message)
    if received_message == message2:
        LOG.info("Message success, received_message: %s, message to compare to: %s", received_message, message2)
        os._exit(0)
    else:
        raise AssertionError("Message1: %s, and Message2: %s differ", received_message, message2)


if __name__ == "__main__":
    main(sys.argv[1:])
