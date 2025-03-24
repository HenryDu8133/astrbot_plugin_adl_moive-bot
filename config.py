from typing import Optional
from pydantic import BaseModel, Extra
from nonebot import get_driver

class Config(BaseModel, extra=Extra.ignore):
    # 插件基本配置
    movie_db_path: str = 'data/movies.db'
    movie_group_id: int = 663767163  # 电影通知群组ID
    
    # 提醒时间配置（分钟）
    reminder_before_start: list[int] = [30, 10]
    
    # 每页显示的电影数量
    movies_per_page: int = 5

# 全局配置
plugin_config = Config.parse_obj(get_driver().config)