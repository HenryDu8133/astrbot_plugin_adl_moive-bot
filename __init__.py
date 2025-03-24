from nonebot import get_driver
from nonebot.plugin import PluginMetadata
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

from .config import plugin_config
from .models import db
from .handlers import movie_schedule, book_movie

__plugin_meta__ = PluginMetadata(
    name="电影订票插件",
    description="提供电影排期查询、订票和开场提醒功能",
    usage="发送 /排期 查看今日排期，发送 /订票 ID 进行订票",
    extra={
        "author": "Henry_Du",
        "version": "1.0.1",
    },
)

# 初始化定时任务
scheduler = AsyncIOScheduler()

# 获取驱动实例
driver = get_driver()

@driver.on_startup
async def startup():
    """插件启动时的初始化操作"""
    try:
        # 初始化数据库连接
        await db.init()  # 使用init()方法初始化数据库连接
        logging.info("数据库连接已初始化")
        
        # 获取机器人实例
        if not driver.bots:
            logging.error("未找到已连接的机器人实例")
            return
            
        bot = next(iter(driver.bots.values()))
        
        # 启动定时任务，每分钟检查一次提醒时间
        from .reminder import check_reminders
        scheduler.add_job(check_reminders, 'interval', minutes=1, args=[bot])
        if not scheduler.running:
            scheduler.start()
            logging.info("提醒任务已启动")
    except Exception as e:
        logging.error(f"启动失败：{str(e)}")

@driver.on_shutdown
async def shutdown():
    """插件关闭时的清理操作"""
    if scheduler.running:
        scheduler.shutdown()
        logging.info("提醒任务已停止")
    db.close()
    logging.info("数据库连接已关闭")