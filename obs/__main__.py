""" Entry point for obs """

import sys
import getopt
import logging
import multiprocessing
import traceback

import obs.config as ObsConfig

LOG = logging.getLogger(__name__)


def main(argv):
    """ Main obs entrypoint """

    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
    )

    relay_processes = []
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
            process = multiprocessing.Process(target=relay.run)
            relay_processes.append(process)
            process.daemon = True
            process.start()
            LOG.info("Loaded relay with relay_client_id: %s", relay.get_relay_client_id())
        for relay_process in relay_processes:
            relay_process.join()
    except getopt.GetoptError as error:
        LOG.error("Must supply config YAML path as first argument: %s", error)
        traceback.format_exc()
    except Exception as exception:
        LOG.error("Caught exception: %s", exception)
        traceback.format_exc()
    finally:
        LOG.info("Shutting down")
        for relay_process in relay_processes:
            relay_process.terminate()
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
