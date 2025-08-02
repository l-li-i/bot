from apscheduler.schedulers.asyncio import AsyncIOScheduler

def setup_scheduler(bot):
    scheduler = AsyncIOScheduler()
    return scheduler