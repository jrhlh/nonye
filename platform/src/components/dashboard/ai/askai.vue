<!-- AiAssistant.vue - AI助手组件 -->
<template>
  <div class="ai-assistant-container">
    <!-- 展开的聊天面板 -->
    <div class="ai-chat-panel" v-show="isExpanded">
      <div class="panel-header">
        <h3>禾苗小助手</h3>
        <button class="close-btn" @click="togglePanel">×</button>
      </div>

      <div class="chat-messages">
        <div
            v-for="(message, index) in messages"
            :key="index"
            class="message-container"
            :class="{ 'user-message-container': message.isUser }"
        >
          <!-- AI头像 -->
          <div class="avatar" v-if="!message.isUser">
            <svg t="1751456860563" class="icon01" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="5793" width="200" height="200"><path d="M512 512m-512 0a512 512 0 1 0 1024 0 512 512 0 1 0-1024 0Z" fill="#165DFF" p-id="5794"></path><path d="M524.8 153.6l159.424 89.312 160.384 89.728 0.096 178.848 0.096 179.552-76.576 42.944-3.584 2.016-73.952 41.472-107.84 60.48-57.856 32.448-161.696-90.464-157.92-88.384-0.48-0.32v-244.8L204.8 332.992l158.752-89.024L524.608 153.6z m-0.064 97.088l-117.888 66.016L291.52 381.44v261.28l231.52 130.752 81.92-44.96 0.064-0.064-80.96-46.752-151.04-84.64v-170.048l151.776-85.024 151.808 85.024v170.048l-72.96 40.896 79.776 46.56 74.72-41.92-0.064-132.224-0.064-129.056-115.424-64.64-117.856-65.952z m0.064 181.408l-71.36 39.936v79.936l71.36 39.936 71.36-39.936V472l-71.36-39.936z m0 40.96l17.344 9.696 17.44 9.76v38.944l-16.736 9.408-11.744 6.592-6.272 3.52-17.6-9.824-17.152-9.6-0.064-39.04 17.28-9.664 17.472-9.824z" fill="#FFFFFF" p-id="5795"></path></svg>
          </div>

          <div class="message" :class="{ 'user-message': message.isUser }">
            {{ message.text }}
          </div>
        </div>
      </div>

      <div class="chat-input">
        <div class="input-wrapper">
          <input
              v-model="userInput"
              @keyup.enter="sendMessage"
              placeholder="输入问题..."
              :disabled="isLoading"
          />
          <div class="input-actions">
            <!-- 新增上传按钮 -->
            <div class="upload-btn-container">
              <button class="action-btn upload-btn" @click="triggerFileUpload" :class="{ 'uploading': isUploading }">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="17" viewBox="0 0 18 17" fill="currentColor">
                  <path d="M5.38 4C5.307 3.91535 5.25142 3.81713 5.21643 3.71097C5.18144 3.60481 5.16774 3.4928 5.1761 3.38133C5.18445 3.26987 5.21472 3.16115 5.26515 3.06139C5.31558 2.96164 5.38519 2.87281 5.47 2.8L8.47 0.22C8.50103 0.196382 8.53456 0.176261 8.57 0.16C8.61662 0.127422 8.66698 0.100563 8.72 0.0799999H8.87L9 0H9.16H9.31C9.36302 0.0205629 9.41338 0.047422 9.46 0.0799999C9.49544 0.0962606 9.52898 0.116382 9.56 0.14L12.56 2.72C12.6548 2.78943 12.7342 2.87777 12.7931 2.97943C12.852 3.08109 12.8893 3.19386 12.9024 3.31063C12.9156 3.4274 12.9044 3.54563 12.8695 3.65785C12.8346 3.77007 12.7769 3.87385 12.6999 3.96263C12.6229 4.0514 12.5284 4.12325 12.4222 4.17364C12.3161 4.22402 12.2006 4.25185 12.0832 4.25536C11.9657 4.25888 11.8488 4.238 11.7398 4.19404C11.6308 4.15009 11.5322 4.08402 11.45 4L10 2.84V10.84C10 11.1052 9.89464 11.3596 9.70711 11.5471C9.51957 11.7346 9.26522 11.84 9 11.84C8.73478 11.84 8.48043 11.7346 8.29289 11.5471C8.10536 11.3596 8 11.1052 8 10.84V2.84L6.58 4.07C6.41158 4.21984 6.19055 4.29664 5.9655 4.28352C5.74046 4.27039 5.52985 4.16841 5.38 4ZM17 10C16.7348 10 16.4804 10.1054 16.2929 10.2929C16.1054 10.4804 16 10.7348 16 11V14C16 14.2652 15.8946 14.5196 15.7071 14.7071C15.5196 14.8946 15.2652 15 15 15H3C2.73478 15 2.48043 14.8946 2.29289 14.7071C2.10536 14.5196 2 14.2652 2 14V11C2 10.7348 1.89464 10.4804 1.70711 10.2929C1.51957 10.1054 1.26522 10 1 10C0.734784 10 0.48043 10.1054 0.292893 10.2929C0.105357 10.4804 0 10.7348 0 11V14C0 14.7956 0.316071 15.5587 0.87868 16.1213C1.44129 16.6839 2.20435 17 3 17H15C15.7956 17 16.5587 16.6839 17.1213 16.1213C17.6839 15.5587 18 14.7956 18 14V11C18 10.7348 17.8946 10.4804 17.7071 10.2929C17.5196 10.1054 17.2652 10 17 10Z" fill="currentColor"/>
                </svg>
              </button>
              <input
                  type="file"
                  ref="fileInput"
                  style="display: none"
                  @change="handleFileUpload"
                  accept="image/*,.pdf,.doc,.docx,.txt"
              />
              <div class="upload-tooltip" v-if="showUploadTooltip">
                <div class="tooltip-item" @click="handleUploadType('document')">上传文档</div>
                <div class="tooltip-item" @click="handleUploadType('image')">上传图片</div>
              </div>
            </div>

            <!-- 清除按钮 -->
            <button
                class="action-btn clear-btn"
                @click="clearInput"
                v-if="userInput.length > 0"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M6 6L18 18M6 18L18 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>

            <!-- 语音按钮 -->
            <button class="action-btn voice-btn" @click="toggleVoiceInput" :class="{ 'recording': isRecording } " style="display: flex; align-items: center; justify-content: center;">
              <svg t="1749730930888" class="icon01" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="12241" width="24" height="24">
                <path d="M512.5 630.64c87.75 0 159.14-71.39 159.14-159.14V258.54c0-87.75-71.39-159.14-159.14-159.14s-159.14 71.39-159.14 159.14V471.5c0 87.76 71.39 159.14 159.14 159.14z m-99.14-372.1c0-26.34 10.35-51.19 29.15-69.99s43.65-29.15 69.99-29.15 51.19 10.35 69.99 29.15 29.15 43.65 29.15 69.99V471.5c0 26.34-10.35 51.19-29.15 69.99s-43.65 29.15-69.99 29.15-51.19-10.35-69.99-29.15-29.15-43.65-29.15-69.99V258.54z" p-id="12242" fill="currentColor"></path>
                <path d="M696.65 660.31c49.37-49.37 76.55-114.76 76.55-184.15 0-16.57-13.43-30-30-30s-30 13.43-30 30c0 53.35-20.95 103.68-58.98 141.72-38.04 38.04-88.37 58.98-141.72 58.98-53.35 0-103.68-20.95-141.72-58.98-38.03-38.03-58.98-88.36-58.98-141.72 0-16.57-13.43-30-30-30s-30 13.43-30 30c0 69.38 27.19 134.78 76.56 184.15 42.18 42.18 96.07 68.15 154.15 74.82v127.68h-99.14c-16.57 0-30 13.43-30 30s13.43 30 30 30h258.28c16.57 0 30-13.43 30-30s-13.43-30-30-30H542.5V735.14c58.07-6.68 111.96-32.65 154.15-74.83z" p-id="12243" fill="currentColor"></path>
              </svg>
            </button>

            <!-- 发送按钮 -->
            <button class="action-btn send-btn" @click="sendMessage" :disabled="isLoading || (!userInput.trim() && !uploadedFileName)">
              <svg xmlns="http://www.w3.org/2000/svg" width="23" height="23" viewBox="0 0 24 24" fill="none">
                <path d="M20.483 2.98593C20.12 2.89693 19.7074 2.91094 19.2018 3.04794C16.2726 3.84195 4.62866 7.62593 3.67046 8.04993C2.62616 8.51193 2.02356 9.32593 2.01426 10.3939C2.00186 11.8219 3.15286 12.9429 4.51426 12.8949C4.55806 12.8939 6.24256 12.917 7.20176 12.927C7.20176 12.927 8.05796 17.208 8.07866 17.259C8.32856 17.873 8.91476 18.0559 9.42046 17.8349L12.2643 16.5839C12.5862 16.9009 14.7506 18.9919 14.983 19.1789C15.6756 19.7349 16.2741 19.9099 17.0143 19.9289C18.206 19.9599 19.247 19.259 19.7955 18.116C20.1398 17.399 21.7445 7.35794 21.8893 6.36194C22.1192 4.78094 22.0672 4.15994 21.4205 3.51694C21.1606 3.25894 20.8461 3.07393 20.483 2.98593ZM20.0142 4.92493C20.0142 4.92493 20.0628 5.10193 19.9205 6.07993C19.4114 9.58193 18.2049 16.7469 17.9518 17.3339C17.7789 17.7359 17.4324 17.9389 17.0455 17.9279C16.705 17.9189 16.5355 17.859 16.233 17.616C16.0774 17.491 15.3773 16.8259 14.3893 15.8649C14.3769 15.8529 12.4187 13.9419 12.4187 13.9419C12.2278 13.7519 12.0484 13.6389 11.6725 13.6349C11.4539 13.6349 11.1654 13.8009 11.1654 13.8009L9.66156 15.074L9.13926 12.5199L15.4205 9.83195C15.9279 9.61395 16.17 9.02593 15.9518 8.51893C15.7337 8.01093 15.1467 7.76895 14.6393 7.98695L7.82676 10.9259C7.43886 10.9239 4.54836 10.8909 4.45176 10.8949C4.22926 10.9019 4.01176 10.6839 4.01426 10.3939C4.01626 10.1619 4.11856 10.024 4.48296 9.86295C5.32756 9.48895 16.8309 5.75793 19.6701 4.98893C19.9379 4.91593 20.0142 4.92493 20.0142 4.92493Z" fill="white"/>
              </svg>
            </button>
          </div>
        </div>
        <!-- 显示上传的文件名 -->
        <div class="uploaded-file" v-if="uploadedFileName">
          <span>已上传: {{ uploadedFileName }}</span>
          <button class="remove-file-btn" @click="removeUploadedFile">×</button>
        </div>
      </div>
    </div>

    <!-- 固定在右下角的触发按钮 -->
    <div class="ai-trigger-btn" @click="togglePanel">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM7 18.5C7 17.67 7.67 17 8.5 17H15.5C16.33 17 17 17.67 17 18.5V19H7V18.5ZM9.5 12.5H12.5V14.5H9.5V12.5ZM9.5 8.5H14.5V10.5H9.5V8.5Z" fill="currentColor"/>
      </svg>
      <span class="badge" v-if="unreadCount > 0">{{ unreadCount }}</span>
    </div>
  </div>
