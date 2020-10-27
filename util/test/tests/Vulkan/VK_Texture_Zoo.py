import renderdoc as rd
import rdtest
from typing import List, Tuple
import time
import os


class VK_Texture_Zoo(rdtest.TestCase):
    slow_test = True
    demos_test_name = 'VK_Texture_Zoo'

    def __init__(self):
        rdtest.TestCase.__init__(self)
        self.zoo_helper = rdtest.Texture_Zoo()

    def check_capture(self):
        # This takes ownership of the controller and shuts it down when it's finished
        self.zoo_helper.check_capture(self.capture_filename, self.controller)
        self.controller = None
