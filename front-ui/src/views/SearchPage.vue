<template>
  <div class="search-page">
    <!-- 搜索区域 -->
    <div class="search-container">
      <div class="search-input-group">
        <!-- 搜索输入框 -->
        <div class="custom-input-wrapper">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="查询科技行业动态..."
            @keyup.enter="handleSearch"
            class="custom-input"
          />
          <span v-if="searchQuery" class="clear-btn" @click="searchQuery = ''">×</span>
        </div>
        <div class="search-btn" @click="handleSearch">智能检索</div>
        <div class="advanced-toggle" @click="toggleAdvancedOptions">
          {{ showAdvancedOptions ? '收起高级选项' : '高级选项' }}
        </div>
      </div>

      <!-- 高级选项 -->
      <div v-if="showAdvancedOptions" class="advanced-options">
        <!-- 时间选择 -->
        <div class="date-picker-group">
          <VueDatePicker
            v-model="startDate"
            placeholder="起始时间"
            :format="formatDate"
            :enable-time-picker="false"
            auto-apply
            @update:model-value="handleDateChange"
            :max-date="endDate"
            text-input
            :text-input-options="{ format: 'yyyy-MM-dd' }"
          />
          <VueDatePicker
            v-model="endDate"
            placeholder="结束时间"
            :format="formatDate"
            :enable-time-picker="false"
            auto-apply
            @update:model-value="handleDateChange"
            :min-date="startDate"
            text-input
            :text-input-options="{ format: 'yyyy-MM-dd' }"
          />
        </div>
        <!-- 标签选项 -->
        <div class="tag-group">
          <el-checkbox-group v-model="selectedTags">
            <el-checkbox v-for="tag in tagOptions" :key="tag.name" :label="tag.name">{{ tag.name }}</el-checkbox>
          </el-checkbox-group>
        </div>
      </div>
    </div>

    <!-- 结果区域 -->
    <div class="results-container">
      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-overlay">
        <div class="spinner"></div>
        <p>正在搜索中...</p>
      </div>

      <!-- 搜索结果 -->
      <div v-if="searchResults" class="search-results">
        <div v-if="searchResults.length > 0">
          <div class="result-count">找到约 {{ totalResults }} 条结果</div>

          <!-- 搜索结果列表 -->
          <div class="result-list">
            <div v-for="(news, index) in searchResults" :key="index" class="result-item" @click="goToDetail(news)">
              <a :href="news.url" target="_blank" class="result-title">
                <!-- 显示高级检索的高亮标题 -->
                <span v-if="showAdvancedOptions" v-html="news.title || news.document_highlight"></span>
                <span v-else>{{ news.title }}</span>
              </a>
              <div class="result-url">{{ formatUrl(news.url) }}</div>
              <div class="result-description">
                <!-- 显示高级检索的高亮内容 -->
                <span v-if="showAdvancedOptions" v-html="news.matched_fragments?.[0]?.highlight || news.description"></span>
                <span v-else>{{ news.description }}</span>
              </div>
              <div class="result-meta">
                <span class="result-date">{{ news.updated_at || news.date }}</span>
                <span class="result-source">{{ news.source }}</span>
                <span class="result-tags">
                  <span v-for="(tag, tagIndex) in news.tags" :key="tagIndex" class="tag">{{ tag }}</span>
                </span>
              </div>
            </div>
          </div>

          <!-- 分页控件 -->
          <div class="pagination">
            <button
              @click="prevPage"
              :disabled="currentPage === 1"
              class="pagination-button prev"
            >
              <i class="el-icon-arrow-left"></i> 上一页
            </button>

            <div class="page-numbers">
              <!-- 首页 -->
              <span
                :class="{ 'active': 1 === currentPage }"
                @click="goToPage(1)"
              >1</span>

              <!-- 前省略号 -->
              <span v-if="currentPage > 4 && totalPages > 5" class="ellipsis">...</span>

              <!-- 动态页码 -->
              <template v-for="page in getDisplayPages()" :key="page">
                <span
                  :class="{ 'active': page === currentPage }"
                  @click="goToPage(page)"
                >
                  {{ page }}
                </span>
              </template>

              <!-- 后省略号 -->
              <span v-if="currentPage < totalPages - 3 && totalPages > 5" class="ellipsis">...</span>

              <!-- 末页 -->
              <span
                v-if="totalPages > 1"
                :class="{ 'active': totalPages === currentPage }"
                @click="goToPage(totalPages)"
              >
                {{ totalPages }}
              </span>
            </div>

            <button
              @click="nextPage"
              :disabled="currentPage === totalPages"
              class="pagination-button next"
            >
              下一页 <i class="el-icon-arrow-right"></i>
            </button>
          </div>
        </div>

        <!-- 无结果提示 -->
        <div v-else class="no-results">
          <div class="no-results-icon">🔍</div>
          <h3>没有找到相关结果</h3>
          <p>请尝试使用不同的关键词或调整筛选条件</p>
        </div>
      </div>

      <!-- 初始状态提示 -->
      <div v-else class="welcome-message">
        <h2>科技资讯检索平台</h2>
        <p>输入关键词获取最新科技行业动态</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import apis from '@/apis'
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ElCheckbox, ElCheckboxGroup } from 'element-plus'
import VueDatePicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import { useRouter } from 'vue-router'