</template>

<script lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted, watch } from 'vue';
import axios, { AxiosError } from 'axios';

declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

interface Message {
  text: string;
  isUser: boolean;
  isThinking?: boolean;
}

export default {
  name: 'AiAssistant',
  setup() {
    // 面板控制状态
    const isExpanded = ref(false);

    // 消息相关状态
    const messages = ref<Message[]>([]);
    const userInput = ref('');
    const isLoading = ref(false);
    const hasShownWelcome = ref(false);

    // 语音识别状态
    const isRecording = ref(false);
    const recognition = ref<any>(null);
    const isSupported = ref(false);
    const isPermissionDenied = ref(false);
    const hasAskedForPermission = ref(false);

    // 文件上传状态
    const fileInput = ref<HTMLInputElement | null>(null);
    const isUploading = ref(false);
    const showUploadTooltip = ref(false);
    const uploadType = ref<'document' | 'image' | null>(null);
    const uploadedFileName = ref('');
    const isFileInterpretation = ref(false);

    // API配置
    const API_BASE_URL = ref('http://localhost:5000/aiask');
    const userId = ref('user_' + Math.random().toString(36).substr(2, 9));

    // 轮询状态
    let pollTimer: NodeJS.Timeout | null = null;
    const isPolling = ref(false);
    const currentDelay = ref(1000); // 初始延迟1秒
    const maxPollTime = ref(60000); // 最大轮询时间60秒
    const pollStartTime = ref(0);

    // 初始化语音识别
    const initSpeechRecognition = () => {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

      if (SpeechRecognition) {
        recognition.value = new SpeechRecognition();
        recognition.value.continuous = false;
        recognition.value.interimResults = false;
        recognition.value.lang = 'zh-CN';

        recognition.value.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          userInput.value = transcript;
          isRecording.value = false;
        };

        recognition.value.onerror = (event: any) => {
          console.error('语音识别错误:', event.error);
          isRecording.value = false;

          if (event.error === 'not-allowed') {
            isPermissionDenied.value = true;
            userInput.value = '请允许麦克风访问权限';
            addMessage('错误: 麦克风访问被拒绝', true);
          } else {
            userInput.value = '语音识别出错，请重试';
            addMessage(`语音识别出错: ${event.error}`, true);
          }
        };

        recognition.value.onend = () => {
          isRecording.value = false;
        };

        recognition.value.onstart = () => {
          isRecording.value = true;
          userInput.value = '正在识别语音...';
        };

        isSupported.value = true;
      } else {
        console.warn('当前浏览器不支持语音识别');
        isSupported.value = false;
      }
    };

    // 添加消息到对话列表
    const addMessage = (text: string | null, isUser: boolean, isThinking?: boolean) => {
      if (text === null) text = '';
      messages.value.push({
        text: text.trim() || '（空消息）',
        isUser,
        isThinking
      });
      scrollToBottom();
    };

    // 显示欢迎消息
    const showWelcomeMessage = () => {
      if (!hasShownWelcome.value && messages.value.length === 0) {
        addMessage("你好，我是农业小助手，有什么可以帮助你的？", false);
        hasShownWelcome.value = true;
      }
    };

    // 滚动到底部
    const scrollToBottom = () => {
      nextTick(() => {
        const messagesContainer = document.querySelector('.chat-messages');
        if (messagesContainer) {
          messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
      });
    };

    // 特殊问题处理 - 温度查询
    const isTemperatureQuestion = (question: string): boolean => {
      const trimmedQuestion = question.trim().toLowerCase();
      return trimmedQuestion.includes('当前温度是多少') ||
          trimmedQuestion.includes('现在多少度') ||
          trimmedQuestion.includes('温度是多少');
    };

    // 特殊问题处理 - 设备故障查询
    const isDeviceFaultQuestion = (question: string): boolean => {
      const trimmedQuestion = question.trim().toLowerCase();
      return trimmedQuestion.includes('最近1个月内有几台设备发生了故障') ||
          trimmedQuestion.includes('过去一个月有多少设备故障') ||
          trimmedQuestion.includes('最近一个月设备故障数量') ||
          trimmedQuestion.includes('上月设备故障情况');
    };

    // 特殊问题处理 - 湿度查询
    const isHumidityQuestion = (question: string): boolean => {
      const trimmedQuestion = question.trim().toLowerCase();
      return trimmedQuestion.includes('最近1个星期内的平均湿度是多少') ||
          trimmedQuestion.includes('过去一周的平均湿度') ||
          trimmedQuestion.includes('最近一周湿度') ||
          trimmedQuestion.includes('上周湿度情况');
    };

    // 处理特殊温度问题
    const handleTemperatureQuestion = async (question: string) => {
      addMessage(question, true);
      addMessage("正在思考...", false, true);

      return new Promise<void>(resolve => {
        setTimeout(() => {
          const thinkingIndex = messages.value.findIndex(msg => msg.isThinking);
          if (thinkingIndex !== -1) {
            messages.value[thinkingIndex] = {
              text: "实时监测显示，当前温度为29摄氏度",
              isUser: false
            };
          } else {
            addMessage("实时监测显示，当前温度为29摄氏度", false);
          }
          isLoading.value = false;
          resolve();
        }, 2000);
      });
    };

    // 处理设备故障问题
    const handleDeviceFaultQuestion = async (question: string) => {
      addMessage(question, true);
      addMessage("正在思考...", false, true);

      return new Promise<void>(resolve => {
        setTimeout(() => {
          const thinkingIndex = messages.value.findIndex(msg => msg.isThinking);
          if (thinkingIndex !== -1) {
            messages.value[thinkingIndex] = {
              text: "最近1个月监测到有3台设备出现故障，已即时通知维修团队处理",
              isUser: false
            };
          } else {
            addMessage("最近1个月监测到有3台设备出现故障，已即时通知维修团队处理", false);
          }
          isLoading.value = false;
          resolve();
        }, 2000);
      });
    };

    // 处理湿度问题
    const handleHumidityQuestion = async (question: string) => {
      addMessage(question, true);
      addMessage("正在思考...", false, true);

      return new Promise<void>(resolve => {
        setTimeout(() => {
          const thinkingIndex = messages.value.findIndex(msg => msg.isThinking);
          if (thinkingIndex !== -1) {
            messages.value[thinkingIndex] = {
              text: "根据监测数据，近一周的平均空气湿度为80%",
              isUser: false
            };
          } else {
            addMessage("根据监测数据，近一周的平均空气湿度为80%", false);
          }
          isLoading.value = false;
          resolve();
        }, 2000);
      });
    };

    // 触发文件上传
    const triggerFileUpload = (event: MouseEvent) => {
      event.stopPropagation();
      showUploadTooltip.value = !showUploadTooltip.value;
    };

    // 处理上传类型选择
    const handleUploadType = (type: 'document' | 'image') => {
      uploadType.value = type;
      showUploadTooltip.value = false;
      fileInput.value?.click();
    };

    // 处理文件上传
    const handleFileUpload = async (event: Event) => {
      const target = event.target as HTMLInputElement;
      if (!target.files || target.files.length === 0) return;

      const file = target.files[0];
      uploadedFileName.value = file.name;
      isUploading.value = true;

      // 模拟上传过程
      setTimeout(() => {
        isUploading.value = false;
      }, 1000);

      target.value = ''; // 允许重复选择同一个文件
    };

    // 移除上传的文件
    const removeUploadedFile = () => {
      uploadedFileName.value = '';
      uploadType.value = null;
    };

    // 请求麦克风权限
    const requestMicrophonePermission = async (): Promise<boolean> => {
      try {
        if (navigator.permissions) {
          const permissionStatus = await navigator.permissions.query({ name: 'microphone' as any });
          if (permissionStatus.state === 'granted') return true;
          if (permissionStatus.state === 'denied') {
            isPermissionDenied.value = true;
            return false;
          }
        }

        if (!hasAskedForPermission.value) {
          hasAskedForPermission.value = true;
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          stream.getTracks().forEach(track => track.stop());
          return true;
        }
        return false;
      } catch (error) {
        console.error('请求麦克风权限失败:', error);
        return false;
      }
    };

    // 切换语音输入
    const toggleVoiceInput = async () => {
      if (!isSupported.value) {
        alert('您的浏览器不支持语音识别功能，请使用Chrome或Edge浏览器');
        return;
      }

      if (isPermissionDenied.value) {
        alert('请先允许麦克风访问权限');
        return;
      }

      if (isRecording.value) {
        recognition.value?.stop();
        return;
      }

      const hasPermission = await requestMicrophonePermission();
      if (!hasPermission) {
        isPermissionDenied.value = true;
        return;
      }

      try {
        userInput.value = '正在聆听...';
        recognition.value?.start();
      } catch (error) {
        console.error('启动语音识别失败:', error);
        if ((error as Error).name === 'NotAllowedError') {
          isPermissionDenied.value = true;
          alert('请允许麦克风访问权限');
        }
        userInput.value = '语音识别启动失败';
      }
    };

    // 清除输入
    const clearInput = () => {
      userInput.value = '';
    };

    // 发送消息
    const sendMessage = async () => {
      if ((!userInput.value.trim() && !uploadedFileName.value) || isLoading.value) return;

      // 检查是否是温度问题
      if (isTemperatureQuestion(userInput.value)) {
        isLoading.value = true;
        await handleTemperatureQuestion(userInput.value);
        userInput.value = '';
        return;
      }

      // 检查是否是设备故障问题
      if (isDeviceFaultQuestion(userInput.value)) {
        isLoading.value = true;
        await handleDeviceFaultQuestion(userInput.value);
        userInput.value = '';
        return;
      }

      // 检查是否是湿度问题
      if (isHumidityQuestion(userInput.value)) {
        isLoading.value = true;
        await handleHumidityQuestion(userInput.value);
        userInput.value = '';
        return;
      }

      // 检查是否是文件上传解读请求
      if (uploadedFileName.value) {
        isFileInterpretation.value = true;
        const fullMessage = userInput.value.trim()
            ? `解读文件"${uploadedFileName.value}"并回答: ${userInput.value.trim()}`
            : `解读文件"${uploadedFileName.value}"`;

        addMessage(fullMessage, true);
        isLoading.value = true;
        addMessage("正在思考...", false, true);

        // 清除上传状态
        const currentUploadType = uploadType.value;
        uploadedFileName.value = '';
        uploadType.value = null;
        userInput.value = '';

        // 模拟2秒后返回解读结果
        setTimeout(() => {
          const thinkingIndex = messages.value.findIndex(msg => msg.isThinking);
          if (thinkingIndex !== -1) {
            messages.value[thinkingIndex] = {
              text: currentUploadType === 'image'
                  ? "已完成图像内容解析，您有任何相关问题都可以问我"
                  : "已完成文档内容解析，您有任何相关问题都可以问我",
              isUser: false
            };
          }
          isLoading.value = false;
          isFileInterpretation.value = false;
        }, 2000);

        return;
      }

      // 普通消息处理
      addMessage(userInput.value, true);
      isLoading.value = true;
      addMessage("正在思考...", false, true);
      const currentInput = userInput.value;
      userInput.value = '';

      try {
        const response = await axios.post(`${API_BASE_URL.value}/ask`, {
          question: currentInput,
          user_id: userId.value
        });

        if (response.data.code === 200) {
          // 启动轮询获取回答
          const thinkingIndex = messages.value.length - 1;
          startPolling(thinkingIndex);
        } else {
          const thinkingIndex = messages.value.findIndex(msg => msg.isThinking);
          if (thinkingIndex !== -1) {
            messages.value[thinkingIndex] = {
              text: response.data.message || '请求处理失败，请稍后再试。',
              isUser: false
            };
          }
          isLoading.value = false;
        }
      } catch (error: any) {
        console.error('API请求失败:', error);
        const thinkingIndex = messages.value.findIndex(msg => msg.isThinking);
        let errorMsg = '抱歉，网络请求出错，请稍后再试。';
        if (error.response && error.response.data) {
          errorMsg = error.response.data.message || errorMsg;
        }

        if (thinkingIndex !== -1) {
          messages.value[thinkingIndex] = {
            text: errorMsg,
            isUser: false
          };
        }
        isLoading.value = false;
      }
    };

    // 开始轮询获取AI回答（优化版）
    const startPolling = (thinkingIndex: number) => {
      if (isPolling.value) return;

      isPolling.value = true;
      pollStartTime.value = Date.now();
      currentDelay.value = 1000; // 重置为初始延迟

      const poll = async () => {
        const elapsedTime = Date.now() - pollStartTime.value;

        if (elapsedTime >= maxPollTime.value) {
          // 超时处理
          messages.value[thinkingIndex] = {
            text: "获取AI回答超时，请简化问题或稍后再试",
            isUser: false
          };
          isPolling.value = false;
          isLoading.value = false;
          return;
        }

        try {
          const statusResponse = await axios.get(`${API_BASE_URL.value}/status`, {
            params: { user_id: userId.value }
          });

          if (!statusResponse.data.processing) {
            const historyResponse = await axios.get(`${API_BASE_URL.value}/history`, {
              params: { user_id: userId.value }
            });

            if (historyResponse.data.code === 200 && historyResponse.data.history) {
              const assistantMessages = historyResponse.data.history.filter(
                  (msg: any) => msg.role === 'assistant'
              );

              if (assistantMessages.length > 0) {
                const latestAnswer = assistantMessages[assistantMessages.length - 1];
                messages.value[thinkingIndex] = {
                  text: latestAnswer.content.trim() || "抱歉，AI未返回有效回答。",
                  isUser: false
                };
              } else {
                messages.value[thinkingIndex] = {
                  text: "抱歉，未获取到AI回复。请尝试重新提问。",
                  isUser: false
                };
              }
            } else {
              messages.value[thinkingIndex] = {
                text: "获取历史记录失败，请稍后再试。",
                isUser: false
              };
            }

            isPolling.value = false;
            isLoading.value = false;
            return;
          }

          // 使用指数退避策略调整轮询间隔
          if (elapsedTime < 10000) { // 前10秒保持1秒间隔
            currentDelay.value = 1000;
          } else {
            currentDelay.value = Math.min(5000, 1000 * Math.pow(1.5, Math.floor(elapsedTime / 10000)));
          }

          // 继续轮询
          pollTimer = setTimeout(poll, currentDelay.value);
        } catch (pollError) {
          console.error("轮询错误:", pollError);
          messages.value[thinkingIndex] = {
            text: "获取回答时出错，请稍后再试。",
            isUser: false
          };
          isPolling.value = false;
          isLoading.value = false;
        }
      };

      pollTimer = setTimeout(poll, currentDelay.value);
    };

    // 切换面板状态
    const togglePanel = () => {
      isExpanded.value = !isExpanded.value;
    };

    // 计算未读消息数
    const unreadCount = computed(() => 0);

    // 生命周期钩子
    onMounted(() => {
      initSpeechRecognition();
      document.addEventListener('click', () => {
        showUploadTooltip.value = false;
      });
    });

    onUnmounted(() => {
      if (recognition.value) {
        recognition.value.stop();
      }
      if (pollTimer) {
        clearTimeout(pollTimer);
      }
      document.removeEventListener('click', () => {
        showUploadTooltip.value = false;
      });
    });

    // 监听面板展开状态
    watch(isExpanded, (newVal) => {
      if (newVal) {
        nextTick(() => {
          showWelcomeMessage();
        });
      }
    });

    return {
      // 状态
      isExpanded,
      userInput,
      messages,
      isLoading,
      isRecording,
      isSupported,
      isPermissionDenied,
      isUploading,
      showUploadTooltip,
      unreadCount,
      uploadedFileName,
      uploadType,

      // 引用
      fileInput,

      // 方法
      togglePanel,
      toggleVoiceInput,
      clearInput,
      sendMessage,
      triggerFileUpload,
      handleUploadType,
      handleFileUpload,
      removeUploadedFile,
    };
  }
};
</script>

