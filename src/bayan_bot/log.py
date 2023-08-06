from __future__ import annotations

from logging import Formatter, Logger, LogRecord, getLogger
from typing import Iterable

from rich.console import Console, ConsoleRenderable
from rich.containers import Renderables
from rich.logging import RichHandler
from rich.text import Text
from rich.traceback import Traceback


def init_logger() -> Logger:
    logger = getLogger("bayan_bot")
    console = Console(
        color_system="truecolor",
        force_terminal=True,
        force_interactive=True,
        soft_wrap=True,
    )
    handler = ExtendedRichHandler("DEBUG", console)
    handler.setFormatter(Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel("DEBUG")
    return logger


# Code below disables columns and wrapping in RichHandler and makes it faster
# Adapted code from enrich:
# https://github.com/pycontribs/enrich/blob/2e6f1a907fdefc8b08e5ae85cdbb2f0189a53e84/src/enrich/logging.py


class LogRender:
    """Renders log by not using columns and avoiding any wrapping."""

    def __call__(self, renderables: Iterable[ConsoleRenderable], level: Text) -> Text:
        # CRITICAL is the longest identifier from default set.
        if len(level) < 9:
            level.append(" " * (9 - len(level)))

        result = level
        for elem in renderables:
            result.append(elem)  # type: ignore[arg-type]

        return result


class ExtendedRichHandler(RichHandler):
    def __init__(
        self,
        level: str | int,
        console: Console,
        *,
        show_time: bool = False,
        show_level: bool = True,
        show_path: bool = False,
        enable_link_path: bool = False,
        rich_tracebacks: bool = True,
        tracebacks_width: int = 130,
        tracebacks_extra_lines: int = 2,
        tracebacks_show_locals: bool = True,
        locals_max_length: int = 50,
        locals_max_string: int | None = None,
    ) -> None:
        super().__init__(
            level=level,
            console=console,
            show_time=show_time,
            show_level=show_level,
            show_path=show_path,
            enable_link_path=enable_link_path,
            rich_tracebacks=rich_tracebacks,
            tracebacks_width=tracebacks_width,
            tracebacks_extra_lines=tracebacks_extra_lines,
            tracebacks_show_locals=tracebacks_show_locals,
            locals_max_length=locals_max_length,
            locals_max_string=locals_max_string,  # type: ignore[arg-type]
        )
        # RichHandler constructor does not allow custom renderer
        # https://github.com/willmcgugan/rich/issues/438
        self._log_render = LogRender()  # type: ignore[assignment]

    def render(
        self,
        *,
        record: LogRecord,
        traceback: Traceback | None,
        message_renderable: ConsoleRenderable,
    ) -> ConsoleRenderable:
        render: LogRender = self._log_render  # type: ignore[assignment]
        message = render([message_renderable], level=self.get_level_text(record))
        if traceback is None:
            return message

        return Renderables((message, traceback))
