""" Entry point for obs """

import sys
import getopt
import logging
import threading

import obs.config as ObsConfig

LOG = logging.getLogger(__name__)


def main(argv):
    """ Main obs entrypoint """

    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
    )

    loaded_relays = []
    try:
        parsed_args = parse_config_args(argv, ['config='])
        config_path = parsed_args['--config']
        if not config_path:
            raise RuntimeError("Encountered null or empty config path, exiting; config_path: %s, args: %s",
                               config_path, str(argv))

        LOG.info("Loading config.yml from: %s", config_path)
        relays = ObsConfig.parse_obs_config(config_path)
        LOG.info("Parsed %s %s", str(len(relays)), "relay" if len(relays) == 1 else "relays")
        for relay in relays:
            loaded_relays.append(relay)
            thread = threading.Thread(relay.run())
            thread.setDaemon(True)
            thread.start()
    except getopt.GetoptError as error:
        LOG.error("Must supply config YAML path as first argument: %s", error)
    except Exception as exception:
        LOG.error("Caught exception: %s", exception)
    finally:
        LOG.info("Shutting down")
        for loaded_relay in loaded_relays:
            loaded_relay.stop()
        sys.exit(0)


def parse_config_args(argv, long_opts):
    """ Parses passed in args into a dict """

    parsed_args = {}
    options, _ = getopt.getopt(argv, shortopts='', longopts=long_opts)
    for option in options:
        if option[0] not in long_opts:
            if option[1]:
                if option[0] not in parsed_args.keys():
                    LOG.info("Found path: %s", option[1])
                    parsed_args[option[0]] = option[1]
                else:
                    LOG.warning("Found duplicate, rejecting: {'%s': '%s'}, current parsed_args: %s",
                                option[0], option[1], str(parsed_args))
            else:
                raise RuntimeError("Found config key: %s, but no value: %s", option[0], option[1])
        else:
            LOG.warning("Ignoring unused option: %s", str(option))
    return parsed_args


if __name__ == "__main__":
    main(sys.argv[1:])
