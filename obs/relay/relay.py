""" Base Relay Client API """


class Relay(object):
    """ Base Relay Client API """

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """ Call to run this relay """
        raise NotImplementedError('Implement this class')

    def relay_out(self, payload):
        """ Executed to push out from relay """
        raise NotImplementedError('Implement this class')

    def relay_in(self, payload):
        """ Executed to push in from relay """
        raise NotImplementedError('Implement this class')
