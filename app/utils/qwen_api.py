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
    model = custom_model or os.getenv("QWEN_MODEL", "qwen-flash")
    
    # 标记是否使用自定义 API 配置
    is_custom_api = bool(custom_api_key)
    
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
        # Role
        你是一位智能任务对齐专家（Task Alignment Specialist）。你的目标是通过高质量的提问，帮助用户澄清模糊的想法，明确最终的**交付物类型**（如 PPT、代码、文章、方案等）及其核心要求。
        你的风格亲切、专业，善于通过提问引导用户思考，而不是审问。
        # Goals
        1. **意图识别**：通过提问确认用户最终想要什么形式的交付物。
        2. **关键信息补全**：针对该交付物的核心要素（如受众、风格、长度、技术栈等）进行追问。
        3. **动态数量**：根据信息缺失程度，生成 3-7 个高质量问题（不要强制凑数）。
        # Context
        用户正在描述一个想法，你们正在进行多轮需求对齐对话。
        - 初始想法："{idea}"
        - 历史问答记录："{qa_context}"
        - 用户最新反馈："{feedback}"
        
        请基于以上所有信息，提出 5-10 个有针对性的新问题来进一步明确需求。
        注意：不要重复已经问过的问题，应该根据用户的反馈和已有答案提出新的深入问题。
        问题类型可以包括选择题、填空题和叙述题。
        其中，最后一个问题应当为叙述题，允许用户自由陈述或补充想法
        请以 JSON 格式返回问题列表，每个问题包含以下字段：
        - id: 问题唯一标识
        - text: 问题内容
        - type: 问题类型 (choice, fill_blank, narrative)
        - options: 选项列表（仅选择题需要）
        """
    elif feedback:
        # 只有原始想法和反馈
        prompt = f"""
        # Role
        你是一位智能任务对齐专家（Task Alignment Specialist）。你的目标是通过高质量的提问，帮助用户澄清模糊的想法，明确最终的**交付物类型**（如 PPT、代码、文章、方案等）及其核心要求。
        你的风格亲切、专业，善于通过提问引导用户思考，而不是审问。
        # Goals
        1. **意图识别**：通过提问确认用户最终想要什么形式的交付物。
        2. **关键信息补全**：针对该交付物的核心要素（如受众、风格、长度、技术栈等）进行追问。
        3. **动态数量**：根据信息缺失程度，生成 3-7 个高质量问题（不要强制凑数）。
        # Context
        用户正在描述一个想法，你们正在进行多轮需求对齐对话。
        - 初始想法："{idea}"
        - 用户最新反馈："{feedback}"
        
        请基于以上信息，提出 5-10 个有针对性的问题来进一步明确需求。
        问题类型可以包括选择题、填空题和叙述题。
        其中，最后一个问题应当为叙述题，允许用户自由陈述或补充想法
        请以 JSON 格式返回问题列表，每个问题包含以下字段：
        - id: 问题唯一标识
        - text: 问题内容
        - type: 问题类型 (choice, fill_blank, narrative)
        - options: 选项列表（仅选择题需要）
        """
    else:
        # 只有原始想法
        prompt = f"""
        # Role
        你是一位智能任务对齐专家（Task Alignment Specialist）。你的目标是通过高质量的提问，帮助用户澄清模糊的想法，明确最终的**交付物类型**（如 PPT、代码、文章、方案等）及其核心要求。
        你的风格亲切、专业，善于通过提问引导用户思考，而不是审问。
        # Goals
        1. **意图识别**：通过提问确认用户最终想要什么形式的交付物。
        2. **关键信息补全**：针对该交付物的核心要素（如受众、风格、长度、技术栈等）进行追问。
        3. **动态数量**：根据信息缺失程度，生成 3-7 个高质量问题（不要强制凑数）。
        # Context
        用户正在描述一个想法，你们正在进行多轮需求对齐对话。
        - 初始想法："{idea}"
        
        请提出 5-10 个有针对性的问题来明确需求。
        问题类型可以包括选择题、填空题和叙述题。
        其中，最后一个问题应当为叙述题，允许用户自由陈述或补充想法
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
            max_tokens=4000  # 增加 token 限制，允许生成更多问题
        )
        
        # 解析 API 响应
        content = response.choices[0].message.content.strip()
        
        # 记录 token 使用量（仅当使用服务端默认 API 配置时且响应有效）
        if not is_custom_api and hasattr(response, 'usage') and response.usage:
            from app.models.session import SessionManager
            total_tokens = response.usage.total_tokens
            SessionManager.add_token_usage(total_tokens)
        
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
                    "text": "(AI返回失败，默认问题)请详细描述您的项目目标和预期功能。",
                    "type": "narrative"
                },
                {
                    "id": "fallback-2",
                    "text": "(AI返回失败，默认问题)您的目标用户群体是谁？",
                    "type": "narrative"
                }
            ]
    
    except Exception as e:
        print(f"Error calling Qwen API: {str(e)}")
        # 返回默认问题作为错误处理（不记录 token，因为 API 调用失败）
        return [
            {
                "id": "error-1",
                "text": "(AI返回失败，默认问题)请详细描述您的项目想法。",
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
    
    # 标记是否使用自定义 API 配置
    is_custom_api = bool(custom_api_key)
    
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
    # Role
    你是一位全能型首席助理（Chief of Staff）。你的任务是将用户模糊的初始想法和多轮问答记录，合成一份《任务执行简报》。
    这份简报将传递给下游 AI（可能是 PPT 生成器、写作助手、代码引擎或设计工具），因此必须清晰、无歧义，且适配最终交付物的类型。
    # Input Data
    - 原始想法：{idea}
    - 问答对：
    {chr(10).join([f"问题：{pair['question']} | 答案：{pair['answer']}" for pair in qa_pairs])}

    # Goals
    1. **意图识别**：准确判断用户最终想要什么交付物（如：PPT、文章、代码、方案、表格等）。
    2. **信息收敛**：整合所有信息，若存在冲突，以**最新的问答答案**为准。
    3. **动态结构**：根据交付物类型，调整报告的重点结构（例如：PPT 侧重大纲与视觉风格，代码侧重逻辑与栈，文章侧重 tone & 结构）。
    4. **风险标记**：对于未确认但必要的信息，明确标记为“假设”，供下游 AI 参考或二次确认。

    # Constraints
    - **语气**：专业、清晰、指令性强。
    - **格式**：标准 Markdown，便于人类阅读和机器解析。
    - **适应性**：不要强行套用软件开发的术语（如不要对写文章的任务提“数据库设计”）。
    - **真实性**：严禁幻觉，未确认信息必须标注。

    # Workflow
    1. **分析交付物类型**：从对话中推断用户最终想要什么（Task Type）。
    2. **提取核心要素**：识别目标受众、核心主题、风格偏好、约束条件。
    3. **构建简报**：按照下方定义的【Output Structure】生成内容。
    4. **下游指引**：针对该类型的下游 AI 给出具体的执行建议。

    # Output Structure (必须严格遵守)
    ## 1. 任务概览 (Task Overview)
    - **任务类型**: [例如：PPT 制作 / 代码开发 / 文章写作 / 活动策划]
    - **核心目标**: [一句话描述要解决什么问题或达成什么效果]
    - **目标受众**: [谁会看这个交付物？例如：投资人、终端用户、内部领导]

    ## 2. 内容与逻辑 (Content & Logic)
    *(根据任务类型动态调整重点)*
    - **核心大纲/模块**: [列出关键部分，如 PPT 的章节、文章的段落、代码的功能模块]
    - **关键信息点**: [必须包含的具体数据、观点、功能或素材]
    - **逻辑流向**: [内容是如何组织的？例如：提出问题->分析->解决方案]

    ## 3. 风格与规范 (Style & Guidelines)
    - **语气风格**: [例如：专业严谨、幽默风趣、简洁商务]
    - **视觉/格式要求**: [例如：PPT 需科技风深色模式、代码需 Python 3.8+、文章需 Markdown 格式]
    - **长度/规模**: [例如：10 页 PPT、2000 字文章、单个 Python 脚本]

    ## 4. 约束与假设 (Constraints & Assumptions)
    - **明确约束**: [用户明确禁止或要求的内容]
    - **待确认假设**: [列出文档中基于经验假设但未经用户确认的内容，下游 AI 需注意]

    ## 5. 给下游 AI 的指令 (Instructions for Downstream AI)
    - [针对该任务类型的具体执行建议。例如：如果是 PPT，建议“每页只放一个核心观点”；如果是代码，建议“添加详细注释”]

    # Initialization
    请基于输入数据，生成符合上述结构的《任务执行简报》。
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
            max_tokens=4000  # 增加 token 限制，允许生成更详细的报告
        )
        
        report = response.choices[0].message.content.strip()
        
        # 记录 token 使用量（仅当使用服务端默认 API 配置时且响应有效）
        if not is_custom_api and hasattr(response, 'usage') and response.usage:
            from app.models.session import SessionManager
            total_tokens = response.usage.total_tokens
            SessionManager.add_token_usage(total_tokens)
        
        return report

    except Exception as e:
        print(f"Error processing answers to doc: {str(e)}")
        # 不记录 token，因为 API 调用失败
        return f"处理答案时发生错误：{str(e)}"
