import sqlite3
import json
from datetime import datetime

DB_PATH = "clarity_ai.db"

def test_rounds_logic():
    """测试轮次数据保存逻辑"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取最新的会话
    cursor.execute("SELECT id FROM sessions ORDER BY created_at DESC LIMIT 1")
    session_id = cursor.fetchone()[0]
    
    print(f"测试会话 ID: {session_id}")
    
    # 获取该会话的轮次数据
    cursor.execute("""
        SELECT round_number, questions, answers, report, created_at 
        FROM rounds 
        WHERE session_id = ? 
        ORDER BY round_number ASC
    """, (session_id,))
    
    rounds = cursor.fetchall()
    print(f"\n轮次数量：{len(rounds)}")
    
    for round_data in rounds:
        round_num = round_data[0]
        questions = json.loads(round_data[1])
        answers = json.loads(round_data[2])
        
        print(f"\n第 {round_num} 轮:")
        print(f"  问题数量：{len(questions)}")
        print(f"  答案数量：{len(answers)}")
        
        # 检查问题和答案数量是否匹配
        if len(questions) != len(answers):
            print(f"  ⚠️  警告：问题数量 ({len(questions)}) 不等于答案数量 ({len(answers)})")
        else:
            print(f"  ✅ 问题和答案数量匹配")
    
    conn.close()
    return len(rounds)

if __name__ == "__main__":
    count = test_rounds_logic()
    print(f"\n总轮次数：{count}")
