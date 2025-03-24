from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, Message
from nonebot.params import CommandArg
from nonebot.exception import FinishedException
import logging

from .models import db, OrderBase

# 电影排期查询命令
movie_schedule = on_command("排期", aliases={"电影排期", "今日排期"}, priority=5, block=True)

@movie_schedule.handle()
async def handle_schedule(event: MessageEvent):
    """查询今日电影排期"""
    try:
        movies = db.get_available_movies()
        
        if not movies:
            await movie_schedule.finish("❎今日暂无电影排期~")
            return
        
        msg = ["🎬 今日电影排期（有效时间5分钟）"]
        for movie in movies:
            msg.append(
                f"ID: {movie.id} 《{movie.name}》\n   时间：{movie.time}\n   余票：{movie.seats}张\n*✅请使用/订票 预定电影票"
            )
        
        await movie_schedule.finish("\n\n".join(msg))
        
    except FinishedException:
        pass
    except Exception as e:
        logging.error(f"排期查询失败：{str(e)}", exc_info=True)
        await movie_schedule.finish("❌查询排期失败，请检查数据库配置")

# 电影订票命令
book_movie = on_command("订票", aliases={"预约", "预订"}, priority=5, block=True)

@book_movie.handle()
async def handle_book(event: MessageEvent, args: Message = CommandArg()):
    """处理订票请求"""
    try:
        movie_id = args.extract_plain_text().strip()
        
        if not movie_id:
            await book_movie.finish("💡请使用 /订票 ID 的格式进行订票\n例：/订票 1")
            return
        
        if not movie_id.isdigit():
            await book_movie.finish("🔴请输入有效的数字 ID")
            return
        
        movie = db.get_movie_by_id(int(movie_id))
        if not movie:
            await book_movie.finish("🔴未找到对应的电影，请检查 ID")
            return
        
        if movie.seats <= 0:
            await book_movie.finish("🟡该场次已满座，请选择其他场次")
            return
        
        # 创建订单
        order = OrderBase(user_id=event.get_user_id(), movie_id=movie.id)
        if not db.create_order(order):
            await book_movie.finish("❌订票失败，请稍后重试")
            return
        
        await book_movie.finish(
            f"\n✅ 预订成功\n-—-—详细信息-—-—\n电影名称：《{movie.name}》\n场次时间：{movie.time}\n🟢座位已保留，请准时到场！🔆",
            at_sender=True
        )
        
    except Exception as e:
        logging.error(f"处理订票请求时出错：{str(e)}", exc_info=True)
        await book_movie.finish("❌订票失败，请联系管理员")