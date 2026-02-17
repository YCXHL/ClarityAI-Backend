import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from app.utils.pdf_generator import generate_pdf

# 创建测试数据
test_session_data = {
    'idea': '这是一个测试想法',
    'questions': [
        {'text': '这是第一个问题', 'type': 'narrative'},
        {'text': '这是第二个问题', 'type': 'choice'}
    ],
    'answers': [
        {'answer': '这是第一个答案'},
        {'answer': '这是第二个答案'}
    ],
    'reports': ['这是分析报告内容']
}

# 生成PDF
output_path = 'test_output.pdf'
try:
    generate_pdf(test_session_data, output_path)
    print(f"PDF已成功生成: {output_path}")
    
    # 检查文件大小
    size = os.path.getsize(output_path)
    print(f"文件大小: {size} 字节")
    
    if size > 0:
        print("文件非空，生成成功")
    else:
        print("文件为空，生成失败")
        
except Exception as e:
    print(f"生成PDF时出错: {str(e)}")
    import traceback
    traceback.print_exc()