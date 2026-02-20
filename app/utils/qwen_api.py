import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建默认 OpenAI 客户端（这里使用 Qwen API 兼容的格式）
default_client = OpenAI(
    api_key=os.getenv("QWEN_API_KEY") or os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
)


def get_client(custom_api_key=None, custom_base_url=None):
    """获取 API 客户端，支持自定义配置"""
    if custom_api_key:
        return OpenAI(
            api_key=custom_api_key,
            base_url=custom_base_url or os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        )
    return default_client


def generate_questions(idea, questions_list=None, answers_list=None, feedback=None, 
                      custom_api_key=None, custom_base_url=None, custom_model=None):
    """
    使用 Qwen API 根据用户想法、已有问答和反馈生成问题
    """
    # 获取客户端
    client = get_client(custom_api_key, custom_base_url)
    
    # 获取模型
    model = custom_model or os.getenv("QWEN_MODEL", "qwen-max")
    
    # 构建提示词 - 检查是否有问答历史
    has_qa_history = questions_list and len(questions_list) > 0 and feedback
    
    if has_qa_history:
        # 包含原始想法、已有问答和用户反馈
        qa_pairs = []
        if answers_list and len(answers_list) > 0:
            min_len = min(len(questions_list), len(answers_list))
            for i in range(min_len):
                q = questions_list[i]
                a = answers_list[i]
                question_text = q.get('text', '') if isinstance(q, dict) else str(q)
                answer_text = a.get('answer', '') if isinstance(a, dict) else str(a)
                qa_pairs.append(f"问题：{question_text} | 答案：{answer_text}")
        
        qa_context = "\n".join(qa_pairs) if qa_pairs else "暂无已回答的问题"
        
        prompt = f"""
        用户最初的想法是："{idea}"
        
        已有的问答对：
        {qa_context}
        
        用户的补充反馈："{feedback}"
        
        请基于以上所有信息，提出 5-10 个有针对性的新问题来进一步明确需求。
        注意：不要重复已经问过的问题，应该根据用户的反馈和已有答案提出新的深入问题。
        问题类型可以包括选择题、填空题和叙述题。
        请以 JSON 格式返回问题列表，每个问题包含以下字段：
        - id: 问题唯一标识
        - text: 问题内容
        - type: 问题类型 (choice, fill_blank, narrative)
        - options: 选项列表（仅选择题需要）
        """
    elif feedback:
        # 只有原始想法和反馈
        prompt = f"""
        用户最初的想法是："{idea}"
        之前的分析报告或用户反馈："{feedback}"
        
        请基于以上信息，提出 5-10 个有针对性的问题来进一步明确需求。
        问题类型可以包括选择题、填空题和叙述题。
        请以 JSON 格式返回问题列表，每个问题包含以下字段：
        - id: 问题唯一标识
        - text: 问题内容
        - type: 问题类型 (choice, fill_blank, narrative)
        - options: 选项列表（仅选择题需要）
        """
    else:
        # 只有原始想法
        prompt = f"""
        用户的想法是："{idea}"
        
        请提出 5-10 个有针对性的问题来明确需求。
        问题类型可以包括选择题、填空题和叙述题。
        请以 JSON 格式返回问题列表，每个问题包含以下字段：
        - id: 问题唯一标识
        - text: 问题内容
        - type: 问题类型 (choice, fill_blank, narrative)
        - options: 选项列表（仅选择题需要）
        """
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # 记录 token 使用量
        if hasattr(response, 'usage') and response.usage:
            from app.models.session import SessionManager
            total_tokens = response.usage.total_tokens
            SessionManager.add_token_usage(total_tokens)
        
        # 解析 API 响应
        content = response.choices[0].message.content.strip()
        
        # 尝试提取 JSON 部分
        import re
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            import json as json_lib
            questions = json_lib.loads(json_match.group())
            return questions
        else:
            # 如果没有找到 JSON，返回默认问题作为备选
            return [
                {
                    "id": "fallback-1",
                    "text": "请详细描述您的项目目标和预期功能。",
                    "type": "narrative"
                },
                {
                    "id": "fallback-2",
                    "text": "您的目标用户群体是谁？",
                    "type": "narrative"
                }
            ]
    
    except Exception as e:
        print(f"Error calling Qwen API: {str(e)}")
        # 返回默认问题作为错误处理
        return [
            {
                "id": "error-1",
                "text": "请详细描述您的项目想法。",
                "type": "narrative"
            }
        ]


def process_answers_to_doc(idea, questions, answers, custom_api_key=None, custom_base_url=None, custom_model=None):
    """
    处理用户答案并生成阶段性报告
    """
    # 获取客户端
    client = get_client(custom_api_key, custom_base_url)
    
    # 获取模型
    model = custom_model or os.getenv("QWEN_MODEL", "qwen-max")
    
    # 创建问题和答案的映射
    qa_pairs = []
    for i, answer in enumerate(answers):
        if i < len(questions):
            qa_pairs.append({
                'question': questions[i]['text'],
                'answer': answer.get('answer', ''),
                'question_type': questions[i].get('type', 'narrative')
            })

    # 构建提示词让 AI 生成分析报告
    prompt = f"""
    原始想法：{idea}

    问答对：
    {chr(10).join([f"问题：{pair['question']} | 答案：{pair['answer']}" for pair in qa_pairs])}

    请基于以上问答对，生成一份结构化的阶段性需求分析报告。
    报告应包括：
    1. 项目概述
    2. 功能需求
    3. 非功能需求
    4. 目标用户
    5. 其他重要考虑因素
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            max_tokens=1500
        )
        
        # 记录 token 使用量
        if hasattr(response, 'usage') and response.usage:
            from app.models.session import SessionManager
            total_tokens = response.usage.total_tokens
            SessionManager.add_token_usage(total_tokens)
        
        report = response.choices[0].message.content.strip()
        return report

    except Exception as e:
        print(f"Error processing answers to doc: {str(e)}")
        return f"处理答案时发生错误：{str(e)}"
