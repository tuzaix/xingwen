<template>
  <div class="report-list-container">
    <el-card shadow="never" class="table-card">
      <template #header>
        <div class="table-header">
          <div class="header-left">
            <el-input
              v-model="queryParams.user_id"
              placeholder="用户 ID"
              class="search-input"
              clearable
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
            </el-input>
            <el-select v-model="queryParams.status" placeholder="所有状态" class="status-select" clearable @change="handleSearch">
              <el-option label="生成中" :value="0" />
              <el-option label="已完成" :value="1" />
              <el-option label="生成失败" :value="2" />
            </el-select>
            <el-button type="primary" @click="handleSearch">查询</el-button>
          </div>
          <div class="header-right">
            <el-button type="warning" @click="handleExport">
              <el-icon class="mr-1"><Download /></el-icon> 导出 CSV
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" row-key="id" hover stripe>
        <el-table-column prop="user_name" label="用户姓名" width="120">
          <template #default="{ row }">
            <div class="user-cell">
              <el-avatar :size="24" class="mr-2">{{ row.user_name?.charAt(0) || '?' }}</el-avatar>
              <span class="font-medium">{{ row.user_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="gender" label="性别" width="80">
          <template #default="{ row }">
            <el-tag :type="row.gender === '男' ? '' : 'danger'" size="small" effect="plain">
              {{ row.gender }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="focus_area" label="核心诉求" width="120" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <div class="status-wrapper">
              <el-tag :type="statusMap[row.status].type" size="small" :effect="row.status === 0 ? 'light' : 'dark'">
                <el-icon v-if="row.status === 0" class="is-loading mr-1"><Loading /></el-icon>
                {{ statusMap[row.status].label }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="model_name" label="AI 模型" width="180">
          <template #default="{ row }">
            <el-tag type="info" size="small" effect="plain">{{ row.model_name || systemConfig.ai_model }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="card_code" label="使用卡密" width="180">
          <template #default="{ row }">
            <code class="card-code">{{ row.card_code }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="生成时间" min-width="160">
          <template #default="{ row }">
            <div class="time-column">
              <span class="time">{{ formatDate(row.created_at) }}</span>
              <span class="duration" v-if="row.generation_time">
                耗时: {{ formatDuration(row.generation_time) }}
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="160">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">
              <el-icon class="mr-1"><View /></el-icon> 查看
            </el-button>
            <el-divider direction="vertical" />
            <el-dropdown trigger="click" @command="(cmd: string) => handleCommand(cmd, row)">
              <el-button link type="primary">
                更多 <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="regenerate" :icon="Refresh">重新生成</el-dropdown-item>
                  <el-dropdown-item command="download" :icon="Download">下载 PDF</el-dropdown-item>
                  <el-dropdown-item command="delete" :icon="Delete" divided class="text-danger">删除报告</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.page_size"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSearch"
          @current-change="handleSearch"
        />
      </div>
    </el-card>

    <el-drawer v-model="showDetail" title="全息命理报告详情" size="70%" class="report-drawer">
      <div v-if="currentReport" class="drawer-content">
        <!-- 头部摘要与详细个人信息 -->
        <div class="report-detail-header mb-8">
          <div class="user-profile-section">
            <div class="profile-avatar">
              <el-avatar :size="80" class="user-large-avatar">{{ currentReport.user_name?.charAt(0) }}</el-avatar>
              <el-tag size="small" :type="currentReport.gender === '男' ? '' : 'danger'" class="gender-tag">
                {{ currentReport.gender }}
              </el-tag>
            </div>
            
            <div class="profile-details">
              <div class="profile-row main">
                <h3 class="user-name">{{ currentReport.user_name }}</h3>
                <el-tag size="small" effect="dark" type="warning">{{ currentReport.focus_area }}</el-tag>
              </div>
              
              <div class="info-grid">
                <div class="info-item">
                  <span class="label">出生日期</span>
                  <span class="value">{{ formatDate(currentReport.birthday) }} ({{ currentReport.calendar_type === 'lunar' ? '农历' : '公历' }})</span>
                </div>
                <div class="info-item">
                  <span class="label">所属地区</span>
                  <span class="value">{{ currentReport.location || '未知' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">生肖星座</span>
                  <span class="value">{{ currentReport.zodiac || '未知' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">生辰八字</span>
                  <span class="value">{{ currentReport.bazi || '解析中...' }}</span>
                </div>
                <div class="info-item full-width">
                  <span class="label">八字喜用神</span>
                  <span class="value">{{ currentReport.bazi_favorable_elements || '解析中...' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">MBTI 类型</span>
                  <span class="value">{{ currentReport.mbti || '未知' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">使用卡密</span>
                  <span class="value font-mono">{{ currentReport.card_code }}</span>
                </div>
                <div class="info-item">
                  <span class="label">用户 ID</span>
                  <span class="value">{{ currentReport.user_id }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="report-meta-info">
            <div class="meta-item">
              <label>报告状态</label>
              <el-tag :type="statusMap[currentReport.status].type" effect="dark">{{ statusMap[currentReport.status].label }}</el-tag>
            </div>
            <div class="meta-item">
              <label>AI 模型</label>
              <span class="model-badge">{{ currentReport.model_name || systemConfig.ai_model }}</span>
            </div>
            <div class="meta-item">
              <label>生成耗时</label>
              <span class="duration-text">{{ formatDuration(currentReport.generation_time) }}</span>
            </div>
          </div>
        </div>

        <el-tabs v-model="activeTab" class="report-tabs">
          <el-tab-pane label="报告内容" name="content">
            <div class="report-content-wrapper">
              <div class="content-toolbar">
                <el-button type="primary" size="small" :icon="Printer" @click="handlePrint">打印报告</el-button>
                <el-button size="small" :icon="CopyDocument" @click="copyReportContent">复制文本</el-button>
              </div>
              
              <!-- 优先展示结构化章节内容 -->
              <div v-if="currentReport.sections && currentReport.sections.length > 0" class="structured-report">
                <div v-for="(section, index) in currentReport.sections" :key="index" class="report-section">
                  <h2 class="section-title">{{ section.chapter_title }}</h2>
                  
                  <!-- 展示高亮标签 -->
                  <div v-if="section.highlights && section.highlights.length > 0" class="section-highlights">
                    <el-tag 
                      v-for="tag in section.highlights" 
                      :key="tag" 
                      size="small" 
                      effect="dark" 
                      class="highlight-tag"
                    >
                      {{ tag }}
                    </el-tag>
                  </div>

                  <div class="section-paragraphs">
                    <p v-for="(p, pIdx) in section.paragraphs" :key="pIdx" class="paragraph">
                      {{ p }}
                    </p>
                  </div>
                </div>
              </div>

              <!-- 兜底展示 Markdown 内容 -->
              <div v-else class="prose-container" v-html="renderMarkdown(currentReport.content || '')"></div>

              <div v-if="!currentReport.content && !currentReport.sections?.length && currentReport.status === 0" class="loading-content">
                <el-icon class="is-loading"><Loading /></el-icon>
                <p>正在通灵中，请稍候... (进度: {{ currentReport.progress }}%)</p>
                <p class="text-xs mt-2 text-gray-400">{{ currentReport.progress_desc }}</p>
              </div>
              <div v-if="!currentReport.content && !currentReport.sections?.length && currentReport.status === 2" class="error-content">
                <el-icon><CircleClose /></el-icon>
                <p>生成失败: {{ currentReport.error_msg || '未知错误' }}</p>
                <el-button type="primary" plain size="small" class="mt-4" @click="handleRegenerate(currentReport.id)">重试生成</el-button>
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="手相特征" name="features">
            <div class="palm-analysis-container" v-if="currentReport.palm_features">
              <h4 class="section-subtitle mb-6">星纹 AI 特征解析结果</h4>
              
              <div class="hand-analysis-grid">
                <!-- 左手解析 (先天) -->
                <div class="hand-analysis-card left">
                  <div class="hand-visual">
                    <div class="hand-label">左手 (先天)</div>
                    <el-image 
                      :src="getFullImageUrl(currentReport.left_hand_image)" 
                      :preview-src-list="[getFullImageUrl(currentReport.left_hand_image)]"
                      class="fixed-palm-image"
                      fit="cover"
                    >
                      <template #error><div class="image-error">图片加载失败</div></template>
                    </el-image>
                  </div>
                  
                  <div class="hand-data" v-if="currentReport.palm_features.left">
                    <div class="feature-group">
                      <div class="group-title">基础掌型</div>
                      <div class="palm-type-badge">{{ currentReport.palm_features.left.hand_type || '未识别' }}</div>
                    </div>
                    
                    <div class="feature-group">
                      <div class="group-title">主线解析</div>
                      <div class="line-list">
                        <div class="line-row">
                          <span class="l">生命线</span>
                          <span class="v">{{ currentReport.palm_features.left.life_line || '未识别' }}</span>
                        </div>
                        <div class="line-row">
                          <span class="l">智慧线</span>
                          <span class="v">{{ currentReport.palm_features.left.head_line || '未识别' }}</span>
                        </div>
                        <div class="line-row">
                          <span class="l">感情线</span>
                          <span class="v">{{ currentReport.palm_features.left.heart_line || '未识别' }}</span>
                        </div>
                        <div class="line-row" v-if="currentReport.palm_features.left.fate_line">
                          <span class="l">事业线</span>
                          <span class="v">{{ currentReport.palm_features.left.fate_line }}</span>
                        </div>
                      </div>
                    </div>

                    <div class="feature-group" v-if="currentReport.palm_features.left.mounts">
                      <div class="group-title">掌丘表现</div>
                      <div class="mounts-text">{{ currentReport.palm_features.left.mounts }}</div>
                    </div>

                    <div class="feature-group" v-if="currentReport.palm_features.left.special_marks?.length">
                      <div class="group-title">全息特征</div>
                      <div class="feature-tag-list">
                        <el-tag v-for="f in currentReport.palm_features.left.special_marks" :key="f" size="small" effect="light" class="f-tag">
                          {{ f }}
                        </el-tag>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 右手解析 (后天) -->
                <div class="hand-analysis-card right">
                  <div class="hand-visual">
                    <div class="hand-label">右手 (后天)</div>
                    <el-image 
                      :src="getFullImageUrl(currentReport.right_hand_image)" 
                      :preview-src-list="[getFullImageUrl(currentReport.right_hand_image)]"
                      class="fixed-palm-image"
                      fit="cover"
                    >
                      <template #error><div class="image-error">图片加载失败</div></template>
                    </el-image>
                  </div>
                  
                  <div class="hand-data" v-if="currentReport.palm_features.right">
                    <div class="feature-group">
                      <div class="group-title">基础掌型</div>
                      <div class="palm-type-badge">{{ currentReport.palm_features.right.hand_type || '未识别' }}</div>
                    </div>
                    
                    <div class="feature-group">
                      <div class="group-title">主线解析</div>
                      <div class="line-list">
                        <div class="line-row">
                          <span class="l">生命线</span>
                          <span class="v">{{ currentReport.palm_features.right.life_line || '未识别' }}</span>
                        </div>
                        <div class="line-row">
                          <span class="l">智慧线</span>
                           <span class="v">{{ currentReport.palm_features.right.head_line || '未识别' }}</span>
                        </div>
                        <div class="line-row">
                          <span class="l">感情线</span>
                          <span class="v">{{ currentReport.palm_features.right.heart_line || '未识别' }}</span>
                        </div>
                        <div class="line-row" v-if="currentReport.palm_features.right.fate_line">
                          <span class="l">事业线</span>
                          <span class="v">{{ currentReport.palm_features.right.fate_line }}</span>
                        </div>
                      </div>
                    </div>

                    <div class="feature-group" v-if="currentReport.palm_features.right.mounts">
                      <div class="group-title">掌丘表现</div>
                      <div class="mounts-text">{{ currentReport.palm_features.right.mounts }}</div>
                    </div>

                    <div class="feature-group" v-if="currentReport.palm_features.right.special_marks?.length">
                      <div class="group-title">全息特征</div>
                      <div class="feature-tag-list">
                        <el-tag v-for="f in currentReport.palm_features.right.special_marks" :key="f" size="small" effect="light" class="f-tag">
                          {{ f }}
                        </el-tag>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <el-collapse class="mt-8 border-none">
                <el-collapse-item title="查看底层 JSON 报文" name="1">
                  <pre class="json-block">{{ JSON.stringify(currentReport.palm_features, null, 2) }}</pre>
                </el-collapse-item>
              </el-collapse>
            </div>
            <div v-else class="no-data-placeholder">
              <el-icon><CircleClose /></el-icon>
              <p>暂无特征数据，请检查报告生成状态</p>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  User, Loading, Download, View, Refresh, 
  Delete, ArrowDown, Printer, CopyDocument,
  CircleClose, Pointer
} from '@element-plus/icons-vue'
import request from '../utils/request'
import { marked } from 'marked'
import useClipboard from 'vue-clipboard3'

const { toClipboard } = useClipboard()
const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const showDetail = ref(false)
const currentReport = ref<any>(null)
const activeTab = ref('content')
const systemConfig = ref({
  ai_model: 'gemini-3-flash-preview',
  project_name: '星纹 AI'
})

const queryParams = reactive({
  page: 1,
  page_size: 20,
  status: null,
  user_id: ''
})

const statusMap: any = {
  0: { label: '生成中', type: 'warning' },
  1: { label: '已完成', type: 'success' },
  2: { label: '失败', type: 'danger' }
}

const formatDate = (dateStr: string, onlyDate = false) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  if (onlyDate) return date.toLocaleDateString('zh-CN')
  return date.toLocaleString('zh-CN')
}

const formatDuration = (seconds: number) => {
  if (!seconds) return '-'
  if (seconds < 60) return `${seconds.toFixed(0)}秒`
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}分${secs}秒`
}

const maskUserId = (id: string) => {
  if (!id) return '-'
  if (id.length <= 8) return id
  return id.substring(0, 4) + '****' + id.substring(id.length - 4)
}

const renderMarkdown = (content: string) => {
  if (!content) return ''
  return marked.parse(content)
}

const getFullImageUrl = (path: string) => {
  if (!path) return ''
  // 获取 API 基础路径，并提取出主机地址（去掉 /api/v1）
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || ''
  const hostUrl = apiBaseUrl.replace(/\/api\/v1\/?$/, '') || 'http://localhost:8000'
  
  // 如果已经是完整路径，则不再拼接前缀
  if (path.startsWith('http')) {
    return path
  }
  
  // 如果是以 / 开头（通常是 /uploads/...），直接拼接主机地址
  if (path.startsWith('/')) {
    return `${hostUrl}${path}`
  }
  
  // 数据库中存储的是纯文件名，需要拼接路径前缀
  return `${hostUrl}/uploads/images/${path}`
}

const handleSearch = async () => {
  loading.value = true
  try {
    console.log('Fetching reports with params:', queryParams)
    const res: any = await request.get('/report/', { params: queryParams })
    if (res && res.items) {
      tableData.value = res.items
      total.value = res.total
    } else {
      console.warn('Unexpected response format for reports:', res)
      tableData.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('Failed to fetch reports:', error)
    tableData.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const fetchConfig = async () => {
  try {
    const res: any = await request.get('/stats/config')
    systemConfig.value = res
  } catch (error) {
    console.error('Failed to fetch system config:', error)
  }
}

const viewDetail = (row: any) => {
  currentReport.value = row
  showDetail.value = true
  activeTab.value = 'content'
}

const handleCommand = (command: string, row: any) => {
  if (command === 'regenerate') {
    handleRegenerate(row.id)
  } else if (command === 'delete') {
    handleDelete(row.id)
  } else if (command === 'download') {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1'
    const downloadUrl = `${baseUrl}/report/${row.id}/pdf`
    
    const link = document.createElement('a')
    link.href = downloadUrl
    link.setAttribute('download', `星纹报告_${row.user_name}.pdf`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

const handleRegenerate = async (id: string) => {
  try {
    await request.post(`/report/${id}/regenerate`)
    ElMessage.success('重构请求已提交')
    handleSearch()
  } catch (error) {
    console.error(error)
  }
}

const handleDelete = (id: string) => {
  ElMessageBox.confirm('确定要永久删除该报告吗？', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await request.delete(`/report/${id}`)
      ElMessage.success('删除成功')
      handleSearch()
    } catch (error) {
      console.error(error)
    }
  })
}

const copyReportContent = async () => {
  if (!currentReport.value?.content) return
  try {
    await toClipboard(currentReport.value.content)
    ElMessage.success('报告内容已复制')
  } catch (e) {
    ElMessage.error('复制失败')
  }
}

const handleExport = async () => {
  try {
    const token = localStorage.getItem('token')
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1'
    window.open(`${baseUrl}/report/export/csv?token=${token}`, '_blank')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const handlePrint = () => {
  const printWindow = window.open('', '_blank')
  if (!printWindow) return
  
  const content = renderMarkdown(currentReport.value.content)
  const styles = `
    body { font-family: "Noto Serif SC", serif; padding: 40px; color: #1a1a1a; line-height: 1.8; }
    h1 { text-align: center; color: #b45309; margin-bottom: 40px; }
    h2 { border-bottom: 2px solid #fde68a; padding-bottom: 10px; margin-top: 30px; color: #92400e; }
    p { margin-bottom: 1.2em; text-indent: 2em; }
    .header-info { text-align: center; font-size: 14px; color: #666; margin-bottom: 40px; border-bottom: 1px dashed #ddd; padding-bottom: 20px; }
  `
  
  printWindow.document.write(`
    <html>
      <head>
        <title>${currentReport.value.user_name}的星纹报告</title>
        <style>${styles}</style>
      </head>
      <body>
        <h1>星纹全息命理报告</h1>
        <div class="header-info">
          姓名：${currentReport.value.user_name} | 性别：${currentReport.value.gender} | 生日：${formatDate(currentReport.value.birthday)}
          <br/>
          生成时间：${formatDate(currentReport.value.created_at)}
        </div>
        <div class="content">${content}</div>
        <script>window.print();<\/script>
      </body>
    </html>
  `)
  printWindow.document.close()
}

onMounted(() => {
  fetchConfig()
  handleSearch()
})
</script>

<style scoped>
.report-list-container {
  animation: fadeIn 0.5s ease-out;
}

.table-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  gap: 12px;
}

.search-input {
  width: 240px;
}

.status-select {
  width: 130px;
}

.user-cell {
  display: flex;
  align-items: center;
}

.time-column {
  display: flex;
  flex-direction: column;
}

.time {
  font-size: 13px;
  color: #334155;
}

.duration {
  font-size: 11px;
  color: #94a3b8;
}

.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

/* Drawer Styles */
.drawer-content {
  padding: 0 24px 24px;
}

.report-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 24px;
  background-color: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.user-profile-section {
  display: flex;
  gap: 24px;
  flex: 1;
}

.profile-avatar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.user-large-avatar {
  background-color: #6366f1;
  font-size: 32px;
  font-weight: bold;
}

.gender-tag {
  border-radius: 10px;
}

.profile-details {
  flex: 1;
}

.profile-row.main {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.user-name {
  margin: 0;
  font-size: 26px;
  font-weight: bold;
  color: #1e293b;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px 24px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-item.full-width {
  grid-column: span 2;
}

.info-item .label {
  font-size: 14px;
  color: #94a3b8;
}

.info-item .value {
  font-size: 16px;
  color: #334155;
  font-weight: 500;
}

.report-meta-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-left: 32px;
  border-left: 1px solid #e2e8f0;
  min-width: 140px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.meta-item label {
  font-size: 14px;
  color: #94a3b8;
}

.model-badge {
  font-size: 14px;
  color: #6366f1;
  font-weight: bold;
  background: #eef2ff;
  padding: 2px 8px;
  border-radius: 4px;
}

.duration-text {
  font-size: 14px;
  color: #64748b;
}

.report-content-wrapper {
  position: relative;
  background-color: #f8fafc;
  border-radius: 12px;
  padding: 24px;
  min-height: 400px;
}

.content-toolbar {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-bottom: 20px;
}

.prose-container {
  font-family: "Noto Serif SC", serif;
  line-height: 1.8;
  color: #334155;
}

.prose-container :deep(h2) {
  color: #1e293b;
  border-left: 4px solid #6366f1;
  padding-left: 12px;
  margin-top: 32px;
}

/* Structured Report Styles */
.structured-report {
  font-family: "Noto Serif SC", serif;
}

.report-section {
  margin-bottom: 40px;
}

.section-title {
  font-size: 1.7rem;
  color: #1e293b;
  border-left: 4px solid #6366f1;
  padding-left: 16px;
  margin-bottom: 16px;
  font-weight: bold;
}

.section-highlights {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
  padding-left: 20px;
}

.highlight-tag {
  background-color: #6366f1;
  border-color: #6366f1;
  font-size: 14px;
  padding: 10px 14px;
  height: auto;
}

.card-code {
  font-family: monospace;
  background-color: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  color: #475569;
  font-size: 12px;
}

.section-paragraphs {
  padding: 0 20px;
}

.paragraph {
  text-indent: 2em;
  margin-bottom: 1.5em;
  line-height: 1.8;
  color: #334155;
  font-size: 1.2rem;
  text-align: justify;
}

.loading-content, .error-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #94a3b8;
}

.loading-content .el-icon {
  font-size: 40px;
  margin-bottom: 16px;
  color: #6366f1;
}

.error-content .el-icon {
  font-size: 40px;
  margin-bottom: 16px;
  color: #ef4444;
}

.palm-features-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.palm-image-card {
  background-color: #f8fafc;
  padding: 12px;
  border-radius: 8px;
}

.palm-image-card .card-title {
  font-size: 12px;
  color: #64748b;
  text-align: center;
  margin-bottom: 8px;
}

.palm-image {
  width: 100%;
  height: 300px;
  border-radius: 4px;
}

.image-error {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  background-color: #f1f5f9;
  color: #cbd5e1;
  font-size: 12px;
}

/* Palm Features Display Styles */
.section-subtitle {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 8px;
}

.hand-analysis-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.hand-analysis-card {
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e2e8f0;
}

.hand-analysis-card.left {
  border-top: 4px solid #6366f1;
}

.hand-analysis-card.right {
  border-top: 4px solid #f59e0b;
}

.hand-visual {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.hand-label {
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
  background: #f1f5f9;
  padding: 4px 16px;
  border-radius: 20px;
}

.fixed-palm-image {
  width: 280px;
  height: 380px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  border: 4px solid #fff;
}

.hand-data {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.group-title {
  font-size: 14px;
  color: #94a3b8;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.palm-type-badge {
  font-size: 20px;
  font-weight: bold;
  color: #1e293b;
  padding: 8px 0;
}

.line-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.line-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 10px;
  background: #f8fafc;
  border-radius: 6px;
}

.line-row .l {
  font-size: 15px;
  color: #6366f1;
  font-weight: 600;
  white-space: nowrap;
  background: #eef2ff;
  padding: 2px 8px;
  border-radius: 4px;
}

.line-row .v {
  font-size: 15px;
  color: #334155;
  line-height: 1.5;
}

.feature-tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.f-tag {
  border-radius: 4px;
  font-size: 14px;
  padding: 12px 16px;
  height: auto;
}

.mounts-text {
  font-size: 15px;
  color: #475569;
  line-height: 1.6;
  background: #fdfaf2;
  padding: 10px;
  border-radius: 6px;
  border: 1px solid #fef3c7;
}

.no-data-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #94a3b8;
  gap: 12px;
}

.no-data-placeholder .el-icon {
  font-size: 40px;
}

.json-block {
  background-color: #1e293b;
  color: #e2e8f0;
  padding: 16px;
  border-radius: 8px;
  font-size: 12px;
  overflow-x: auto;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

:deep(.el-table__header th) {
  background-color: #f8fafc;
  color: #64748b;
  font-weight: 600;
}
</style>
