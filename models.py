from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import sqlite3
import os
from .config import plugin_config

class MovieBase(BaseModel):
    name: str
    time: str
    seats: int

class Movie(MovieBase):
    id: int
    reminder_30_time: Optional[str] = None
    reminder_10_time: Optional[str] = None

class OrderBase(BaseModel):
    user_id: str
    movie_id: int

class Order(OrderBase):
    id: int
    status: str = 'pending'

class MovieDB:
    def __init__(self):
        os.makedirs('data', exist_ok=True)
        self.conn = sqlite3.connect(plugin_config.movie_db_path)
        self._init_tables()
    
    def _init_tables(self):
        """初始化数据库表"""
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                time TEXT NOT NULL,
                seats INTEGER NOT NULL,
                reminder_30_time TEXT,
                reminder_10_time TEXT
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                movie_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY(movie_id) REFERENCES movies(id)
            )
        ''')
        self.conn.commit()
    
    def get_available_movies(self) -> List[Movie]:
        """获取所有可用的电影场次"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM movies WHERE datetime(time) > datetime('now', 'localtime')"
        )
        movies = cursor.fetchall()
        return [
            Movie(
                id=movie[0],
                name=movie[1],
                time=movie[2],
                seats=movie[3],
                reminder_30_time=movie[4],
                reminder_10_time=movie[5]
            )
            for movie in movies
        ]
    
    def get_movie_by_id(self, movie_id: int) -> Optional[Movie]:
        """根据ID获取电影信息"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
        movie = cursor.fetchone()
        if not movie:
            return None
        return Movie(
            id=movie[0],
            name=movie[1],
            time=movie[2],
            seats=movie[3],
            reminder_30_time=movie[4],
            reminder_10_time=movie[5]
        )
    
    def create_order(self, order: OrderBase) -> bool:
        """创建订单"""
        try:
            cursor = self.conn.cursor()
            # 检查座位是否可用
            cursor.execute(
                "SELECT seats FROM movies WHERE id = ?",
                (order.movie_id,)
            )
            seats = cursor.fetchone()
            if not seats or seats[0] <= 0:
                return False
            
            # 更新座位数并创建订单
            cursor.execute(
                "UPDATE movies SET seats = seats - 1 WHERE id = ?",
                (order.movie_id,)
            )
            cursor.execute(
                "INSERT INTO orders (user_id, movie_id) VALUES (?, ?)",
                (order.user_id, order.movie_id)
            )
            self.conn.commit()
            return True
        except Exception:
            return False
    
    def get_pending_reminders(self, minutes: int) -> List[tuple]:
        """获取待提醒的订单"""
        cursor = self.conn.cursor()
        status = 'pending' if minutes == 30 else 'notified_30'
        reminder_time = f'reminder_{minutes}_time'
        
        cursor.execute(f'''
            SELECT movies.name, orders.user_id 
            FROM movies 
            JOIN orders ON movies.id = orders.movie_id
            WHERE datetime(movies.{reminder_time}) <= datetime('now', 'localtime')
            AND orders.status = ?
        ''', (status,))
        return cursor.fetchall()
    
    def update_order_status(self, user_id: str, status: str):
        """更新订单状态"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE orders SET status = ? WHERE user_id = ?",
            (status, user_id)
        )
        self.conn.commit()
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()

# 全局数据库实例
db = MovieDB()