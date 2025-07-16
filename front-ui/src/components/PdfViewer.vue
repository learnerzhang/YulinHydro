<template>
  <div class="pdf-container" ref="container">
    <canvas v-for="page in renderedPages" :key="page" :ref="(el) => setCanvasRef(el, page)"></canvas>
    <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
    <!-- 加载指示器 -->
    <div v-if="isLoading" class="loading-indicator">
      <div class="spinner"></div>
      <p>加载PDF中...</p>
    </div>
    <!-- 高亮选区 -->
    <div 
      v-if="highlightArea" 
      class="highlight-area"
      :style="{
        left: `${highlightArea.left}px`,
        top: `${highlightArea.top}px`,
        width: `${highlightArea.width}px`,
        height: `${highlightArea.height}px`
      }"
    ></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, defineProps, defineEmits, nextTick } from 'vue'
import * as pdfjsLib from 'pdfjs-dist'
import 'pdfjs-dist/web/pdf_viewer.css'

// 配置worker路径 - 使用稳定版本
pdfjsLib.GlobalWorkerOptions.workerSrc = '//cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js'

const props = defineProps({
  src: String,
  page: {
    type: Number,
    default: 1
  },
  bbox: {
    type: Array,
    default: () => [] // [x1, y1, x2, y2]
  }
})

const emit = defineEmits(['num-pages', 'page-rendered', 'error', 'loading'])
const errorMessage = ref('')
const highlightArea = ref(null)
const renderedPages = ref([])
const isLoading = ref(false)

const container = ref(null)
const canvasRefs = ref({})
const pdfDoc = ref(null)
const scale = ref(1.5)
const abortController = ref(null) // 用于取消请求

// 加载PDF文档 - 增强错误处理和请求控制
const loadPdf = async () => {
  // 重置状态
  errorMessage.value = ''
  renderedPages.value = []
  isLoading.value = true
  emit('loading', true)
  
  // 取消之前的请求
  if (abortController.value) {
    abortController.value.abort()
  }

  if (!props.src) {
    const err = new Error('请提供有效的PDF地址')
    handleError(err)
    return
  }

  try {
    // 创建新的中止控制器
    abortController.value = new AbortController()
    
    // 完全重置文档
    if (pdfDoc.value) {
      pdfDoc.value.destroy()
      pdfDoc.value = null
    }
    
    let loadingTask;
    
    // 修改loadPdf函数中的fetch部分
    if (typeof props.src === 'string' && props.src.startsWith('http')) {
        // 处理跨域URL - 优化请求配置
        try {
            // 方式1: 直接加载（带更完整的跨域配置）
            loadingTask = pdfjsLib.getDocument({ 
            url: props.src,
            withCredentials: false,
            signal: abortController.value.signal,
            // 新增跨域请求头配置
            httpHeaders: {
                'Access-Control-Request-Method': 'GET',
                'Accept': 'application/pdf'
            }
            })
        } catch (e) {
            // 方式2: 通过fetch先获取数据（优化跨域处理）
            const response = await fetch(props.src, {
            method: 'GET',
            mode: 'cors', // 明确跨域模式
            cache: 'no-store',
            signal: abortController.value.signal,
            headers: {
                'Accept': 'application/pdf'
            }
            })
            
            if (!response.ok) {
            throw new Error(`HTTP错误: ${response.status} (可能是跨域限制或文件不存在)`)
            }
            
            const arrayBuffer = await response.arrayBuffer()
            loadingTask = pdfjsLib.getDocument({
            data: new Uint8Array(arrayBuffer),
            verbosity: 0
            })
        }
    }
    
    // 加载文档
    const doc = await loadingTask.promise
    pdfDoc.value = doc
    emit('num-pages', doc.numPages)
    
    // 渲染页面
    await renderPage(props.page)
  } catch (err) {
    console.error('PDF加载失败:', err)
    handleError(err)
  } finally {
    isLoading.value = false
    emit('loading', false)
  }
}