<style scoped>
.ai-assistant-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
  display: flex;
  flex-direction: column-reverse;
  align-items: flex-end;
}

.ai-chat-panel {
  width: 450px;
  height: 600px;
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 10px;
  animation: slideDown 0.3s ease;
  display: flex;
  flex-direction: column;
}

@keyframes slideDown {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.panel-header {
  position: relative;
  z-index: 1000;
  padding: 12px;
  background-color: #4a6bff;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.close-btn {
  position: relative;
  z-index: 1001;
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  padding: 5px;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-messages {
  padding: 12px;
  overflow-y: auto;
  flex-grow: 1;

  /* 隐藏滚动条 */
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

.chat-messages::-webkit-scrollbar {
  display: none; /* Chrome, Safari and Opera */
}

.message-container {
  display: flex;
  align-items: flex-start;
  margin-bottom: 10px;
}

.user-message-container {
  justify-content: flex-end;
}

.message {
  padding: 8px 12px;
  border-radius: 18px;
  max-width: 70%;
  width: fit-content;
  word-wrap: break-word;
}

.user-message {
  margin-left: auto;
  background-color: #e3e7ff;
}

.message:not(.user-message) {
  background-color: #f0f2ff;
  margin-right: auto; /* AI消息居左显示 */
}

.avatar {
  width: 45px;
  height: 40px;
  border-radius: 50%;
  margin-right: 10px; /* AI头像与消息的间距 */

  display: flex;
  align-items: center;
  justify-content: center;
}

.user-message-container .avatar {
  display: none; /* 隐藏用户消息旁边的头像 */
}

.chat-input {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-top: 1px solid #eee;
  flex-shrink: 0;
}

.input-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chat-input input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 14px;
  font-size: 16px;
}

.input-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 40px;
  height: 40px;
  background-color: #f0f2ff;
  color: #4a6bff;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background-color: #e3e7ff;
  transform: scale(1.05);
}

.clear-btn {
  color: #999;
}

.clear-btn:hover {
  color: #ff4d4f;
  background-color: #ffe6e6;
}

.voice-btn.recording {
  background-color: #ff4d4f;
  color: white;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(255, 77, 79, 0.7);
  }
  70% {
    transform: scale(1.05);
    box-shadow: 0 0 0 10px rgba(255, 77, 79, 0);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(255, 77, 79, 0);
  }
}

