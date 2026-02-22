import sqlite3
import json

DB_PATH = "clarity_ai.db"

def check_rounds_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取所有会话
    cursor.execute("SELECT id, idea FROM sessions")
    sessions = cursor.fetchall()
    
    print(f"找到 {len(sessions)} 个会话\n")
    
    for session_id, idea in sessions:
        print(f"会话 ID: {session_id[:8]}...")
        print(f"想法：{idea[:50]}...")
        
        # 获取该会话的轮次数据
        cursor.execute("""
            SELECT round_number, questions, answers, report, created_at 
            FROM rounds 
            WHERE session_id = ? 
            ORDER BY round_number ASC
        """, (session_id,))
        
        rounds = cursor.fetchall()
        print(f"轮次数量：{len(rounds)}")
        
        for round_data in rounds:
            round_num = round_data[0]
            questions = json.loads(round_data[1])
            answers = json.loads(round_data[2])
            report = round_data[3][:50] if round_data[3] else "None"
            created_at = round_data[4]
            
            print(f"\n  第 {round_num} 轮:")
            print(f"    问题数量：{len(questions)}")
            print(f"    答案数量：{len(answers)}")
            print(f"    问题 1: {questions[0]['text'][:50] if questions else 'None'}...")
            print(f"    答案 1: {answers[0]['answer'][:50] if answers else 'None'}...")
            print(f"    报告：{report}...")
            print(f"    创建时间：{created_at}")
        
        print("\n" + "="*80 + "\n")
    
    conn.close()

if __name__ == "__main__":
    check_rounds_data()
