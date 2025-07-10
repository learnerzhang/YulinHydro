import { ref } from 'vue';

// 全局错误状态
const errorMessage = ref('');
const showError = ref(false);

export default {
  showError,
  errorMessage,
  
  // 处理 API 错误
  handleApiError(error) {
    if (error.response) {
      // 服务器返回的错误
      const status = error.response.status;
      if (status === 401) {
        this.setError('登录已过期，请重新登录');
      } else if (status >= 500) {
        this.setError('服务器错误，请稍后再试');
      } else {
        this.setError(error.response.data?.message || '请求失败');
      }
    } else if (error.request) {
      // 请求已发送但无响应
      this.setError('网络错误，请检查连接');
    } else {
      // 请求未发出
      this.setError('请求配置错误');
    }
    
    // 重置错误状态
    setTimeout(() => {
      this.resetError();
    }, 5000);
  },
  
  // 设置错误信息
  setError(message) {
    errorMessage.value = message;
    showError.value = true;
  },
  
  // 重置错误状态
  resetError() {
    showError.value = false;
    errorMessage.value = '';
  }
};