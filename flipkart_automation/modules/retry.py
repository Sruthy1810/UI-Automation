import asyncio
from utils.logger import logger
from utils.screenshot import take_failure_screenshot


async def retry_async(
    function,
    *args,
    retries=3,
    delay=2,
    action_name="Action",
    **kwargs
):
    """
    Retry an async function when it fails.

    retries = number of retry attempts
    delay = delay between attempts in seconds
    """

    for attempt in range(1, retries + 1):

        try:
            logger.info(
                f"{action_name} - Attempt {attempt}/{retries}"
            )

            result = await function(*args, **kwargs)

            logger.info(
                f"{action_name} completed successfully."
            )

            return result

        except Exception as e:

            logger.error(
                f"{action_name} failed on attempt "
                f"{attempt}/{retries}: {e}"
            )

            # Screenshot of the page at this failed attempt
            # (page is the first argument of every action function)
            if args:
                await take_failure_screenshot(
                    args[0],
                    f"{action_name}_attempt{attempt}"
                )

            if attempt < retries:
                await asyncio.sleep(delay)

            else:
                logger.error(
                    f"{action_name} failed after "
                    f"{retries} attempts."
                )

                raise