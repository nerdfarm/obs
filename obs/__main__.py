""" Entry point for obs """

import logging
import concurrent.futures as futures

from .mq.hangouts_mq import HangoutsMq
from .relay.hangouts_relay import HangoutsRelay

LOG = logging.getLogger(__name__)


def main():
    """ Main obs entrypoint """

    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
    )

    LOG.info("Init hangouts_mq")
    hangouts_mq = HangoutsMq(
        host="localhost",
        port=1883,
        qos=2,
        mq_pub_client_id="hangouts_pub_client",
        mq_pub_topic="obs/hangouts_to_pub",
        mq_sub_client_id="hangouts_sub_client",
        mq_sub_topic="obs/hangouts_to_sub"
    )

    LOG.info("Init hangouts_relay")
    hangouts_relay = HangoutsRelay(
        auth_token_path="",
        client_id="hangouts_relay",
        hangouts_conversation_id="",
        mq_client=hangouts_mq
    )

    LOG.info("hangouts_relay connect")

    tpe = futures.ThreadPoolExecutor(max_workers=24)
    relay_futures = tpe.map(lambda relay: relay.run(), [hangouts_relay])
    futures.wait(list(relay_futures))


if __name__ == "__main__":
    main()
