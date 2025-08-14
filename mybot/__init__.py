"""Helper entry point for running the Refer & Earn bot as a module."""

from . import config


def run() -> None:
    """Start the bot application.

    Importing :mod:`mybot` and calling :func:`run` provides a simple way to
    execute the bot from another Python program, for example::

        import mybot
        mybot.run()

    """

    from .main import run as _run

    _run()


__all__ = ["run", "config"]
