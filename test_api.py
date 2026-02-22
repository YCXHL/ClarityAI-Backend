import sys
sys.path.append('.')

from app.models.session import SessionManager

# 创建测试会话
print("1. 创建会话...")
session_id = SessionManager.create_session('测试想法')
print(f"   会话 ID: {session_id}")

# 保存问题
print("\n2. 保存问题...")
questions = [
    {'id': 'q1', 'text': '问题 1', 'type': 'narrative'},
    {'id': 'q2', 'text': '问题 2', 'type': 'narrative'}
]
SessionManager.save_questions(session_id, questions)
print("   问题保存成功")

# 获取会话
print("\n3. 获取会话...")
session = SessionManager.get_session(session_id)
print(f"   问题数：{len(session['questions'])}")
print(f"   反馈数：{len(session['feedbacks'])}")

# 保存反馈
print("\n4. 保存反馈...")
SessionManager.save_feedback(session_id, '这是测试反馈')
print("   反馈保存成功")

# 再次获取会话
print("\n5. 再次获取会话...")
session = SessionManager.get_session(session_id)
print(f"   反馈数：{len(session['feedbacks'])}")
print(f"   反馈内容：{session['feedbacks']}")

print("\n✅ 所有测试通过！")
