// SmartSafety PPE检测系统JavaScript功能
// 来源: https://blog.csdn.net/QQ_1309399183/article/details/147738037

class SmartSafetyApp {
    constructor() {
        this.isStreaming = false;
        this.detectionStats = {
            total: 0,
            safe: 0,
            unsafe: 0,
            accuracy: 0
        };
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeCharts();
        this.startStatsUpdate();
        this.checkSystemStatus();
    }

    setupEventListeners() {
        // 开始/停止检测按钮
        const toggleBtn = document.getElementById('toggle-detection');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggleDetection());
        }

        // 手动截图按钮
        const screenshotBtn = document.getElementById('manual-screenshot');
        if (screenshotBtn) {
            screenshotBtn.addEventListener('click', () => this.takeScreenshot());
        }

        // 刷新统计数据按钮
        const refreshBtn = document.getElementById('refresh-stats');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshStats());
        }

        // 导出报告按钮
        const exportBtn = document.getElementById('export-report');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportReport());
        }

        // 设置按钮
        const settingsBtn = document.getElementById('settings-btn');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => this.openSettings());
        }

        // 响应式菜单切换
        const menuToggle = document.getElementById('menu-toggle');
        const mobileMenu = document.getElementById('mobile-menu');
        if (menuToggle && mobileMenu) {
            menuToggle.addEventListener('click', () => {
                mobileMenu.classList.toggle('hidden');
            });
        }
    }

    toggleDetection() {
        const btn = document.getElementById('toggle-detection');
        const status = document.getElementById('detection-status');
        
        if (this.isStreaming) {
            this.stopDetection();
            btn.innerHTML = '<i class="fas fa-play mr-2"></i>开始检测';
            btn.classList.remove('btn-error');
            btn.classList.add('btn-success');
            if (status) status.textContent = '检测已停止';
        } else {
            this.startDetection();
            btn.innerHTML = '<i class="fas fa-stop mr-2"></i>停止检测';
            btn.classList.remove('btn-success');
            btn.classList.add('btn-error');
            if (status) status.textContent = '正在检测...';
        }
        
        this.isStreaming = !this.isStreaming;
    }

    startDetection() {
        const videoFeed = document.getElementById('video-feed');
        if (videoFeed) {
            videoFeed.src = '/video_feed';
            videoFeed.style.display = 'block';
        }
        
        this.showNotification('检测已开始', 'success');
        this.updateDetectionStatus('active');
    }

    stopDetection() {
        const videoFeed = document.getElementById('video-feed');
        if (videoFeed) {
            videoFeed.src = '';
            videoFeed.style.display = 'none';
        }
        
        this.showNotification('检测已停止', 'info');
        this.updateDetectionStatus('inactive');
    }

    takeScreenshot() {
        const btn = document.getElementById('manual-screenshot');
        const originalText = btn.innerHTML;
        
        btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>截图中...';
        btn.disabled = true;
        
        // 模拟截图请求
        fetch('/api/screenshot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showNotification('截图已保存', 'success');
                this.refreshStats();
            } else {
                this.showNotification('截图失败', 'error');
            }
        })
        .catch(error => {
            console.error('Screenshot error:', error);
            this.showNotification('截图请求失败', 'error');
        })
        .finally(() => {
            btn.innerHTML = originalText;
            btn.disabled = false;
        });
    }

    refreshStats() {
        fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                this.updateStatsDisplay(data);
                this.showNotification('统计数据已更新', 'success');
            })
            .catch(error => {
                console.error('Stats refresh error:', error);
                this.showNotification('统计数据更新失败', 'error');
            });
    }

    updateStatsDisplay(data) {
        // 更新统计卡片
        const elements = {
            'total-detections': data.total,
            'safe-count': data.safe,
            'unsafe-count': data.unsafe,
            'accuracy-rate': data.accuracy + '%'
        };

        Object.keys(elements).forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = elements[id];
            }
        });

        // 更新检测项目状态
        if (data.items) {
            data.items.forEach(item => {
                const element = document.getElementById(`item-${item.id}`);
                if (element) {
                    element.className = `detection-item ${item.detected ? 'border-success' : 'border-error'}`;
                    const statusText = element.querySelector('.detection-status-text');
                    if (statusText) {
                        statusText.textContent = item.detected ? '已佩戴' : '未佩戴';
                        statusText.className = `detection-status-text ${item.detected ? 'text-success' : 'text-error'}`;
                    }
                }
            });
        }
    }

    updateDetectionStatus(status) {
        const indicator = document.querySelector('.status-indicator');
        if (indicator) {
            indicator.className = `status-indicator ${status}`;
        }
    }

    initializeCharts() {
        // 初始化图表（如果有chart.js）
        if (typeof Chart !== 'undefined') {
            this.createAccuracyChart();
            this.createDetectionTrendChart();
        }
    }

    createAccuracyChart() {
        const ctx = document.getElementById('accuracy-chart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['正确佩戴', '未佩戴', '检测失败'],
                datasets: [{
                    data: [85, 12, 3],
                    backgroundColor: ['#10b981', '#ef4444', '#f59e0b'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    createDetectionTrendChart() {
        const ctx = document.getElementById('trend-chart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                datasets: [{
                    label: '检测次数',
                    data: [120, 190, 300, 500, 200, 300],
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    startStatsUpdate() {
        // 每30秒更新一次统计数据
        setInterval(() => {
            if (this.isStreaming) {
                this.refreshStats();
            }
        }, 30000);
    }

    checkSystemStatus() {
        // 检查系统状态
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'healthy') {
                    this.showNotification('系统运行正常', 'success');
                } else {
                    this.showNotification('系统状态异常', 'warning');
                }
            })
            .catch(error => {
                console.error('System check error:', error);
                this.showNotification('系统状态检查失败', 'error');
            });
    }

    exportReport() {
        const btn = document.getElementById('export-report');
        const originalText = btn.innerHTML;
        
        btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>生成中...';
        btn.disabled = true;
        
        // 模拟报告生成
        setTimeout(() => {
            // 创建并下载报告
            const reportData = this.generateReportData();
            this.downloadReport(reportData);
            
            btn.innerHTML = originalText;
            btn.disabled = false;
            this.showNotification('报告已生成并下载', 'success');
        }, 2000);
    }

    generateReportData() {
        const now = new Date();
        return {
            timestamp: now.toISOString(),
            totalDetections: this.detectionStats.total,
            safeCount: this.detectionStats.safe,
            unsafeCount: this.detectionStats.unsafe,
            accuracy: this.detectionStats.accuracy,
            generatedBy: 'SmartSafety System'
        };
    }

    downloadReport(data) {
        const blob = new Blob([JSON.stringify(data, null, 2)], {
            type: 'application/json'
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ppe-detection-report-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    openSettings() {
        // 打开设置模态框
        const modal = document.getElementById('settings-modal');
        if (modal) {
            modal.classList.add('modal-open');
        }
    }

    showNotification(message, type = 'info') {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} fixed top-4 right-4 z-50 max-w-sm`;
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        // 3秒后自动移除
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-triangle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', function() {
    window.smartSafetyApp = new SmartSafetyApp();
});

// 全局函数供HTML调用
function toggleFullscreen() {
    const videoContainer = document.getElementById('video-container');
    if (videoContainer) {
        if (!document.fullscreenElement) {
            videoContainer.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }
}

function refreshPage() {
    location.reload();
}