// 渲染页面
const renderPage = async (pageNumber) => {
  if (!pdfDoc.value || pageNumber < 1 || pageNumber > pdfDoc.value.numPages) {
    return
  }
  
  try {
    const page = await getPageSafely(pdfDoc.value, pageNumber)
    renderedPages.value = [pageNumber]
    
    await nextTick()
    
    const canvas = canvasRefs.value[pageNumber]
    if (!canvas) return
    
    // 设置canvas和渲染
    const viewport = page.getViewport({ scale: scale.value })
    const context = canvas.getContext('2d')
    
    canvas.height = viewport.height
    canvas.width = viewport.width
    
    const renderContext = {
      canvasContext: context,
      viewport: viewport
    }
    
    await page.render(renderContext).promise
    emit('page-rendered', pageNumber)
    
    // 处理高亮
    if (props.bbox.length === 4) {
      calculateHighlightArea(page, props.bbox)
    }
  } catch (err) {
    console.error('渲染页面失败:', err)
    emit('error', err)
    errorMessage.value = '页面渲染失败: ' + err.message
  }
}

// 安全获取页面
const getPageSafely = async (doc, pageNumber) => {
  try {
    return await doc.getPage(pageNumber)
  } catch (e) {
    if (e.message.includes('private member')) {
      // 降级方案
      const loadingTask = pdfjsLib.getDocument(doc._transport)
      const newDoc = await loadingTask.promise
      return newDoc.getPage(pageNumber)
    }
    throw e
  }
}

// 计算高亮区域
const calculateHighlightArea = (page, bbox) => {
  const viewport = page.getViewport({ scale: scale.value })
  const [x1, y1, x2, y2] = bbox
  
  highlightArea.value = {
    left: x1 * viewport.scale,
    top: (viewport.viewBox[3] - y2) * viewport.scale,
    width: (x2 - x1) * viewport.scale,
    height: (y2 - y1) * viewport.scale
  }
  
  // 滚动到高亮区域
  if (container.value) {
    container.value.scrollTo({
      top: highlightArea.value.top - 100,
      behavior: 'smooth'
    })
  }
}

// 设置canvas引用
const setCanvasRef = (el, pageNumber) => {
  if (el) {
    canvasRefs.value[pageNumber] = el
  }
}

// 错误处理函数
const handleError = (err) => {
  let message = '加载PDF时发生错误'
  
  if (err.name === 'AbortError') {
    message = '请求已取消'
  } else if (err.message.includes('Failed to fetch') || err.details?.includes('Failed to fetch')) {
    message = `网络请求失败: 无法获取PDF文件
                可能的解决方案:
                1. 检查网络连接是否正常
                2. 确认PDF文件URL是否可访问
                3. 若为跨域请求，请联系服务器管理员设置CORS头:
                Access-Control-Allow-Origin: * (或当前域名)`
  } else if (err.message.includes('HTTP错误')) {
    message = `服务器返回错误: ${err.message}
可能是文件不存在或权限不足`
  } else if (err.message.includes('private member')) {
    message = 'PDF格式不兼容，请尝试更新PDF查看器'
  } else {
    message = '加载失败: ' + err.message
  }
  
  errorMessage.value = message
  emit('error', err)
}

// 监听属性变化
watch(() => props.src, (newSrc) => {
  if (newSrc) loadPdf()
}, { immediate: false })

watch(() => [props.page, props.bbox], ([newPage]) => {
  if (pdfDoc.value && newPage >= 1 && newPage <= pdfDoc.value.numPages) {
    renderPage(newPage)
  }
}, { deep: true })

onMounted(() => {
  if (props.src) {
    loadPdf()
  }
})

onBeforeUnmount(() => {
  // 取消请求并清理资源
  if (abortController.value) {
    abortController.value.abort()
  }
  if (pdfDoc.value) {
    pdfDoc.value.destroy()
  }
  canvasRefs.value = {}
  renderedPages.value = []
})
</script>

<style scoped>
.pdf-container {
  position: relative;
  overflow: auto;
  height: 100%;
  background-color: #f5f5f5;
  min-height: 600px;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

canvas {
  display: block;
  margin: 0 auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background-color: white;
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.error-message {
  color: #ff4444;
  background-color: #fefefe;
  padding: 16px;
  border-radius: 4px;
  text-align: center;
  margin-top: 20px;
  box-shadow: 0 2px 8px rgba(255, 68, 68, 0.15);
  white-space: pre-line; /* 支持换行 */
}

.highlight-area {
  position: absolute;
  background-color: rgba(255, 255, 0, 0.3);
  border: 1px solid rgba(255, 215, 0, 0.8);
  z-index: 10;
  transition: all 0.3s ease;
  animation: pulse 1.5s infinite;
}

.loading-indicator {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto;
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

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(255, 215, 0, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(255, 215, 0, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(255, 215, 0, 0);
  }
}
</style>
    