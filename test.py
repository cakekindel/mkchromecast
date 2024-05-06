#!/usr/bin/env python3

# This file is part of mkchromecast.

import argparse
import logging
import os
import pathlib
import shutil
import subprocess
import sys
import time
import unittest

import pychromecast


# Modify this to enable debug logging of test outputs.
ENABLE_DEBUG_LOGGING = False

# This argument parser will steal arguments from unittest.  So we only define
# arguments that are needed for the integration test, and that won't collide
# with arguments that unittest cares about (like --help).
integration_arg_parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)

integration_arg_parser.add_argument(
    "--test-connect-to",
    type=str,
    help=(
        "Enables integration test mode, and attempts to connect to the "
        "Chromecast with the specified friendly name"
    ),
)

integration_args = ...


class MkchromecastTests(unittest.TestCase):
    def setUp(self):
        # TODO(xsdg): Do something better than just listing files by hand.
        target_names = [
            "bin/mkchromecast",
            "mkchromecast/",
            "setup.py",
            "start_tray.py",
            "test.py"
        ]

        # Makes target names absolute.
        self.parent_dir = pathlib.Path(__file__).parent
        self.type_targets = [self.parent_dir / name for name in target_names]

    def testMyPy(self):
        """Runs the mypy static type analyzer, if it's installed."""
        if not shutil.which("mypy"):
            self.skipTest("mypy not installed")

        mypy_cmd = [
            "mypy",
            "--ignore-missing-imports",
            "--no-namespace-packages",
            "--check-untyped-defs"
        ]

        mypy_result = subprocess.run(
            mypy_cmd + self.type_targets,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding="utf8",
        )

        if mypy_result.returncode:
            self.fail(mypy_result.stdout)
        else:
            # Debug-log for diagnostic purposes.
            logging.debug(mypy_result.stdout)

    def testPytype(self):
        """Runs the pytype static type analyzer, if it's installed."""
        if not shutil.which("pytype"):
            self.skipTest("pytype not installed")

        pytype_cmd = ["pytype", "-k", "-j", "auto", "--no-cache"]
        pytype_result = subprocess.run(
            pytype_cmd + self.type_targets,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding="utf8",
        )

        if pytype_result.returncode:
            self.fail(pytype_result.stdout)
        else:
            # Debug-log for diagnostic purposes.
            logging.debug(pytype_result.stdout)

    def testExecUnitTests(self):
        """Runs the Mkchromecast unit test suite."""
        tests_dir = self.parent_dir / "tests"
        pytest_cmd = [
            "python3",
            "-m", "unittest",
            "discover",
            "-s", tests_dir,
            "-t", tests_dir,
        ]

        # Set PYTHONPATH to include parentdir, so that the unit tests can
        # import mkchromecast regardless of how the current file is executed.
        custom_env = os.environ.copy()
        orig_python_path = os.environ.get("PYTHONPATH", "")
        custom_env["PYTHONPATH"] = f"{self.parent_dir}:{orig_python_path}"
        pytest_result = subprocess.run(
            pytest_cmd,
            env=custom_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding="utf8",
        )

        if pytest_result.returncode:
            self.fail(pytest_result.stdout)
        else:
            # Always show unit test output, even when they pass.
            logging.info("\n" + pytest_result.stdout)

    # "ZZ" prefix so this runs last.
    def testZZEndToEndIntegration(self):
        args = integration_args  # Shorthand.

        if not args.test_connect_to:
            self.skipTest("Specify --test-connect-to to run integration test")

        # TODO(xsdg): pychromecast API has changed significantly since this was
        # written, so this test is currently broken.
        self.skipTest("Integration test is currently broken :(")

        cast = pychromecast.get_chromecast(friendly_name=args.test_connect_to)
        print("Connected to Chromecast")
        mc = cast.media_controller
        print("Playing BigBuckBunny.mp4 (video)")
        # TODO(xsdg): use https.
        mc.play_media(
            "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "video/mp4",
        )
        time.sleep(15)
        print("Stopping video and sleeping for 5 secs")
        mc.stop()
        time.sleep(5)
        print("Playing Canon mp3 (audio)")
        # TODO(xsdg): This link is broken; find something else that's more
        # stable.  Also, https.
        mc.play_media("http://www.stephaniequinn.com/Music/Canon.mp3", "audio/mp3")
        time.sleep(15)
        print("Stopping audio and quitting app")
        mc.stop()
        cast.quit_app()


if __name__ == "__main__":
    loglevel = logging.INFO if not ENABLE_DEBUG_LOGGING else logging.DEBUG
    logging.basicConfig(format="%(levelname)s:%(message)s", level=loglevel)

    # Steals known arguments from unittest in order to properly configure the
    # integration test.
    integration_args, skipped_argv = integration_arg_parser.parse_known_args()
    sys.argv[1:] = skipped_argv
    unittest.main(verbosity=2)
