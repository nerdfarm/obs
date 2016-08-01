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
        LOG.info("Starting test_mq_message_to_hangouts")
        test_send_message = "test_send_message_" + str(datetime.now())

        LOG.info("Starting test_mq_message_to_hangouts hangups client")
        thread = threading.Thread(
            target=init_hangouts_client,
            args=(os.path.expanduser(auth_token_path), conversation_id, test_send_message,)
        )
        thread.setDaemon(True)
        thread.start()
        time.sleep(5)

        LOG.info("Starting test_mq_message_to_hangouts mq_client")
        mq_client = mqtt.Client(client_id="test_mq_client", clean_session=False)
        rc = mq_client.connect(host="localhost", port=1883)
        LOG.info("MQ client connect returned rc: %s", str(rc))
        if int(rc) is not 0:
            LOG.info("Failed to connect to mq host")
            sys.exit(1)
        LOG.info("Publishing test message to topic: %s", "obs/hangouts_to_sub")
        client_thread = threading.Thread(target=mq_client.loop_forever)
        client_thread.setDaemon(True)
        client_thread.start()
        mq_client.publish(payload=test_send_message, topic="obs/hangouts_to_sub", qos=2, retain=False)

    except Exception as error:
        LOG.error("test_mq_message_to_hangouts failed: %s" + str(error))
        sys.exit(1)

    time.sleep(5)
    LOG.error("Failed to send mosquitto_to_hangouts message")
    sys.exit(1)


def init_hangouts_client(auth_token_path, conversation_id, test_send_message):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    cookies = hangups.get_auth_stdin(auth_token_path)
    client = hangups.Client(cookies)
    client.on_state_update.add_observer(functools.partial(assert_message, test_message=test_send_message))
    LOG.info("Connecting hangups client")
    loop.run_until_complete(client.connect())


def assert_message(state_update, test_message):
    segments = list(state_update.event_notification.event.chat_message.message_content.segment)
    received_message = "".join([x.text for x in segments])
    LOG.info(received_message)
    if received_message == test_message:
        LOG.info("Message success, received_message: %s, message to compare to: %s", received_message, test_message)
        os._exit(0)
    else:
        raise AssertionError("Message1: %s, and Message2: %s differ", received_message, test_message)


if __name__ == "__main__":
    main(sys.argv[1:])
