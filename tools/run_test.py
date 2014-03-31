#!/usr/bin/env python

""" Test runner for GAE

Code originally found in `GAE docs`_.

.. _GAE docs: https://developers.google.com/appengine/docs/python/tools/localunittesting
"""

import os
import optparse
import sys
import unittest
import platform
import time

USAGE = """%prog SDK_PATH TEST_PATH
Run unit tests for App Engine apps.

SDK_PATH    Path to the SDK installation
TEST_PATH   Path to package containing test modules"""


def main(sdk_path, test_path):
    import dev_appserver
    dev_appserver.fix_sys_path()
    suite = unittest.loader.TestLoader().discover(test_path)
    unittest.TextTestRunner(verbosity=1).run(suite)


if __name__ == '__main__':
    from watchdog.observers import Observer
    from watchdog.observers.read_directory_changes import WindowsApiObserver

    parser = optparse.OptionParser(USAGE)
    options, args = parser.parse_args()
    if len(args) != 2:
        print 'Error: Exactly 2 arguments required.'
        parser.print_help()
        sys.exit(1)
    SDK_PATH = args[0]
    TEST_PATH = args[1]

    # Append all necessary paths
    sys.path.insert(0, SDK_PATH)
    sys.path.insert(0, '.')
    sys.path.insert(0, 'vendor')

    # Run once first
    main(SDK_PATH, TEST_PATH)

