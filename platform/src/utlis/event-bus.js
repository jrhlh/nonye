// utils/event-bus.js - 改进事件总线以管理全局状态
class GlobalState {
    constructor() {
        this.threshold = 36; // 默认阈值
        this.listeners = new Map();
    }

    // 注册事件监听
    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }

    // 触发事件
    emit(event, data) {
        if (this.listeners.has(event)) {
            this.listeners.get(event).forEach(callback => callback(data));
        }
    }

    // 设置全局阈值
    setThreshold(threshold) {
        this.threshold = threshold;
        this.emit('thresholdUpdated', threshold);
    }

    // 获取全局阈值
    getThreshold() {
        return this.threshold;
    }
}

// 创建全局状态实例
const globalState = new GlobalState();
export default globalState;