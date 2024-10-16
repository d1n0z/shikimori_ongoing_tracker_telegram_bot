import asyncio
import logging
import time
import traceback

import scheduler
from bot import dp
from config import bot


def main():
    logging.info('0%   loading . . . . .')
    time.sleep(0.01)
    loop = asyncio.new_event_loop()
    loop.create_task(scheduler.run())
    loop.create_task(dp.start_polling(bot))
    logging.info('100% loading complete!!')
    loop.run_forever()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        main()
    except KeyboardInterrupt:
        logging.info('Bye-bye!')
    except Exception as e:
        logging.exception(traceback.format_exc())
