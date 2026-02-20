from flask import jsonify, request
from app.routes import bp
from app.utils.qwen_api import generate_questions, process_answers_to_doc
from app.utils.token_limit import check_token_limit
from app.models.session import SessionManager


@bp.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})


@bp.route('/api/generate-questions', methods=['POST'])
@check_token_limit
def api_generate_questions():
    """
    根据用户输入的想法生成问题
    """
    try:
        data = request.get_json()
        idea = data.get('idea', '')

        # 获取自定义 API 配置
        custom_config = data.get('custom_api') or {}
        custom_api_key = custom_config.get('api_key')
        custom_base_url = custom_config.get('base_url')
        custom_model = custom_config.get('model')

        if not idea:
            return jsonify({'error': '想法不能为空'}), 400

        # 生成唯一会话 ID
        session_id = SessionManager.create_session(idea)

        # 调用 Qwen API 生成问题
        questions = generate_questions(idea, custom_api_key=custom_api_key,
                                      custom_base_url=custom_base_url,
                                      custom_model=custom_model)

        # 保存问题到会话
        SessionManager.save_questions(session_id, questions)

        return jsonify({
            'session_id': session_id,
            'questions': questions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/submit-answers', methods=['POST'])
@check_token_limit
def api_submit_answers():
    """
    提交问题答案，生成阶段性报告
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id', '')
        answers = data.get('answers', [])

        # 获取自定义 API 配置
        custom_config = data.get('custom_api') or {}
        custom_api_key = custom_config.get('api_key')
        custom_base_url = custom_config.get('base_url')
        custom_model = custom_config.get('model')

        if not session_id or not answers:
            return jsonify({'error': '会话 ID 和答案不能为空'}), 400

        # 获取会话信息
        session_data = SessionManager.get_session(session_id)
        if not session_data:
            return jsonify({'error': '无效的会话 ID'}), 400

        # 使用所有历史问题和答案（包括之前轮次的）
        all_questions = session_data['questions']
        all_answers = session_data['answers'] + answers  # 合并历史答案和新答案

        # 生成阶段性报告（基于所有历史问答）
        report = process_answers_to_doc(session_data['idea'], all_questions, all_answers,
                                       custom_api_key=custom_api_key,
                                       custom_base_url=custom_base_url,
                                       custom_model=custom_model)

        # 更新会话数据
        SessionManager.update_session_with_answers(session_id, answers, report)

        return jsonify({
            'session_id': session_id,
            'report': report
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/generate-pdf', methods=['POST'])
def api_generate_pdf():
    """
    生成最终 PDF 文档
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id', '')

        if not session_id:
            return jsonify({'error': '会话 ID 不能为空'}), 400

        # 获取会话信息
        session_data = SessionManager.get_session(session_id)
        if not session_data:
            return jsonify({'error': '无效的会话 ID'}), 400

        # 生成 PDF 文档
        pdf_path = SessionManager.generate_pdf_report(session_id)

        return jsonify({
            'session_id': session_id,
            'pdf_url': f'/api/download-pdf/{session_id}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/session/<session_id>', methods=['GET'])
def api_get_session_data(session_id):
    """
    获取会话数据（包括问题）
    """
    try:
        # 获取会话信息
        session_data = SessionManager.get_session(session_id)
        if not session_data:
            return jsonify({'error': '无效的会话 ID'}), 400

        return jsonify({
            'session_id': session_id,
            'idea': session_data['idea'],
            'questions': session_data['questions'],
            'answers': session_data['answers'],
            'reports': session_data['reports']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/continue-with-feedback', methods=['POST'])
@check_token_limit
def api_continue_with_feedback():
    """
    用户提供反馈后继续生成新问题
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id', '')
        feedback = data.get('feedback', '')

        # 获取自定义 API 配置
        custom_config = data.get('custom_api') or {}
        custom_api_key = custom_config.get('api_key')
        custom_base_url = custom_config.get('base_url')
        custom_model = custom_config.get('model')

        if not session_id or not feedback:
            return jsonify({'error': '会话 ID 和反馈不能为空'}), 400

        # 获取会话信息
        session_data = SessionManager.get_session(session_id)
        if not session_data:
            return jsonify({'error': '无效的会话 ID'}), 400

        # 基于原始想法、已有问答和用户反馈生成新问题
        new_questions = generate_questions(session_data['idea'], session_data['questions'],
                                          session_data['answers'], feedback,
                                          custom_api_key=custom_api_key,
                                          custom_base_url=custom_base_url,
                                          custom_model=custom_model)

        # 替换会话中的问题（而不是追加）
        SessionManager.replace_questions(session_id, new_questions)

        return jsonify({
            'session_id': session_id,
            'questions': new_questions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/download-pdf/<session_id>', methods=['GET'])
def api_download_pdf(session_id):
    """
    下载报告（现在是 Markdown 格式）
    """
    try:
        # 获取会话信息
        session_data = SessionManager.get_session(session_id)
        if not session_data:
            return "未找到会话", 404

        # 如果没有文档，生成一个
        if not session_data.get('final_doc'):
            from flask import send_file
            import os
            # 创建输出目录
            output_dir = "output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # 生成 Markdown 文件
            filename = f"requirement_document_{session_id[:8]}.md"
            filepath = os.path.join(output_dir, filename)

            from app.utils.markdown_generator import generate_markdown
            generate_markdown(session_data, filepath)

            # 在数据库中记录文件路径
            import sqlite3
            conn = sqlite3.connect(SessionManager.DB_PATH)
            cursor = conn.cursor()

            from datetime import datetime
            updated_at = datetime.now().isoformat()
            cursor.execute("""
                UPDATE sessions
                SET final_doc_path = ?, updated_at = ?
                WHERE id = ?
            """, (filepath, updated_at, session_id))

            conn.commit()
            conn.close()
        else:
            filepath = session_data['final_doc']

        from flask import send_file
        import os
        if not os.path.exists(filepath):
            return "文件不存在", 404

        # 确定正确的文件扩展名
        file_ext = os.path.splitext(filepath)[1]
        download_name = f"requirement_document_{session_id[:8]}{file_ext}"

        return send_file(filepath, as_attachment=True, download_name=download_name)
    except Exception as e:
        return str(e), 500


@bp.route('/api/session/<session_id>', methods=['DELETE'])
def api_delete_session(session_id):
    """
    删除会话
    """
    try:
        # 获取会话信息
        session_data = SessionManager.get_session(session_id)
        if not session_data:
            return jsonify({'error': '无效的会话 ID'}), 404

        # 删除会话
        SessionManager.delete_session(session_id)

        return jsonify({
            'message': '删除成功'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
