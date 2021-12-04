import json
import os

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures")


def get_fixture(filepath):
    """Get fixture content.

    :param string filepath: Path to file.

    """
    with open(os.path.join(FIXTURES_DIR, filepath)) as fixture:
        return json.loads(fixture.read())
