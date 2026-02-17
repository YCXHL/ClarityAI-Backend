import os
import sys
import sqlite3
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from app.models.session import SessionManager

# 测试会话管理
print("测试会话管理...")

# 创建一个测试会话
idea = "测试想法"
session_id = SessionManager.create_session(idea)
print(f"创建会话: {session_id}")

# 获取会话数据
session_data = SessionManager.get_session(session_id)
print(f"获取会话数据: {session_data}")

# 添加测试问题和答案
test_questions = [
    {'id': 'q1', 'text': '这是第一个问题', 'type': 'narrative'},
    {'id': 'q2', 'text': '这是第二个问题', 'type': 'choice', 'options': ['选项A', '选项B']}
]
SessionManager.save_questions(session_id, test_questions)

# 添加测试答案
test_answers = [
    {'questionId': 'q1', 'answer': '这是第一个答案'},
    {'questionId': 'q2', 'answer': '选项A'}
]
SessionManager.update_session_with_answers(session_id, test_answers, "这是测试报告")

# 再次获取会话数据
updated_session = SessionManager.get_session(session_id)
print(f"更新后的会话数据: {updated_session}")

# 生成PDF
pdf_path = SessionManager.generate_pdf_report(session_id)
print(f"PDF生成路径: {pdf_path}")

if pdf_path and os.path.exists(pdf_path):
    size = os.path.getsize(pdf_path)
    print(f"PDF文件大小: {size} 字节")
    print("PDF文件存在且非空")
else:
    print("PDF文件不存在或为空")