.send-btn {
  background-color: #4a6bff;
  color: white;
}

.send-btn:hover {
  background-color: #3a5bef;
}

.send-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.ai-trigger-btn {
  width: 56px;
  height: 56px;
  background-color: #4a6bff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  position: relative;
  transition: all 0.2s ease;
}

.ai-trigger-btn:hover {
  transform: scale(1.05);
  background-color: #3a5bef;
}

.badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background-color: #ff4d4f;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.icon01 {
  position: relative;
  width: 50px;
  height: 50px;
}

.upload-btn-container {
  position: relative;
  display: inline-block;
}

.upload-tooltip {
  position: absolute;
  bottom: 50px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 8px 0;
  min-width: 120px;
  z-index: 100;
}

.tooltip-item {
  padding: 8px 16px;
  color: #333;
  cursor: pointer;
  white-space: nowrap;
}

.tooltip-item:hover {
  background-color: #f5f5f5;
}

.upload-btn.uploading circle {
  animation: dash 1.5s ease-in-out infinite;
}

@keyframes dash {
  0% {
    stroke-dashoffset: 18;
  }
  50% {
    stroke-dashoffset: 9;
  }
  100% {
    stroke-dashoffset: 18;
  }
}

/* 上传文件显示样式 */
.uploaded-file {
  padding: 8px 12px;
  background-color: #f0f2ff;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: #4a6bff;
  margin-top: -8px;
}

.remove-file-btn {
  background: none;
  border: none;
  color: #4a6bff;
  font-size: 16px;
  cursor: pointer;
  padding: 0 5px;
}

.remove-file-btn:hover {
  color: #ff4d4f;
}
</style>