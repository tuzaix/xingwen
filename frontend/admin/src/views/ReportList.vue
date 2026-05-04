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
            <div class="profile-avatar-wrapper">
              <el-avatar :size="100" class="user-large-avatar" :src="currentReport.gender === '男' ? '' : ''">
                {{ currentReport.user_name?.charAt(0) }}
              </el-avatar>
              <div class="gender-badge" :class="currentReport.gender === '男' ? 'male' : 'female'">
                {{ currentReport.gender === '男' ? '♂' : '♀' }}
              </div>
            </div>
            
            <div class="profile-main">
              <div class="name-row">
                <h3 class="user-name">{{ currentReport.user_name }}</h3>
                <el-tag size="default" effect="dark" type="warning" class="focus-tag">{{ currentReport.focus_area }}</el-tag>
              </div>
              
              <div class="info-grid-modern">
                <div class="info-card">
                  <div class="card-label">
                    <el-icon><Calendar /></el-icon> 出生日期
                    <el-tag size="small" :type="currentReport.calendar_type === 'lunar' ? 'warning' : 'info'" effect="plain" class="calendar-tag-mini">
                      {{ currentReport.calendar_type === 'lunar' ? '农历' : '公历' }}
                    </el-tag>
                  </div>
                  <div class="card-value">{{ formatDate(currentReport.birthday) }}</div>
                </div>
                
                <div class="info-card">
                  <div class="card-label"><el-icon><Location /></el-icon> 所属地区</div>
                  <div class="card-value">{{ currentReport.location || '未知' }}</div>
                </div>
                
                <div class="info-card">
                  <div class="card-label"><el-icon><Compass /></el-icon> 生肖星座</div>
                  <div class="card-value">{{ currentReport.zodiac || '未知' }}</div>
                </div>

                <div class="info-card">
                  <div class="card-label"><el-icon><MagicStick /></el-icon> 生辰八字</div>
                  <div class="card-value bazi-value">{{ currentReport.bazi || '解析中...' }}</div>
                </div>

                <div class="info-card full-row">
                  <div class="card-label"><el-icon><ElementPlus /></el-icon> 八字喜用神</div>
                  <div class="card-value highlight-value">{{ currentReport.bazi_favorable_elements || '解析中...' }}</div>
                </div>

                <div class="info-card">
                  <div class="card-label"><el-icon><ChatLineRound /></el-icon> MBTI 类型</div>
                  <div class="card-value">{{ currentReport.mbti || '未知' }}</div>
                </div>

                <div class="info-card">
                  <div class="card-label"><el-icon><Key /></el-icon> 使用卡密</div>
                  <div class="card-value font-mono">{{ currentReport.card_code }}</div>
                </div>
              </div>
            </div>
          </div>

          <div class="report-side-stats">
            <div class="stat-block">
              <div class="stat-label">报告状态</div>
              <el-tag :type="statusMap[currentReport.status].type" effect="dark" size="large">{{ statusMap[currentReport.status].label }}</el-tag>
            </div>
            <div class="stat-block">
              <div class="stat-label">AI 模型</div>
              <div class="model-name-text">{{ currentReport.model_name || systemConfig.ai_model }}</div>
            </div>
            <div class="stat-block">
              <div class="stat-label">生成耗时</div>
              <div class="duration-badge">{{ formatDuration(currentReport.generation_time) }}</div>
            </div>
            <div class="stat-block">
              <div class="stat-label">用户 ID</div>
              <div class="uid-text">{{ currentReport.user_id }}</div>
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
  
  // 如果秒数是 1，说明是后端标记的“时间未知”
  if (date.getSeconds() === 1) {
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    }).replace(/\//g, '-') + ' (出生时间未知)'
  }

  if (onlyDate) {
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    }).replace(/\//g, '-')
  }
  
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).replace(/\//g, '-')
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

/* Drawer Styles Refactored */
.drawer-content {
  padding: 0 32px 32px;
}

.report-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: stretch;
  padding: 32px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
}

