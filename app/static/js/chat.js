// SimpleChat 前端JavaScript

class SimpleChat {
    constructor() {
        this.currentConversationId = null;
        this.isLoading = false;
        this.initializeApp();
    }

    initializeApp() {
        this.loadConversations();
        this.setupEventListeners();
        this.setupAutoResize();
    }

    setupEventListeners() {
        // 新建对话按钮
        const newChatBtn = document.getElementById('newChatBtn');
        if (newChatBtn) {
            newChatBtn.addEventListener('click', () => this.createNewConversation());
        }

        // 发送消息按钮
        const sendBtn = document.getElementById('sendBtn');
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }

        // 输入框回车发送
        const messageInput = document.getElementById('messageInput');
        if (messageInput) {
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
    }

    setupAutoResize() {
        const messageInput = document.getElementById('messageInput');
        if (messageInput) {
            messageInput.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 120) + 'px';
            });
        }
    }

    async loadConversations() {
        try {
            const response = await fetch('/api/chat/conversations');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.renderConversations(data.conversations);
                
                // 如果有对话，加载第一个
                if (data.conversations.length > 0 && !this.currentConversationId) {
                    this.loadConversation(data.conversations[0].id);
                }
            } else {
                console.error('获取对话列表失败:', data.error);
                this.showError(data.error || '获取对话列表失败');
            }
        } catch (error) {
            console.error('加载对话列表失败:', error);
            this.showError('网络错误，请检查网络连接');
        }
    }

    renderConversations(conversations) {
        const conversationList = document.getElementById('conversationList');
        if (!conversationList) return;

        conversationList.innerHTML = '';

        conversations.forEach(conv => {
            const item = document.createElement('div');
            item.className = 'conversation-item';
            item.dataset.conversationId = conv.id;
            
            item.innerHTML = `
                <div class="conversation-title">${this.escapeHtml(conv.title)}</div>
                <div class="conversation-time">${this.formatTime(conv.last_message_time)}</div>
            `;
            
            item.addEventListener('click', () => {
                this.loadConversation(conv.id);
            });
            
            conversationList.appendChild(item);
        });
    }

    async createNewConversation() {
        try {
            const response = await fetch('/api/chat/new', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                await this.loadConversations();
                this.loadConversation(data.conversation_id);
            } else {
                this.showError('创建新对话失败');
            }
        } catch (error) {
            console.error('创建新对话失败:', error);
            this.showError('创建新对话失败');
        }
    }

    async loadConversation(conversationId) {
        try {
            // 更新当前对话ID
            this.currentConversationId = conversationId;
            
            // 更新选中状态
            document.querySelectorAll('.conversation-item').forEach(item => {
                item.classList.remove('active');
            });
            
            const currentItem = document.querySelector(`[data-conversation-id="${conversationId}"]`);
            if (currentItem) {
                currentItem.classList.add('active');
            }
            
            // 加载消息
            const response = await fetch(`/api/chat/messages/${conversationId}`);
            const data = await response.json();
            
            if (data.success) {
                this.renderMessages(data.messages);
                
                // 更新对话标题
                const chatTitle = document.getElementById('chatTitle');
                if (chatTitle && data.conversation) {
                    chatTitle.textContent = data.conversation.title;
                }
            }
        } catch (error) {
            console.error('加载对话失败:', error);
        }
    }

    renderMessages(messages) {
        const messagesContainer = document.getElementById('chatMessages');
        if (!messagesContainer) return;

        messagesContainer.innerHTML = '';

        messages.forEach(message => {
            const messageDiv = this.createMessageElement(message);
            messagesContainer.appendChild(messageDiv);
        });

        this.scrollToBottom();
    }

    createMessageElement(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.role}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = message.role === 'user' ? 'U' : 'AI';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        content.innerHTML = this.formatMessageContent(message.content);
        
        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = this.formatTime(message.created_at);
        
        content.appendChild(time);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        return messageDiv;
    }

    async sendMessage() {
        if (this.isLoading) return;
        
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        
        if (!messageInput || !sendBtn) return;
        
        const message = messageInput.value.trim();
        if (!message) return;
        
        if (!this.currentConversationId) {
            // 如果没有当前对话，先创建一个
            await this.createNewConversation();
            if (!this.currentConversationId) {
                this.showError('无法创建对话');
                return;
            }
        }
        
        // 禁用输入和按钮
        this.isLoading = true;
        messageInput.disabled = true;
        sendBtn.disabled = true;
        sendBtn.textContent = '发送中...';
        
        // 清空输入框
        messageInput.value = '';
        messageInput.style.height = 'auto';
        
        // 显示用户消息
        this.addMessageToChat({
            role: 'user',
            content: message,
            created_at: new Date().toISOString()
        });
        
        // 显示加载状态
        this.showLoadingMessage();
        
        try {
            const response = await fetch('/api/chat/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    conversation_id: this.currentConversationId,
                    message: message
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // 移除加载消息
            this.removeLoadingMessage();
            
            if (data.success) {
                // 显示AI回复
                this.addMessageToChat(data.ai_message);
                
                // 刷新对话列表（标题可能已更新）
                await this.loadConversations();
            } else {
                this.showError(data.error || '发送消息失败');
            }
        } catch (error) {
            console.error('发送消息失败:', error);
            this.removeLoadingMessage();
            
            // 根据错误类型显示不同的提示
            if (error.message.includes('timeout') || error.message.includes('Timeout')) {
                this.showError('请求超时，请稍后重试');
            } else if (error.message.includes('Failed to fetch')) {
                this.showError('网络连接失败，请检查网络');
            } else {
                this.showError('发送消息失败，请重试');
            }
        } finally {
            // 恢复输入和按钮
            this.isLoading = false;
            messageInput.disabled = false;
            sendBtn.disabled = false;
            sendBtn.textContent = '发送';
            messageInput.focus();
        }
    }

    addMessageToChat(message) {
        const messagesContainer = document.getElementById('chatMessages');
        if (!messagesContainer) return;

        const messageElement = this.createMessageElement(message);
        messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }

    showLoadingMessage() {
        const messagesContainer = document.getElementById('chatMessages');
        if (!messagesContainer) return;

        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message assistant loading-message';
        loadingDiv.innerHTML = `
            <div class="message-avatar">AI</div>
            <div class="message-content">
                <div class="loading">
                    <span>正在思考</span>
                    <span class="loading-dots"></span>
                </div>
            </div>
        `;
        
        messagesContainer.appendChild(loadingDiv);
        this.scrollToBottom();
    }

    removeLoadingMessage() {
        const loadingMessage = document.querySelector('.loading-message');
        if (loadingMessage) {
            loadingMessage.remove();
        }
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chatMessages');
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    formatMessageContent(content) {
        // 简单的文本格式化，支持换行
        return this.escapeHtml(content).replace(/\n/g, '<br>');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        // 如果是今天
        if (date.toDateString() === now.toDateString()) {
            return date.toLocaleTimeString('zh-CN', {
                hour: '2-digit',
                minute: '2-digit'
            });
        }
        
        // 如果是昨天
        const yesterday = new Date(now);
        yesterday.setDate(yesterday.getDate() - 1);
        if (date.toDateString() === yesterday.toDateString()) {
            return '昨天 ' + date.toLocaleTimeString('zh-CN', {
                hour: '2-digit',
                minute: '2-digit'
            });
        }
        
        // 其他日期
        return date.toLocaleDateString('zh-CN', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    showError(message) {
        // 简单的错误提示
        alert(message);
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('chatApp')) {
        new SimpleChat();
    }
});