""" Base API for obs messaging brokering """


class Mq(object):
    """ Base API for obs messaging brokering """

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs

    def sub_client(self, on_relay_out):
        """ Get an mq-subscribing client that calls provided on_relay_out on message receipt """
        raise NotImplementedError('Implement this class')

    def pub_client(self, payload):
        """ Get an mq-publishing client that publishes the provided paylod """
        raise NotImplementedError('Implement this class')