const router = useRouter()

const searchQuery = ref('')
const isLoading = ref(false)
const searchResults = ref(null)
const totalResults = ref(0)
const itemsPerPage = ref(5)
const currentPage = ref(1)
const totalPages = ref(1)

// 高级选项相关
const showAdvancedOptions = ref(false)
const startDate = ref(null)
const endDate = ref(null)
const selectedTags = ref([])
const tagOptions = ref([])

// 缓存已加载的数据页 - 结构：{ searchQuery: { page: results } }
const cachedPages = ref({})

// 日期格式化函数
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toISOString().split('T')[0]
}

// 获取当前搜索查询的缓存键
const getCacheKey = () => {
  return showAdvancedOptions.value 
    ? `advanced:${searchQuery.value}:${selectedTags.value.join(',')}:${startDate.value || ''}:${endDate.value || ''}`
    : `basic:${searchQuery.value}`
}

// 从缓存中获取数据
const getFromCache = (page) => {
  const cacheKey = getCacheKey()
  return cachedPages.value[cacheKey]?.[page]
}

// 将数据存入缓存
const saveToCache = (page, results) => {
  const cacheKey = getCacheKey()
  if (!cachedPages.value[cacheKey]) {
    cachedPages.value[cacheKey] = {}
  }
  cachedPages.value[cacheKey][page] = results
}

// 切换高级选项
const toggleAdvancedOptions = () => {
  if (showAdvancedOptions.value) {
    startDate.value = null
    endDate.value = null
    selectedTags.value = []
  }
  currentPage.value = 1
  showAdvancedOptions.value = !showAdvancedOptions.value
  handleSearch()
}

// 日期变化处理
const handleDateChange = () => {
  currentPage.value = 1
  handleSearch()
}

// 获取显示的页码
const getDisplayPages = () => {
  const pages = []
  const current = currentPage.value
  const total = totalPages.value

  if (total <= 5) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 3) {
      pages.push(2, 3, 4)
    } else if (current >= total - 2) {
      pages.push(total - 3, total - 2, total - 1)
    } else {
      pages.push(current - 1, current, current + 1)
    }
  }
  return pages.filter(p => p > 1 && p < total)
}

