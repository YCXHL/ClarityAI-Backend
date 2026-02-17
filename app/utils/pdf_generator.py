from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


def setup_chinese_font():
    """注册中文字体"""
    # 查找系统中的中文字体
    font_paths = [
        'C:/Windows/Fonts/simhei.ttf',  # 黑体
        'C:/Windows/Fonts/msyh.ttc',   # 微软雅黑
        'C:/Windows/Fonts/simsun.ttc', # 宋体
        'C:/Windows/Fonts/simkai.ttf', # 楷体
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            # 注册字体
            font_name = os.path.basename(font_path).split('.')[0]
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            return font_name
    
    # 如果找不到中文字体，返回None
    return None


def generate_pdf(session_data, filepath):
    """使用ReportLab生成PDF文档"""
    # 设置中文字体
    chinese_font = setup_chinese_font()
    
    # 创建文档
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    story = []
    
    # 获取样式
    styles = getSampleStyleSheet()
    
    # 定义中文字体样式
    if chinese_font:
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=chinese_font,
            fontSize=18,
            spaceAfter=30,
            alignment=1  # 居中
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName=chinese_font,
            fontSize=14,
            spaceAfter=12
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontName=chinese_font,
            fontSize=12,
            spaceAfter=12,
            leading=16
        )
    else:
        # 如果没有中文字体，使用默认样式
        title_style = styles['Title']
        heading_style = styles['Heading2']
        normal_style = styles['Normal']
    
    # 添加标题
    title = Paragraph("项目需求说明书", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # 添加原始想法
    idea_heading = Paragraph("1. 项目原始想法", heading_style)
    story.append(idea_heading)
    
    # 确保idea不为空
    idea_text = session_data.get('idea', '未提供项目想法')
    idea_content = Paragraph(idea_text, normal_style)
    story.append(idea_content)
    story.append(Spacer(1, 20))
    
    # 添加问答内容（只有在有数据时才添加）
    if session_data.get('questions') and session_data.get('answers'):
        qa_heading = Paragraph("2. 需求澄清问答", heading_style)
        story.append(qa_heading)
        
        # 确保问题和答案数量匹配
        min_len = min(len(session_data['questions']), len(session_data['answers']))
        for i in range(min_len):
            q = session_data['questions'][i]
            a = session_data['answers'][i]
            
            question_text = f"Q{i+1}: {q.get('text', '') if isinstance(q, dict) else str(q)}"
            question_para = Paragraph(question_text, normal_style)
            story.append(question_para)
            
            answer_text = f"A{i+1}: {a.get('answer', '') if isinstance(a, dict) else str(a)}"
            answer_para = Paragraph(answer_text, normal_style)
            story.append(answer_para)
            story.append(Spacer(1, 12))
        
        story.append(Spacer(1, 20))
    
    # 添加分析报告
    if session_data.get('reports'):
        report_heading = Paragraph("3. 阶段性分析报告", heading_style)
        story.append(report_heading)
        
        for i, report in enumerate(session_data['reports'], 1):
            report_title = Paragraph(f"第{i}次分析:", heading_style)
            story.append(report_title)
            
            report_content = Paragraph(str(report), normal_style)
            story.append(report_content)
            story.append(Spacer(1, 20))
    
    # 如果没有任何内容，添加默认内容
    if len(story) <= 2:  # 只有标题和间距
        empty_content = Paragraph("暂无内容", normal_style)
        story.append(empty_content)
    
    # 构建PDF
    doc.build(story)