""" Base API for obs messaging brokering """


class Mq(object):
    """ Base API for obs messaging brokering """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def subscribe(self, on_relay_out):
        """ Subscribe to mq, calling on_relay_out on msg """
        raise NotImplementedError('Implement this class')

    def unsubscribe(self):
        """ Unsubscribe from mq """
        raise NotImplementedError('Implement this class')

    def publish(self, payload):
        """ Publish payload to mq """
        raise NotImplementedError('Implement this class')
