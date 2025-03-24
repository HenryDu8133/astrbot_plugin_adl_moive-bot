from nonebot.adapters.onebot.v11 import Bot
import logging
from .config import plugin_config
from .models import db

async def check_reminders(bot: Bot):
    """检查提醒时间并发送提醒消息"""
    try:
        # 检查 30 分钟提醒
        reminders_30 = db.get_pending_reminders(30)
        for movie_name, user_id in reminders_30:
            await bot.send_group_msg(
                group_id=plugin_config.movie_group_id,
                message=f"@{user_id} 您预订的《{movie_name}》将在30分钟后开始，请准备入场！"
            )
            db.update_order_status(user_id, 'notified_30')
        
        # 检查 10 分钟提醒
        reminders_10 = db.get_pending_reminders(10)
        for movie_name, user_id in reminders_10:
            await bot.send_group_msg(
                group_id=plugin_config.movie_group_id,
                message=f"@{user_id} 您预订的《{movie_name}》将在10分钟后开始，请尽快入场！"
            )
            db.update_order_status(user_id, 'notified_10')
            
    except Exception as e:
        logging.error(f"提醒任务出错：{str(e)}")