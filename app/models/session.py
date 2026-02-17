import uuid
import json
import os
import sqlite3
from datetime import datetime
from app.utils.markdown_generator import generate_markdown


class SessionManager:
    DB_PATH = "clarity_ai.db"
    
    @classmethod
    def init_db(cls):
        """初始化数据库"""
        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()
        
        # 创建会话表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                idea TEXT NOT NULL,
                created_at TEXT NOT NULL,
                questions TEXT DEFAULT '[]',
                answers TEXT DEFAULT '[]',
                reports TEXT DEFAULT '[]',
                final_doc_path TEXT,
                updated_at TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    @classmethod
    def create_session(cls, idea):
        """创建新会话"""
        cls.init_db()  # 确保数据库已初始化
        
        session_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        
        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sessions (id, idea, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        """, (session_id, idea, created_at, created_at))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    @classmethod
    def get_session(cls, session_id):
        """获取会话信息"""
        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        
        if row:
            # 解析JSON字段
            session = {
                'id': row[0],
                'idea': row[1],
                'created_at': row[2],
                'questions': json.loads(row[3]),
                'answers': json.loads(row[4]),
                'reports': json.loads(row[5]),
                'final_doc': row[6]
            }
            conn.close()
            return session
        else:
            conn.close()
            return None
    
    @classmethod
    def save_questions(cls, session_id, questions):
        """保存问题到会话"""
        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()
        
        questions_json = json.dumps(questions)
        updated_at = datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE sessions
            SET questions = ?, updated_at = ?
            WHERE id = ?
        """, (questions_json, updated_at, session_id))
        
        conn.commit()
        conn.close()
    
    @classmethod
    def update_session_with_answers(cls, session_id, answers, report):
        """更新会话中的答案和报告"""
        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()
        
        # 获取当前答案和报告
        cursor.execute("SELECT answers, reports FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        
        if row:
            current_answers = json.loads(row[0])
            current_reports = json.loads(row[1])
            
            # 添加新答案和报告
            current_answers.extend(answers)
            current_reports.append(report)
            
            # 更新数据库
            answers_json = json.dumps(current_answers)
            reports_json = json.dumps(current_reports)
            updated_at = datetime.now().isoformat()
            
            cursor.execute("""
                UPDATE sessions
                SET answers = ?, reports = ?, updated_at = ?
                WHERE id = ?
            """, (answers_json, reports_json, updated_at, session_id))
            
            conn.commit()
        conn.close()
    
    @classmethod
    def add_follow_up_questions(cls, session_id, new_questions):
        """添加后续问题"""
        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()
        
        # 获取当前问题
        cursor.execute("SELECT questions FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        
        if row:
            current_questions = json.loads(row[0])
            
            # 添加新问题
            current_questions.extend(new_questions)
            
            # 更新数据库
            questions_json = json.dumps(current_questions)
            updated_at = datetime.now().isoformat()
            
            cursor.execute("""
                UPDATE sessions
                SET questions = ?, updated_at = ?
                WHERE id = ?
            """, (questions_json, updated_at, session_id))
            
            conn.commit()
        conn.close()

    @classmethod
    def replace_questions(cls, session_id, new_questions):
        """替换会话中的问题（用于继续细化需求场景）"""
        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()

        # 更新问题列表
        questions_json = json.dumps(new_questions)
        updated_at = datetime.now().isoformat()

        cursor.execute("""
            UPDATE sessions
            SET questions = ?, updated_at = ?
            WHERE id = ?
        """, (questions_json, updated_at, session_id))

        conn.commit()
        conn.close()

    @classmethod
    def delete_session(cls, session_id):
        """删除会话"""
        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))

        conn.commit()
        conn.close()

    @classmethod
    def init_token_usage(cls):
        """初始化 token 使用记录表"""
        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS token_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                total_tokens INTEGER DEFAULT 0,
                updated_at TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    @classmethod
    def get_today_token_usage(cls):
        """获取今日 token 使用量"""
        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()

        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("SELECT total_tokens FROM token_usage WHERE date = ?", (today,))
        row = cursor.fetchone()

        conn.close()
        return row[0] if row else 0

    @classmethod
    def add_token_usage(cls, tokens):
        """增加 token 使用量"""
        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()

        today = datetime.now().strftime('%Y-%m-%d')
        updated_at = datetime.now().isoformat()

        # 检查今日记录是否存在
        cursor.execute("SELECT total_tokens FROM token_usage WHERE date = ?", (today,))
        row = cursor.fetchone()

        if row:
            # 更新现有记录
            new_total = row[0] + tokens
            cursor.execute("""
                UPDATE token_usage
                SET total_tokens = ?, updated_at = ?
                WHERE date = ?
            """, (new_total, updated_at, today))
        else:
            # 插入新记录
            cursor.execute("""
                INSERT INTO token_usage (date, total_tokens, updated_at)
                VALUES (?, ?, ?)
            """, (today, tokens, updated_at))

        conn.commit()
        conn.close()

    @classmethod
    def generate_pdf_report(cls, session_id):
        """生成Markdown报告（原方法名保持不变以避免修改其他地方）"""
        session = cls.get_session(session_id)
        if not session:
            return None

        # 创建输出目录
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 生成Markdown文件
        filename = f"requirement_document_{session_id[:8]}.md"
        filepath = os.path.join(output_dir, filename)

        generate_markdown(session, filepath)

        # 在数据库中记录文件路径
        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()

        updated_at = datetime.now().isoformat()
        cursor.execute("""
            UPDATE sessions
            SET final_doc_path = ?, updated_at = ?
            WHERE id = ?
        """, (filepath, updated_at, session_id))

        conn.commit()
        conn.close()

        return filepath