import logging

from app.logging_setup import setup_logging


def test_setup_logging_runs():
    setup_logging()
    logging.getLogger("seo").info("logging works")