import re

# 读取文件
with open('app/models/session.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 旧的 get_session 方法
old_code = """        if row:
            # 解析 JSON 字段
            session = {
                'id': row[0],
                'idea': row[1],
                'created_at': row[2],
                'questions': json.loads(row[3]),
                'answers': json.loads(row[4]),
                'reports': json.loads(row[5]),
                'feedbacks': json.loads(row[8]) if row[8] else [],
                'final_doc': row[6]
            }
            conn.close()
            return session"""

# 新的 get_session 方法
new_code = """        if row:
            # 使用列名获取数据，避免索引问题
            columns = [description[0] for description in cursor.description]
            data = dict(zip(columns, row))
            
            # 解析 JSON 字段
            session = {
                'id': data['id'],
                'idea': data['idea'],
                'created_at': data['created_at'],
                'questions': json.loads(data['questions']),
                'answers': json.loads(data['answers']),
                'reports': json.loads(data['reports']),
                'feedbacks': json.loads(data['feedbacks']) if data['feedbacks'] else [],
                'final_doc': data['final_doc_path']
            }
            conn.close()
            return session"""

# 替换
new_content = content.replace(old_code, new_code)

if content == new_content:
    print("替换失败：未找到匹配的代码")
else:
    with open('app/models/session.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("替换成功！")
