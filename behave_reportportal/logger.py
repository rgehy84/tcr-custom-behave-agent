"""Module provides logging functionality."""
import logging
import sys
from logging import NOTSET, Handler, Logger


class RPLogger(Logger):
    """RPLogger class for logging tests."""

    def __init__(self, name, level=NOTSET):
        """
        Initialize RPLogger instance.

        :param name:  logger name
        :param level: level of logs
        """
        super().__init__(name, level=level)

    def _log(
        self,
        level,
        msg,
        args,
        exc_info=None,
        extra=None,
        stack_info=False,
        stacklevel=1,
        file_to_attach=None,
        is_launch_log=False,
    ):
        if file_to_attach or is_launch_log:
            extra = extra or {}
            if file_to_attach:
                extra["file_to_attach"] = file_to_attach
            if is_launch_log:
                extra["is_launch_log"] = is_launch_log
        pass_args = [level, msg, args, exc_info, extra, stack_info]
        if sys.version_info >= (3, 8):
            pass_args.append(stacklevel)
        super()._log(*pass_args)

    def makeRecord(
        self,
        name,
        level,
        fn,
        lno,
        msg,
        args,
        exc_info,
        func=None,
        extra=None,
        sinfo=None,
    ):
        """Override building of record to add custom fields."""
        record = super().makeRecord(
            name, level, fn, lno, msg, args, exc_info, func, extra, sinfo
        )

        record.is_launch_log = False
        record.file_to_attach = None
        if extra:
            record.file_to_attach = extra.get("file_to_attach", None)
            record.is_launch_log = extra.get("is_launch_log", False)

        return record


class RPHandler(Handler):
    """Provide ability to send logs to Report Portal."""

    # Map loglevel codes from `logging` module to ReportPortal text names:
    _loglevel_map = {
        logging.CRITICAL: "FATAL",
        logging.ERROR: "ERROR",
        logging.WARNING: "WARN",
        logging.INFO: "INFO",
        logging.DEBUG: "DEBUG",
        logging.NOTSET: "TRACE",
    }

    def __init__(self, rp, level=NOTSET):
        """Initialize handler."""
        super().__init__(level)
        self.rp = rp

    def emit(self, record):
        """Send log message to Report Portal."""
        msg = self.format(record)
        log_level = self._get_rp_log_level(record.levelno)
        if record.is_launch_log:
            self.rp.post_launch_log(
                msg,
                log_level,
                file_to_attach=record.file_to_attach,
            )
        else:
            self.rp.post_log(
                msg,
                log_level,
                file_to_attach=record.file_to_attach,
            )

    def _get_rp_log_level(self, levelno):
        return next(
            (
                self._loglevel_map[level]
                for level in self._loglevel_map
                if levelno >= level
            ),
            "TRACE",
        )
