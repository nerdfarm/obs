""" Config parsing for yaml -> Relays and mq clients """

import os
import importlib
import logging

import yaml

LOG = logging.getLogger(__name__)


def parse_obs_config(path_to_yaml):
    """ Method to parse relays and mq clients directly from yaml """
    with open(os.path.expanduser(path_to_yaml), 'r') as stream:
        try:
            parsed_yaml = yaml.load(stream)
            return [_build_relay(relay) for relay in parsed_yaml["relay"]]
        except yaml.YAMLError as exc:
            LOG.error(exc)


def _build_relay(args):
    """ Constructs relays and mq clients for a single YAML entry """
    mq_class = getattr(importlib.import_module(args['mq_module']), args['mq_class_name'])
    filtered_mq_args = {k: v for k, v in args.items() if k in mq_class.MQ_ARG_WHITELIST}
    LOG.info("Building mq client with args: %s", str(filtered_mq_args))
    if not _is_valid_args(filtered_mq_args, mq_class.MQ_ARG_WHITELIST):
        raise Exception("Invalid arguments for mq client")
    mq_client = mq_class(**filtered_mq_args)

    relay_class = getattr(importlib.import_module(args['relay_module']), args['relay_class_name'])
    filtered_relay_args = {k: v for k, v in args.items() if k in relay_class.RELAY_ARG_WHITELIST}
    LOG.info("Building relay with args: %s", str(filtered_relay_args))
    filtered_relay_args['mq_client'] = mq_client
    if not _is_valid_args(filtered_relay_args, relay_class.RELAY_ARG_WHITELIST):
        raise Exception("Invalid arguments for relay")
    return relay_class(**filtered_relay_args)


def _is_valid_args(args, arg_whitelist):
    for required_arg in arg_whitelist:
        if required_arg not in args:
            LOG.error("Missing required argument: %s, args: %s, required args: %s", required_arg, args, arg_whitelist)
            return False
    return True
