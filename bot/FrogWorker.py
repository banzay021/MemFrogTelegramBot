import asyncio

from aiogram import types

#asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()

queue = asyncio.Queue(loop=loop)


async def add_mem_to_posting_queue(message):
    await queue.put(message)


async def get_mem_to_posting_from_queue():
    return await queue.get()


def mem_posted():
    queue.task_done()


def get_queue_size() -> int:
    return queue.qsize()
