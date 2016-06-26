from unittest import TestCase

import os
import subprocess


class TestEteMosquittoHangouts(TestCase):

    def test_ete_mosquitto_hangouts(self):
        ete_sp = subprocess.Popen([
            "python3",
            "-m",
            "test.integration_test.ete_mosquitto_hangouts",
            '--auth_token_path=' + os.path.expanduser('~/' + os.environ['TEST_HANGOUTS_AUTH_TOKEN_NAME']),
            '--conversation_id=' + os.environ['HANGOUTS_CONVERSATION_ID'],
            '--config=' + os.path.expanduser('~/' + os.environ['TEST_CONFIG_NAME'])
        ])
        out = ete_sp.communicate()[0]
        self.assertEqual(0, ete_sp.returncode)