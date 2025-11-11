import asyncio

from tasks.token_watcher_task.token_watcher import TokenWatcher

watch = TokenWatcher()

async def main():
    await watch.watch_transfers()

asyncio.run(main())
