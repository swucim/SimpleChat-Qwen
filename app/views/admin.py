from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.services import UserService, api_service
from app.models import Config
import logging

admin = Blueprint('admin', __name__)

@admin.route('/login', methods=['GET', 'POST'])
def login():
    """管理员登录"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('用户名和密码不能为空', 'error')
            return render_template('admin/login.html')
        
        user = UserService.authenticate_admin(username, password)
        if user:
            login_user(user)
            flash('登录成功', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('用户名或密码错误', 'error')
    
    return render_template('admin/login.html')

@admin.route('/logout')
@login_required
def logout():
    """管理员退出登录"""
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('main.index'))

@admin.route('/dashboard')
@login_required
def dashboard():
    """管理员仪表板"""
    if not current_user.is_admin:
        flash('无权限访问', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # 获取统计数据
        user_stats = UserService.get_user_stats()
        conversation_stats = UserService.get_conversation_stats()
        recent_activities = UserService.get_recent_activities(10)
        
        return render_template('admin/dashboard.html',
                             user_stats=user_stats,
                             conversation_stats=conversation_stats,
                             recent_activities=recent_activities)
    except Exception as e:
        logging.error(f"获取仪表板数据失败: {str(e)}")
        flash('获取数据失败', 'error')
        return render_template('admin/dashboard.html',
                             user_stats={},
                             conversation_stats={},
                             recent_activities=[])

@admin.route('/users')
@login_required
def users():
    """用户管理"""
    if not current_user.is_admin:
        flash('无权限访问', 'error')
        return redirect(url_for('main.index'))
    
    try:
        page = request.args.get('page', 1, type=int)
        users = UserService.get_all_users(page=page, per_page=20)
        
        return render_template('admin/users.html', users=users)
    except Exception as e:
        logging.error(f"获取用户列表失败: {str(e)}")
        flash('获取用户列表失败', 'error')
        return render_template('admin/users.html', users=None)

@admin.route('/conversations')
@login_required
def conversations():
    """对话记录管理"""
    if not current_user.is_admin:
        flash('无权限访问', 'error')
        return redirect(url_for('main.index'))
    
    try:
        page = request.args.get('page', 1, type=int)
        user_id = request.args.get('user_id', type=int)
        
        if user_id:
            conversations = UserService.get_user_conversations(user_id, page=page, per_page=20)
        else:
            conversations = UserService.get_all_conversations(page=page, per_page=20)
        
        return render_template('admin/conversations.html', 
                             conversations=conversations, 
                             selected_user_id=user_id)
    except Exception as e:
        logging.error(f"获取对话记录失败: {str(e)}")
        flash('获取对话记录失败', 'error')
        return render_template('admin/conversations.html', 
                             conversations=None, 
                             selected_user_id=None)

@admin.route('/config', methods=['GET', 'POST'])
@login_required
def config():
    """系统配置"""
    if not current_user.is_admin:
        flash('无权限访问', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            api_url = request.form.get('api_url', '').strip()
            api_key = request.form.get('api_key', '').strip()
            model = request.form.get('model', '').strip()
            
            if not api_url or not api_key or not model:
                flash('所有字段都必须填写', 'error')
                return redirect(url_for('admin.config'))
            
            # 测试API连接
            test_result = api_service.test_connection(api_url, api_key, model)
            
            if test_result['success']:
                # 保存配置
                Config.set_openai_config(api_url, api_key, model)
                flash('配置保存成功', 'success')
            else:
                flash(f'配置测试失败: {test_result["message"]}', 'error')
                
        except Exception as e:
            logging.error(f"保存配置失败: {str(e)}")
            flash('保存配置失败', 'error')
    
    try:
        # 获取当前配置
        current_config = Config.get_openai_config()
        return render_template('admin/config.html', config=current_config)
    except Exception as e:
        logging.error(f"获取配置失败: {str(e)}")
        flash('获取配置失败', 'error')
        return render_template('admin/config.html', config={})

@admin.route('/test-api', methods=['POST'])
@login_required
def test_api():
    """测试API连接"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': '无权限访问'}), 403
    
    try:
        data = request.get_json()
        api_url = data.get('api_url', '').strip()
        api_key = data.get('api_key', '').strip()
        model = data.get('model', '').strip()
        
        if not api_url or not api_key or not model:
            return jsonify({
                'success': False,
                'message': '所有字段都必须填写'
            })
        
        # 测试连接
        result = api_service.test_connection(api_url, api_key, model)
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"API测试失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'测试失败: {str(e)}'
        })

@admin.route('/conversation/<int:conversation_id>')
@login_required
def view_conversation(conversation_id):
    """查看对话详情"""
    if not current_user.is_admin:
        flash('无权限访问', 'error')
        return redirect(url_for('main.index'))
    
    try:
        from app.services import ChatService
        conversation_detail = ChatService.get_conversation_detail(conversation_id)
        
        if not conversation_detail:
            flash('对话不存在', 'error')
            return redirect(url_for('admin.conversations'))
        
        return render_template('admin/conversation_detail.html', 
                             conversation=conversation_detail['conversation'],
                             messages=conversation_detail['messages'])
    except Exception as e:
        logging.error(f"获取对话详情失败: {str(e)}")
        flash('获取对话详情失败', 'error')
        return redirect(url_for('admin.conversations'))