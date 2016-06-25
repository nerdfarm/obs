# pylint: disable=unused-argument,invalid-name
""" Hangouts mq client """

import logging
import functools

import paho.mqtt.client as mqtt

from .mq import Mq

LOG = logging.getLogger(__name__)


class HangoutsMq(Mq):
    """ Wraps Mq methods to create sub and pub mq clients """

    MQ_ARG_WHITELIST = ['mq_host', 'mq_port', 'mq_qos', 'mq_client_id', 'mq_sub_topic', 'mq_pub_topic']

    def __init__(self, mq_host, mq_port, mq_qos, mq_client_id, mq_sub_topic, mq_pub_topic):
        self._mq_host = mq_host
        self._mq_port = mq_port
        self._mq_qos = mq_qos
        self._mq_client_id = mq_client_id
        self._mq_pub_topic = mq_pub_topic
        self._mq_sub_topic = mq_sub_topic
        self._mq_client = mqtt.Client(client_id=self._mq_client_id, clean_session=False)
        super(HangoutsMq, self).__init__()

    def subscribe(self, on_relay_out):
        """ Subscribe mosquitto mq client """
        try:
            self._mq_client.on_connect = self._on_connect
            self._mq_client.on_message = functools.partial(HangoutsMq._on_message, on_relay_out=on_relay_out)
            connect_status = self._mq_client.connect(self._mq_host, port=self._mq_port)
            LOG.info("MQ connection status: %s", str(connect_status))
            subscribe_status = self._mq_client.subscribe(topic=self._mq_sub_topic, qos=self._mq_qos)
            LOG.info("MQ subscribe status: %s", str(subscribe_status))
            self._mq_client.loop_start()
        except Exception as e:
            LOG.error("Failed to connect and/or subscribe to mqtt: %s", e)

    def unsubscribe(self):
        try:
            self._mq_client.unsubscribe(self._mq_sub_topic)
            self._mq_client.loop_stop()
            self._mq_client.disconnect()
        except Exception as e:
            LOG.error("Failed to disconnect and unsubscribe to mqtt: %s", e)

    def _on_connect(self, client, user_data, flags, rc):
        """ Log mosquitto mq client connection response """
        LOG.info("Connected to mqtt host at: %s:%s, mq_client_id: %s, with code: %s",
                 self._mq_host, str(self._mq_port), self._mq_client_id, str(rc))

    def _on_subscribe(self, client, user_data, mid, granted_qos):
        """ Log mosquitto mq client subscription response """
        LOG.info("Subscribed to mqtt host at: %s:%s, topic: %s, mq_client_id: %s, granted_qos: %s",
                 self._mq_host, str(self._mq_port), self._mq_sub_topic, self._mq_client_id, granted_qos)

    @staticmethod
    def _on_message(client, user_data, msg, on_relay_out):
        """ Relay a mosquitto mq event out """
        LOG.info("Received a message from topic: %s", msg.topic)
        on_relay_out({"message": msg.payload.decode(encoding='utf-8', errors='ignore')})

    def publish(self, payload):
        try:
            self._mq_client.publish(
                topic=self._mq_pub_topic,
                payload=payload['message'],
                qos=self._mq_qos,
                retain=False
            )
        except Exception as e:
            LOG.error("Failed to publish to mqtt: %s", e)
