from flask import Blueprint, render_template, redirect, url_for

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """首页"""
    return render_template('index.html')

@main.route('/chat')
def chat():
    """聊天页面"""
    return render_template('chat.html')