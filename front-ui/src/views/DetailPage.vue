<template>
  <div class="detail-page">
    <div v-if="isLoading" class="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>
    <div v-else-if="error" class="error-card">
      <div class="error-icon">⚠️</div>
      <p>{{ error }}</p>
      <button @click="retry" class="retry-btn">重试</button>
    </div>
    <div v-else class="content">
      <div class="left-panel card">
        <div class="pdf-controls">
          <button 
            @click="prevPage" 
            :disabled="currentPage <= 1"
            class="control-btn"
          >
            上一页
          </button>
          <span class="page-info">第 {{ currentPage }} 页 / 共 {{ numPages }} 页</span>
          <button 
            @click="nextPage" 
            :disabled="currentPage >= numPages"
            class="control-btn"
          >
            下一页
          </button>
        </div>
        
        <pdf-viewer
          v-if="pdfUrl"
          :src="pdfUrl"
          :page="currentPage"
          :bbox="currentBbox"
          @num-pages="numPages = $event"
          @error="handlePdfError"
          class="pdf-viewer"
        />
      </div>
      
      <div class="right-panel card">
        <div class="search-container">
          <input
            v-model="searchText"
            type="text"
            placeholder="搜索文档内容..."
            @keyup.enter="searchInPdf"
            class="search-input"
          />
          <button @click="searchInPdf" class="search-button">
            <i class="search-icon">🔍</i>
          </button>
        </div>
        
        <div class="result-list">
          <div v-if="searchResults.length === 0 && searchText" class="no-result">
            未找到相关结果
          </div>
          
          <div
            v-for="(result, index) in searchResults"
            :key="index"
            class="result-item"
            @click="goToPosition(result.pageNumber, result.bbox)"
            @mouseenter="result.hover = true"
            @mouseleave="result.hover = false"
          >
            <div class="result-page">
              第 {{ result.pageNumber }} 页
            </div>
            <p class="result-content">
              <span 
                v-for="(part, i) in result.contextParts" 
                :key="i"
                :class="{ 'highlight-text': part.highlight }"
              >
                {{ part.text }}
              </span>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import apis from '@/apis'
import PdfViewer from '@/components/PdfViewer.vue'

const route = useRoute()
const pdfUrl = ref('')
const searchText = ref('')
const searchResults = ref([])
const isLoading = ref(true)
const error = ref('')

// 分页和定位相关变量
const currentPage = ref(1)
const currentBbox = ref([])
const numPages = ref(0)

// 处理搜索结果，拆分高亮文本
const processSearchResults = (results) => {
  return results.map(result => {
    // 拆分文本为普通部分和高亮部分
    const parts = []
    const lowerText = result.context.toLowerCase()
    const lowerQuery = searchText.value.toLowerCase()
    const queryIndex = lowerText.indexOf(lowerQuery)
    
    if (queryIndex > 0) {
      parts.push({ text: result.context.substring(0, queryIndex), highlight: false })
    }
    
    parts.push({ 
      text: result.context.substring(queryIndex, queryIndex + searchText.value.length), 
      highlight: true 
    })
    
    if (queryIndex + searchText.value.length < result.context.length) {
      parts.push({ 
        text: result.context.substring(queryIndex + searchText.value.length), 
        highlight: false 
      })
    }
    
    return {
      ...result,
      contextParts: parts,
      hover: false
    }
  })
}

// 在fetchPdfUrl函数中添加URL验证
const fetchPdfUrl = async () => {
  try {
    isLoading.value = true
    const id = route.params.id
    const response = await apis.getPdfDetail(id)
    const fileUrl = response.data.data?.file_url;
    
    // 新增URL格式验证
    if (!fileUrl) {
      throw new Error('未获取到有效的PDF地址')
    }
    try {
      new URL(fileUrl); // 验证URL格式
    } catch (err) {
      throw new Error(`PDF地址格式无效: ${fileUrl}`)
    }
    
    pdfUrl.value = fileUrl;
  } catch (err) {
    console.error('获取PDF地址失败:', err)
    error.value = err.message || '获取文档失败，请重试'
  } finally {
    isLoading.value = false
  }
}

