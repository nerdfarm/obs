""" Config parsing for yaml -> Relays and mq clients """

import importlib
import logging
import yaml

LOG = logging.getLogger(__name__)


def parse_obs_config(path_to_yaml):
    """ Method to parse relays and mq clients directly from yaml """
    with open(path_to_yaml, 'r') as stream:
        try:
            parsed_yaml = yaml.load(stream)
            return [_build_relay(relay) for relay in parsed_yaml["relay"]]
        except yaml.YAMLError as exc:
            LOG.error(exc)


def _build_relay(args):
    """ Constructs relays and mq clients for a single YAML entry """
    mq_class = getattr(importlib.import_module(args['mq_module']), args['mq_class_name'])
    filtered_mq_args = {k: v for k, v in args.items() if k in mq_class.MQ_ARG_WHITELIST}
    mq_client = mq_class(**filtered_mq_args)

    relay_class = getattr(importlib.import_module(args['relay_module']), args['relay_class_name'])
    filtered_relay_args = {k: v for k, v in args.items() if k in relay_class.RELAY_ARG_WHITELIST}
    filtered_relay_args['mq_client'] = mq_client
    return relay_class(**filtered_relay_args)
