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
                <div class="conversation-content">
                    <div class="conversation-title">${this.escapeHtml(conv.title)}</div>
                    <div class="conversation-time">${this.formatTime(conv.last_message_time)}</div>
                </div>
                <button class="conversation-delete-btn" title="删除对话">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                        <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                </button>
            `;
            
            // 点击对话内容区域加载对话
            const conversationContent = item.querySelector('.conversation-content');
            conversationContent.addEventListener('click', () => {
                this.loadConversation(conv.id);
            });
            
            // 点击删除按钮
            const deleteBtn = item.querySelector('.conversation-delete-btn');
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation(); // 阻止事件冒泡
                this.deleteConversation(conv.id, conv.title);
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
        
        // 创建流式AI消息容器
        const streamingMessage = this.createStreamingMessageElement();
        const messagesContainer = document.getElementById('chatMessages');
        messagesContainer.appendChild(streamingMessage);
        this.scrollToBottom();
        
        const contentElement = streamingMessage.querySelector('.streaming-content');
        let streamCompleted = false;
        
        try {
            const response = await fetch('/api/chat/send-stream', {
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
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            
            while (true) {
                const { value, done } = await reader.read();
                
                if (done) {
                    streamCompleted = true;
                    break;
                }
                
                // 将新数据添加到缓冲区
                buffer += decoder.decode(value, { stream: true });
                
                // 按行分割处理
                const lines = buffer.split('\n');
                // 保留最后一个不完整的行
                buffer = lines.pop() || '';
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6).trim(); // 移除 'data: ' 前缀
                        
                        if (data === '[DONE]') {
                            streamCompleted = true;
                            break;
                        }
                        
                        if (data) {
                            try {
                                const eventData = JSON.parse(data);
                                this.handleStreamChunk(eventData, contentElement, streamingMessage);
                            } catch (e) {
                                console.warn('解析流式数据失败:', e, data);
                            }
                        }
                    }
                }
                
                if (streamCompleted) break;
            }
            
            // 确保流式完成后恢复状态
            if (streamCompleted) {
                this.restoreUIState();
            }
            
            // 刷新对话列表（标题可能已更新）
            await this.loadConversations();
            
        } catch (error) {
            console.error('发送消息失败:', error);
            
            // 移除流式消息元素
            if (streamingMessage && streamingMessage.parentNode) {
                streamingMessage.parentNode.removeChild(streamingMessage);
            }
            
            // 根据错误类型显示不同的提示
            if (error.message.includes('timeout') || error.message.includes('Timeout')) {
                this.showError('请求超时，请稍后重试');
            } else if (error.message.includes('Failed to fetch')) {
                this.showError('网络连接失败，请检查网络');
            } else {
                this.showError('发送消息失败，请重试');
            }
        } finally {
            // 确保恢复输入和按钮状态（作为备用机制）
            this.restoreUIState();
        }
    }

    addMessageToChat(message) {
        const messagesContainer = document.getElementById('chatMessages');
        if (!messagesContainer) return;

        const messageElement = this.createMessageElement(message);
        messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }
    
    createStreamingMessageElement() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant streaming';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = 'AI';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        const streamingContent = document.createElement('div');
        streamingContent.className = 'streaming-content';
        
        const cursor = document.createElement('span');
        cursor.className = 'streaming-cursor';
        cursor.textContent = '|';
        
        content.appendChild(streamingContent);
        content.appendChild(cursor);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        return messageDiv;
    }
    
    handleStreamChunk(chunk, contentElement, messageElement) {
        switch (chunk.type) {
            case 'user_message':
                // 用户消息已经在前面显示了，这里不需要处理
                break;
            case 'ai_start':
                // AI开始生成回复
                break;
            case 'ai_chunk':
                // 添加文本块
                if (chunk.content) {
                    contentElement.textContent += chunk.content;
                    this.scrollToBottom();
                }
                break;
            case 'ai_complete':
                // AI完成回复
                const cursor = messageElement.querySelector('.streaming-cursor');
                if (cursor) {
                    cursor.remove();
                }
                messageElement.classList.remove('streaming');
                
                // 添加时间戳
                const time = document.createElement('div');
                time.className = 'message-time';
                time.textContent = this.formatTime(chunk.message.created_at);
                contentElement.parentElement.appendChild(time);
                
                // 恢复界面状态
                this.restoreUIState();
                break;
            case 'error':
                // 处理错误
                console.error('流式错误:', chunk.error);
                if (messageElement && messageElement.parentNode) {
                    messageElement.parentNode.removeChild(messageElement);
                }
                this.showError(chunk.error);
                // 错误时也要恢复界面状态
                this.restoreUIState();
                break;
            default:
                console.warn('未知流式事件类型:', chunk.type);
        }
    }
    
    restoreUIState() {
        // 恢复输入和按钮状态
        this.isLoading = false;
        
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        
        if (messageInput) {
            messageInput.disabled = false;
            messageInput.focus();
        }
        
        if (sendBtn) {
            sendBtn.disabled = false;
            sendBtn.textContent = '发送';
        }
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

    async deleteConversation(conversationId, conversationTitle) {
        // 确认删除
        if (!confirm(`确定要删除对话 "${conversationTitle}" 吗？\n\n删除后将无法恢复。`)) {
            return;
        }
        
        try {
            const response = await fetch(`/api/chat/delete/${conversationId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                // 如果删除的是当前对话，清空聊天区域
                if (this.currentConversationId == conversationId) {
                    this.currentConversationId = null;
                    this.clearChatArea();
                }
                
                // 重新加载对话列表
                await this.loadConversations();
                
                // 简单的成功提示
                this.showSuccess('对话删除成功');
            } else {
                this.showError(data.error || '删除对话失败');
            }
            
        } catch (error) {
            console.error('删除对话失败:', error);
            this.showError('删除对话失败，请重试');
        }
    }
    
    clearChatArea() {
        const chatMessages = document.getElementById('chatMessages');
        const chatTitle = document.getElementById('chatTitle');
        
        if (chatMessages) {
            chatMessages.innerHTML = `
                <div class="welcome-message" style="text-align: center; padding: 2rem; color: #666;">
                    <h3>欢迎使用 SimpleChat</h3>
                    <p>选择一个对话开始聊天，或者创建一个新的对话。</p>
                </div>
            `;
        }
        
        if (chatTitle) {
            chatTitle.textContent = '选择或创建一个对话';
        }
    }
    
    showSuccess(message) {
        // 简单的成功提示
        const notification = document.createElement('div');
        notification.className = 'notification success';
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // 3秒后自动移除
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }

    showError(message) {
        // 简单的错误提示
        const notification = document.createElement('div');
        notification.className = 'notification error';
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // 3秒后自动移除
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('chatApp')) {
        new SimpleChat();
    }
});