.user-profile-section {
  display: flex;
  gap: 40px;
  flex: 1;
}

.profile-avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}

.user-large-avatar {
  background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%);
  font-size: 48px;
  font-weight: bold;
  border: 4px solid #fff;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.gender-badge {
  position: absolute;
  bottom: 5px;
  right: 5px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.gender-badge.male {
  background-color: #3b82f6;
  color: #fff;
}

.gender-badge.female {
  background-color: #ec4899;
  color: #fff;
}

.profile-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.name-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-name {
  margin: 0;
  font-size: 32px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.025em;
}

.focus-tag {
  font-weight: 600;
  letter-spacing: 0.05em;
  padding: 0 12px;
}

.info-grid-modern {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.info-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 10px;
  border: 1px solid rgba(226, 232, 240, 0.8);
  transition: all 0.2s ease;
}

.info-card:hover {
  background: #fff;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.info-card.full-row {
  grid-column: span 3;
  background: linear-gradient(to right, rgba(251, 191, 36, 0.05), transparent);
  border-left: 3px solid #fbbf24;
}

.card-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #94a3b8;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.card-label .el-icon {
  font-size: 14px;
}

.card-value {
  font-size: 16px;
  color: #334155;
  font-weight: 600;
}

.bazi-value {
  color: #1e293b;
  font-family: "Noto Serif SC", serif;
}

.highlight-value {
  color: #b45309;
  font-size: 18px;
}

.calendar-tag-mini {
  height: 16px;
  line-height: 14px;
  padding: 0 4px;
  font-size: 10px;
  margin-left: 4px;
}

.report-side-stats {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-left: 40px;
  border-left: 2px dashed #e2e8f0;
  min-width: 180px;
}

.stat-block {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.stat-label {
  font-size: 13px;
  color: #94a3b8;
  font-weight: 600;
}

.model-name-text {
  font-size: 14px;
  font-weight: 700;
  color: #6366f1;
  background: #eef2ff;
  padding: 4px 12px;
  border-radius: 6px;
  border: 1px solid #c7d2fe;
}

.duration-badge {
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
  background: #f1f5f9;
  padding: 4px 10px;
  border-radius: 6px;
}

.uid-text {
  font-size: 12px;
  font-family: monospace;
  color: #94a3b8;
}

.report-content-wrapper {
  position: relative;
  background-color: #fff;
  border-radius: 16px;
  padding: 40px;
  min-height: 500px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
  border: 1px solid #f1f5f9;
}

.content-toolbar {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-bottom: 32px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f1f5f9;
}

.prose-container {
  font-family: "Inter", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  line-height: 1.8;
  color: #334155;
  font-size: 16px;
}

.prose-container :deep(h2) {
  color: #0f172a;
  font-size: 24px;
  font-weight: 800;
  border-left: 6px solid #6366f1;
  padding-left: 16px;
  margin: 40px 0 20px;
  letter-spacing: -0.025em;
}

.prose-container :deep(p) {
  margin-bottom: 1.5em;
  text-align: justify;
}

/* Structured Report Styles */
.structured-report {
  font-family: "Inter", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}

.report-section {
  margin-bottom: 48px;
}

.section-title {
  font-size: 24px;
  color: #0f172a;
  border-left: 6px solid #6366f1;
  padding-left: 16px;
  margin-bottom: 24px;
  font-weight: 800;
  letter-spacing: -0.025em;
  display: flex;
  align-items: center;
}

.section-highlights {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 24px;
  padding-left: 22px;
}

.highlight-tag {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border: none;
  font-size: 13px;
  font-weight: 600;
  padding: 8px 16px;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.2);
  color: #fff;
}

.section-paragraphs {
  padding-left: 22px;
}

.paragraph {
  text-indent: 0;
  margin-bottom: 1.25em;
  line-height: 1.85;
  color: #475569;
  font-size: 16px;
  text-align: justify;
  font-weight: 400;
}

.paragraph:last-child {
  margin-bottom: 0;
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
