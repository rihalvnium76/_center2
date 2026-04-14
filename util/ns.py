import argparse
import ctypes
import logging
import random
import time


class LogFormatter(logging.Formatter):
    def format(self, record):
        record.levelname = record.levelname[0]
        return super().format(record)

def build_logger():
    handler = logging.StreamHandler()
    formatter = LogFormatter(
        fmt="[%(levelname)s %(asctime)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger

log = build_logger()

class NoSleepNative:
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    ES_DISPLAY_REQUIRED = 0x00000002
    ES_AWAYMODE_REQUIRED = 0x00000040

    @staticmethod
    def buildSetThreadExecutionState():
        SetThreadExecutionState = ctypes.windll.kernel32.SetThreadExecutionState
        SetThreadExecutionState.argtypes = [ctypes.c_uint]
        SetThreadExecutionState.restype = ctypes.c_uint
        return SetThreadExecutionState

    SetThreadExecutionState = buildSetThreadExecutionState()

    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser()

        parser.add_argument(
            "-d",
            action="store_true",
            dest="display",
            default=False,
            help="Keep display on",
        )

        return parser.parse_args()

    WAKE = ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED
    WAKE_WITH_DISPLAY = ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED | ES_DISPLAY_REQUIRED

    @classmethod
    def run(cls):
        args = cls.parse_args()
        
        log.debug(f"display: {args.display}")

        if args.display:
            execution_state = cls.WAKE_WITH_DISPLAY
        else:
            execution_state = cls.WAKE

        log.info("NoSleep Native is running...")

        try:
            while True:
                cls.SetThreadExecutionState(execution_state)
                time.sleep(random.randint(10, 20))
        except KeyboardInterrupt:
            log.info("Received interrupt signal, restoring state...")
            cls.SetThreadExecutionState(cls.ES_CONTINUOUS)

if __name__ == "__main__":
    NoSleepNative.run()