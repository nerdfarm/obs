""" Entry point for obs """

import os
import sys
import signal
import getopt
import logging
import concurrent.futures as futures

import obs.config as ObsConfig

LOG = logging.getLogger(__name__)


def main(argv):
    """ Main obs entrypoint """

    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
    )

    tpe = futures.ThreadPoolExecutor(max_workers=24)
    try:
        _, args = getopt.getopt(argv, "c", ["config"])

        LOG.info("Loading config.yml from: %s", args[0])
        relays = ObsConfig.parse_obs_config(args[0])
        relay_futures = tpe.map(lambda relay: relay.run(), relays)
        futures.wait(list(relay_futures))
    except getopt.GetoptError as error:
        LOG.error("Must supply config YAML path as first argument: %s", error)
    finally:
        tpe.shutdown(False)
        os.kill(os.getpid(), signal.SIGUSR1)


if __name__ == "__main__":
    main(sys.argv[1:])
