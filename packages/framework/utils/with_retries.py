import logging
import time
import signal
from functools import wraps
from typing import Optional


class TimeoutError(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutError("Execution timed out")


def with_retries(max_retries: int = 10, timeout_seconds: Optional[int] = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    # Set up timeout if specified
                    if timeout_seconds is not None:
                        signal.signal(signal.SIGALRM, timeout_handler)
                        signal.alarm(timeout_seconds)

                    try:
                        result = func(*args, **kwargs)
                        if timeout_seconds is not None:
                            signal.alarm(0)  # Disable alarm
                        return result
                    finally:
                        if timeout_seconds is not None:
                            signal.alarm(0)  # Ensure alarm is disabled

                except TimeoutError as te:
                    if attempt == max_retries - 1:
                        logging.error(
                            f"Failed after {max_retries} attempts due to timeout"
                        )
                        return {"error": f"Timeout after {timeout_seconds} seconds"}
                    logging.warning(f"Attempt {attempt + 1} timed out. Retrying...")
                    time.sleep(0.1 * (attempt + 1))

                except Exception as e:
                    if attempt == max_retries - 1:  # Last attempt
                        logging.error(
                            f"Failed after {max_retries} attempts. Final error: {str(e)}"
                        )
                        return {"error": str(e)}

                    logging.warning(
                        f"Attempt {attempt + 1} failed: {str(e)}. Retrying..."
                    )
                    time.sleep(0.1 * (attempt + 1))  # Exponential backoff

            return {"error": "Max retries reached"}

        return wrapper

    return decorator