// 执行搜索
const handleSearch = async () => {
  // 如果是普通搜索且搜索词为空，则加载默认内容
  if (!showAdvancedOptions.value && !searchQuery.value.trim()) {
    await fetchDefaultSearch()
    return
  }

  isLoading.value = true
  try {
    let res
    const cachedData = getFromCache(currentPage.value)
    
    if (cachedData) {
      searchResults.value = cachedData
    } else {
      if (showAdvancedOptions.value) {
        // 高级检索调用 ES 接口
        res = await apis.getEsSearch(
          searchQuery.value, 
          selectedTags.value,
          startDate.value ? formatDate(startDate.value) : null,
          endDate.value ? formatDate(endDate.value) : null,
          currentPage.value, 
          itemsPerPage.value
        )
      } else {
        // 默认检索调用原接口
        res = await apis.getDefaultSearch(
          searchQuery.value, 
          currentPage.value, 
          itemsPerPage.value
        )
      }
      
      searchResults.value = res.data.results
      totalResults.value = res.data.total
      saveToCache(currentPage.value, res.data.results)
    }
    
    totalPages.value = Math.ceil(totalResults.value / itemsPerPage.value)
  } catch (error) {
    console.error('搜索出错:', error)
    searchResults.value = []
    ElMessage.error('搜索时出现错误')
  } finally {
    isLoading.value = false
  }
}

// 格式化URL
const formatUrl = (url) => {
  try {
    const parsed = new URL(url)
    return `${parsed.hostname}${parsed.pathname.replace(/\/$/, '')}`
  } catch {
    return url
  }
}

// 获取标签选项
const fetchTagOptions = async () => {
  try {
    const res = await apis.getNewsTags()
    if (res.status === 200) {
      tagOptions.value = res.data.data || []
    }
  } catch (error) {
    console.error('获取标签失败:', error)
  }
}

// 获取默认搜索结果
const fetchDefaultSearch = async () => {
  isLoading.value = true
  try {
    const res = await apis.getDefaultSearch(
      '', // 默认搜索为空查询
      currentPage.value, 
      itemsPerPage.value
    )
    
    if (res.status === 200) {
      searchResults.value = res.data.results
      totalResults.value = res.data.total
      totalPages.value = Math.ceil(totalResults.value / itemsPerPage.value)
      saveToCache(currentPage.value, res.data.results)
    }
  } catch (error) {
    console.error('获取默认搜索失败:', error)
    searchResults.value = []
    ElMessage.error('获取默认搜索结果失败')
  } finally {
    isLoading.value = false
  }
}

// 清空搜索框
// const clearSearchQuery = () => {
//   searchQuery.value = ''
//   currentPage.value = 1
//   handleSearch()
// }

