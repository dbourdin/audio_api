"""ColorizedFormatter class."""

import logging
import sys
from copy import copy
from typing import Literal

import click

TRACE_LOG_LEVEL = 5


class ColorizedFormatter(logging.Formatter):
    """ColorizedFormatter class.

    A custom log formatter class that:

    * Outputs the LOG_LEVEL with an appropriate color.
    * If a log call includes an `extras={"color_message": ...}` it will be used
      for formatting the output, instead of the plain text message.
    """

    level_name_colors = {
        TRACE_LOG_LEVEL: lambda level_name: click.style(str(level_name), fg="blue"),
        logging.DEBUG: lambda level_name: click.style(str(level_name), fg="cyan"),
        logging.INFO: lambda level_name: click.style(str(level_name), fg="green"),
        logging.WARNING: lambda level_name: click.style(str(level_name), fg="yellow"),
        logging.ERROR: lambda level_name: click.style(str(level_name), fg="red"),
        logging.CRITICAL: lambda level_name: click.style(
            str(level_name), fg="bright_red"
        ),
    }

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
        use_colors: bool | None = None,
    ):
        """Create a new formatter.

        Args:
            fmt: Log format.
            datefmt: Log date format.
            style: Log format style.
            use_colors: Whether it should use colors or not.
        """
        if use_colors in (True, False):
            self.use_colors = use_colors
        else:
            self.use_colors = sys.stdout.isatty()
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def color_level_name(self, level_name: str, level_no: int) -> str:
        """Get color for a specific level.

        Args:
            level_name: Log level name.
            level_no: Log level no.

        Returns:
            str: Color level name.
        """

        def default(level_name: str) -> str:
            return str(level_name)  # pragma: no cover

        func = self.level_name_colors.get(level_no, default)
        return func(level_name)

    def should_use_colors(self) -> bool:
        """Return True.

        Returns:
              bool: True
        """
        return True  # pragma: no cover

    def formatMessage(self, record: logging.LogRecord) -> str:  # noqa
        """Format a record using formatter.

        Args:
            record: LogRecord to format.

        Returns:
            str: Formatted message.
        """
        recordcopy = copy(record)
        levelname = recordcopy.levelname
        seperator = " " * (8 - len(recordcopy.levelname))
        if self.use_colors:
            levelname = self.color_level_name(levelname, recordcopy.levelno)
            if "color_message" in recordcopy.__dict__:
                recordcopy.msg = recordcopy.__dict__["color_message"]
                recordcopy.__dict__["message"] = recordcopy.getMessage()
        recordcopy.__dict__["levelprefix"] = levelname + ":" + seperator
        return super().formatMessage(recordcopy)


class DefaultFormatter(ColorizedFormatter):
    """DefaultFormatter class."""

    def should_use_colors(self) -> bool:
        """Override default should_use_colors behavior."""
        return sys.stderr.isatty()  # pragma: no cover
