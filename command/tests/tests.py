from unittest import TestCase
from command.cli import main

class TestConsole(TestCase):
    def test_basic(self):
        main()
