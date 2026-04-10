"""
数据库初始化脚本
"""
import asyncio
import sqlite3
from datetime import datetime

DATABASE_URL = "./videocraft.db"


def init_database():
    """初始化 SQLite 数据库"""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            avatar VARCHAR(255) DEFAULT '',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建任务表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id VARCHAR(64) UNIQUE NOT NULL,
            task_type VARCHAR(20) NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            model VARCHAR(100) NOT NULL,
            prompt TEXT NOT NULL,
            negative_prompt TEXT DEFAULT '',
            mode VARCHAR(20) DEFAULT 'text2image',
            ratio VARCHAR(10) DEFAULT '1:1',
            resolution VARCHAR(20) DEFAULT '1024',
            duration INTEGER DEFAULT 5,
            num INTEGER DEFAULT 1,
            with_audio BOOLEAN DEFAULT 0,
            input_image_url TEXT DEFAULT '',
            output_urls TEXT DEFAULT '',
            error_message TEXT DEFAULT '',
            processing_time REAL DEFAULT 0,
            cost REAL DEFAULT 0,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # 创建索引
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_task_id ON tasks(task_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at)
    """)
    
    # 插入测试用户（密码: test123）
    # 密码使用 bcrypt 哈希: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ/I1O
    cursor.execute("""
        INSERT OR IGNORE INTO users (id, username, email, hashed_password, is_active)
        VALUES (1, 'test', 'test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ/I1O', 1)
    """)
    
    conn.commit()
    conn.close()
    
    print(f"[OK] Database initialized: {DATABASE_URL}")


if __name__ == "__main__":
    init_database()