const handlePdfError = (err) => {
  console.error('PDF渲染错误:', err)
  error.value = '文档渲染失败，请检查文件格式'
}

// 分页控制
const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    currentBbox.value = [] // 清除高亮
  }
}

const nextPage = () => {
  if (currentPage.value < numPages.value) {
    currentPage.value++
    currentBbox.value = [] // 清除高亮
  }
}

// 跳转到指定位置（页码+bbox）
const goToPosition = (pageNumber, bbox) => {
  if (pageNumber >= 1 && pageNumber <= numPages.value) {
    currentPage.value = pageNumber
    currentBbox.value = bbox
  }
}

const searchInPdf = async () => {
  if (!searchText.value.trim()) return
  
  try {
    isLoading.value = true
    const response = await apis.searchPdf({
      id: route.params.id,
      query: searchText.value
    })
    searchResults.value = processSearchResults(response.data.results || [])
  } catch (err) {
    console.error('搜索失败:', err)
    error.value = '搜索过程中出错'
  } finally {
    isLoading.value = false
  }
}

const retry = () => {
  error.value = ''
  fetchPdfUrl()
}

onMounted(fetchPdfUrl)
</script>

<style scoped>
.detail-page {
  display: flex;
  height: 100vh;
  padding: 20px;
  background-color: #f0f2f5;
  box-sizing: border-box;
  gap: 20px;
}

.card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.left-panel {
  flex: 2;
  display: flex;
  flex-direction: column;
}

.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 400px;
}

.pdf-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  padding: 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #eee;
}

.control-btn {
  padding: 8px 16px;
  background: #4e6ef2;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
}

.control-btn:hover:not(:disabled) {
  background: #3d5afe;
  transform: translateY(-2px);
}

.control-btn:disabled {
  background: #cccccc;
  cursor: not-allowed;
  transform: none;
}

.page-info {
  color: #444;
  font-size: 14px;
  font-weight: 500;
}

.pdf-viewer {
  flex: 1;
  overflow: auto;
}

.search-container {
  display: flex;
  gap: 10px;
  padding: 16px;
  border-bottom: 1px solid #eee;
}

.search-input {
  flex: 1;
  height: 44px;
  padding: 0 16px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  outline: none;
  font-size: 14px;
  transition: all 0.2s ease;
}

.search-input:focus {
  border-color: #4e6ef2;
  box-shadow: 0 0 0 3px rgba(78, 110, 242, 0.1);
}

.search-button {
  width: 44px;
  height: 44px;
  background: #4e6ef2;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-button:hover {
  background: #3d5afe;
  transform: translateY(-2px);
}

.search-icon {
  font-size: 18px;
}

.result-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.result-item {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.result-item:hover {
  background-color: #f0f7ff;
  border-color: #e1f0fe;
  transform: translateX(4px);
}

.result-item.hover {
  background-color: #f0f7ff;
}

.result-page {
  font-size: 12px;
  color: #666;
  margin-bottom: 6px;
  display: inline-block;
  padding: 2px 8px;
  background: #f0f2f5;
  border-radius: 4px;
}

.result-content {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
}

.highlight-text {
  color: #4e6ef2;
  font-weight: 600;
  background-color: rgba(78, 110, 242, 0.1);
  padding: 0 2px;
  border-radius: 2px;
}

.no-result {
  text-align: center;
  padding: 30px 0;
  color: #999;
  font-size: 14px;
}

.loading {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4e6ef2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: #ff6b6b;
}

.retry-btn {
  margin-top: 20px;
  padding: 8px 16px;
  background: #4e6ef2;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.retry-btn:hover {
  background: #3d5afe;
}
</style>