// 翻页方法
const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    handleSearch()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    handleSearch()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const goToPage = (page) => {
  currentPage.value = page
  handleSearch()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 在script部分找到goToDetail方法并修改
const goToDetail = (news) => {
  // 假设新闻数据中有id字段
  router.push({ name: 'DetailPage', params: { id: news.id } })
}


onMounted(() => {
  fetchTagOptions()
  // 初始加载默认搜索结果
  fetchDefaultSearch()
})
</script>

<style scoped>
/* 原有的样式保持不变 */
.search-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.search-container {
  margin-bottom: 30px;
}

.search-input-group {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.custom-input-wrapper {
  flex: 1;
  position: relative;
  border: 2px solid #4e6ef2;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(78, 110, 242, 0.2);
}

.custom-input {
  width: 100%;
  height: 50px;
  padding: 0 20px;
  font-size: 16px;
  border: none;
  outline: none;
}

.clear-btn {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #e4e6eb;
  color: #606266;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 18px;
  font-weight: bold;
}

.search-btn {
  height: 50px;
  padding: 0 25px;
  background: #4e6ef2;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s;
}

.search-btn:hover {
  background: #3d5afe;
}

.advanced-toggle {
  height: 50px;
  padding: 0 25px;
  background: #f5f7fa;
  color: #606266;
  border: 1px solid #dcdfe6;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.advanced-toggle:hover {
  background: #ebedf0;
}

.advanced-options {
  width: 80%;
  padding: 20px;
  background: #f9fafb;
  border-radius: 10px;
  border: 1px solid #ebeef5;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.date-picker-group {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.tag-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.results-container {
  min-height: 500px;
}

.loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(78, 110, 242, 0.1);
  border-radius: 50%;
  border-top: 4px solid #4e6ef2;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.welcome-message {
  text-align: center;
  padding: 60px 20px;
  color: #606266;
}

.welcome-message h2 {
  font-size: 28px;
  margin-bottom: 15px;
  color: #1a1a1a;
}

.welcome-message p {
  font-size: 18px;
}

.result-count {
  color: #70757a;
  font-size: 14px;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebebeb;
}

.result-list {
  margin-bottom: 40px;
}

.result-item {
  padding: 20px 0;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.3s;
}

.result-item:hover {
  background-color: #f9fafb;
}

.result-title {
  font-size: 20px;
  color: #1a0dab;
  text-decoration: none;
  display: block;
  margin-bottom: 5px;
  font-weight: normal;
  line-height: 1.3;
}

.result-title:hover {
  text-decoration: underline;
}

.result-url {
  color: #006621;
  font-size: 14px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
}

.result-url:before {
  content: "🔗";
  margin-right: 5px;
}

.result-description {
  color: #545454;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 10px;
}

.result-meta {
  display: flex;
  align-items: center;
  color: #70757a;
  font-size: 13px;
  gap: 15px;
}

.result-date:before {
  content: "📅";
  margin-right: 5px;
}

.result-source:before {
  content: "🏢";
  margin-right: 5px;
}

.result-tags {
  display: flex;
  gap: 8px;
}

.tag {
  background: #f1f3f4;
  color: #5f6368;
  padding: 3px 8px;
  border-radius: 3px;
  font-size: 12px;
}

.no-results {
  text-align: center;
  padding: 60px 20px;
}

.no-results-icon {
  font-size: 60px;
  margin-bottom: 20px;
}

.no-results h3 {
  font-size: 24px;
  color: #202124;
  margin-bottom: 10px;
}

.no-results p {
  font-size: 16px;
  color: #5f6368;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 30px;
  gap: 15px;
}

.pagination-button {
  padding: 10px 20px;
  background: #f8f9fa;
  border: 1px solid #dadce0;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #1a73e8;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.2s;
}

.pagination-button:hover:not(:disabled) {
  background: #e8eaed;
  border-color: #c6c9ce;
}

.pagination-button:disabled {
  color: #9aa0a6;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 5px;
}

.page-numbers span {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #1a73e8;
}

.page-numbers span.active {
  background: #1a73e8;
  color: white;
}

.page-numbers span:not(.active):not(.ellipsis):hover {
  background: #f1f3f4;
}

.ellipsis {
  cursor: default;
  color: #9aa0a6;
}

/* 美化日期选择器 */
:deep(.dp__main) {
  border: 2px solid #4e6ef2;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(78, 110, 242, 0.2);
}

/* 调小时间输入框的高度 */
:deep(.dp__input) {
  height: 36px; /* 调整高度 */
  padding: 0 15px;
  font-size: 14px;
  border: none;
  background: transparent;
}

:deep(.dp__menu) {
  border: 2px solid #4e6ef2;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(78, 110, 242, 0.25);
}

:deep(.dp__today) {
  border: 1px solid #4e6ef2 !important;
}

:deep(.dp__active_date) {
  background: #4e6ef2 !important;
  color: white !important;
}

:deep(.dp__action_row) {
  padding: 10px;
}

:deep(.dp__action_buttons) {
  display: flex;
  gap: 10px;
}

:deep(.dp__action_button) {
  flex: 1;
  padding: 8px 0;
  border-radius: 6px;
  background: #4e6ef2;
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

:deep(.dp__action_button:hover) {
  background: #3d5afe;
}
</style>