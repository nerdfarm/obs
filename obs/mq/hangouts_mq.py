# pylint: disable=unused-argument,invalid-name
""" Hangouts mq client """

import logging
import threading

import paho.mqtt.client as mqtt
import paho.mqtt.publish as paho

from .mq import Mq

LOG = logging.getLogger(__name__)


class HangoutsMq(Mq):
    """ Wraps Mq methods to create sub and pub mq clients """

    MQ_ARG_WHITELIST = ['mq_host', 'mq_port', 'mq_qos', 'mq_sub_client_id',
                        'mq_sub_topic', 'mq_pub_client_id', 'mq_pub_topic']

    def __init__(self, mq_host, mq_port, mq_qos, mq_sub_client_id, mq_sub_topic, mq_pub_client_id, mq_pub_topic):
        self._mq_host = mq_host
        self._mq_port = mq_port
        self._mq_qos = mq_qos
        self._mq_pub_client_id = mq_pub_client_id
        self._mq_pub_topic = mq_pub_topic
        self._mq_sub_client_id = mq_sub_client_id
        self._mq_sub_topic = mq_sub_topic
        super().__init__(options={
            "host": mq_host,
            "port": mq_port,
            "qos": mq_qos,
            "mq_pub_client_id": mq_pub_client_id,
            "mq_pub_topic": mq_pub_topic,
            "mq_sub_client_id": mq_sub_client_id,
            "mq_sub_topic": mq_sub_topic
        })

    def sub_client(self, on_relay_out):
        """ Return a new Hangouts mq sub client """
        return HangoutsSubMq(
            host=self._mq_host,
            port=self._mq_port,
            qos=self._mq_qos,
            mq_client_id=self._mq_sub_client_id,
            mq_topic=self._mq_sub_topic,
            on_relay_out=on_relay_out
        )

    def pub_client(self, payload):
        """ Return a new Hangouts mq pub client """
        return HangoutsPubMq(
            host=self._mq_host,
            port=self._mq_port,
            qos=self._mq_qos,
            mq_topic=self._mq_pub_topic,
            mq_client_id=self._mq_pub_client_id,
            payload=payload
        )


class HangoutsSubMq:
    """ Google Hangouts Subscribing MQ Client """

    def __init__(self, host, port, qos, mq_topic, mq_client_id, on_relay_out):
        self._host = host
        self._port = port
        self._qos = qos
        self._mq_topic = mq_topic
        self._mq_client_id = mq_client_id
        self._on_relay_out = on_relay_out
        self._init_mq_client()

    def _init_mq_client(self):
        """ Initialize mosquitto mq client """
        client = mqtt.Client(client_id=self._mq_client_id, clean_session=False)
        client.on_connect = self._on_connect
        client.on_message = self._on_message
        client.connect(self._host, port=self._port)
        client.subscribe(topic=self._mq_topic, qos=self._qos)
        thread = threading.Thread(target=client.loop_forever)
        thread.start()

    def _on_connect(self, client, user_data, flags, rc):
        """ Log mosquitto mq client connection response """
        LOG.info("Connected to mqtt host at: %s:%s, topic: %s, mq_client_id: %s, with code: %s",
                 self._host, str(self._port), self._mq_topic, self._mq_client_id, str(rc))

    def _on_message(self, client, user_data, msg):
        """ Relay a mosquitto mq event out """
        LOG.info("Received a message from topic: %s", msg.topic)
        self._on_relay_out({"message": msg.payload.decode(encoding='utf-8', errors='ignore')})


class HangoutsPubMq():
    """ Google Hangouts Publishing MQ Client """

    def __init__(self, host, port, qos, mq_topic, mq_client_id, payload):
        self._host = host
        self._port = port
        self._qos = qos
        self._mq_topic = mq_topic
        self._mq_client_id = mq_client_id
        self._payload = payload

    def publish(self):
        """ Publish a message to mq mosquitto """
        paho.single(
            topic=self._mq_topic,
            payload=self._payload["message"],
            qos=self._qos,
            hostname=self._host,
            port=self._port,
            retain=False,
            client_id=self._mq_client_id
        )
