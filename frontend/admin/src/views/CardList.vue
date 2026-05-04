<template>
  <div class="card-list-container">
    <!-- 统计概览 -->
    <el-row :gutter="20" class="mb-6">
      <el-col :span="6" v-for="item in stats" :key="item.label">
        <div class="stats-mini-card">
          <div class="label">{{ item.label }}</div>
          <div class="value">{{ item.value }}</div>
        </div>
      </el-col>
    </el-row>

    <!-- 操作区域 -->
    <el-card shadow="never" class="table-card">
      <template #header>
        <div class="table-header">
          <div class="header-left">
            <el-input
              v-model="queryParams.card_code"
              placeholder="搜索卡密"
              class="search-input"
              clearable
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select
              v-model="queryParams.batch_no"
              placeholder="选择批次号"
              class="batch-select"
              clearable
              filterable
              @change="handleSearch"
            >
              <template #prefix>
                <el-icon><CollectionTag /></el-icon>
              </template>
              <el-option
                v-for="item in batchOptions"
                :key="item"
                :label="item"
                :value="item"
              />
            </el-select>
            <el-select v-model="queryParams.status" placeholder="所有状态" class="status-select" clearable @change="handleSearch">
              <el-option label="未使用" :value="0" />
              <el-option label="已使用" :value="1" />
              <el-option label="已过期" :value="2" />
              <el-option label="已作废" :value="3" />
            </el-select>
            <el-button type="primary" @click="handleSearch">查询</el-button>
          </div>
          <div class="header-right">
            <el-button type="success" @click="showGenerateDialog = true">
              <el-icon class="mr-1"><Plus /></el-icon> 批量生成
            </el-button>
            <el-button type="warning" @click="handleExport">
              <el-icon class="mr-1"><Download /></el-icon> 导出
            </el-button>
          </div>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table :data="tableData" v-loading="loading" row-key="id" hover stripe>
        <el-table-column label="卡密编号" min-width="180">
          <template #default="{ row }">
            <div class="code-wrapper">
              <span class="code-text">{{ formatCode(row.card_code) }}</span>
              <el-button link type="primary" size="small" @click="copyCode(row.card_code)">
                <el-icon><CopyDocument /></el-icon>
              </el-button>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="card_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.card_type === 'year' ? 'warning' : 'info'" effect="light">
              {{ typeMap[row.card_type] || row.card_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-badge :type="statusMap[row.status].type" is-dot class="status-badge" />
            <span :class="'status-text text-' + statusMap[row.status].type">
              {{ statusMap[row.status].label }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="expire_at" label="有效期" width="160">
          <template #default="{ row }">
            <div class="time-column">
              <div class="time">{{ formatDate(row.expire_at) }}</div>
              <div class="relative-time">{{ getRelativeTime(row.expire_at) }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="used_at" label="核销时间" width="160">
          <template #default="{ row }">
            <span v-if="row.used_at" class="time">{{ formatDate(row.used_at) }}</span>
            <span v-else class="text-gray-400">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="batch_no" label="批次" width="150" show-overflow-tooltip />
        <el-table-column label="操作" fixed="right" width="120">
          <template #default="{ row }">
            <el-button link type="primary" @click="showDetail(row)">详情</el-button>
            <el-divider direction="vertical" />
            <el-popconfirm
              v-if="row.status === 0"
              title="确定要作废该卡密吗？"
              confirm-button-text="确定"
              cancel-button-text="取消"
              @confirm="handleRevoke(row.id)"
            >
              <template #reference>
                <el-button link type="danger">作废</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
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

    <!-- 生成对话框 -->
    <el-dialog v-model="showGenerateDialog" title="批量生成卡密" width="450px" border-radius="12px">
      <el-form :model="generateForm" label-position="top" class="generate-form">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="生成数量">
              <el-input-number v-model="generateForm.count" :min="1" :max="1000" class="w-full" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="卡密类型">
              <el-select v-model="generateForm.card_type" class="w-full">
                <el-option label="次卡" value="once" />
                <el-option label="月卡" value="month" />
                <el-option label="年卡" value="year" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="有效期 (天)">
          <el-input-number v-model="generateForm.valid_days" :min="1" class="w-full" />
        </el-form-item>
        <el-form-item label="渠道备注">
          <el-input v-model="generateForm.channel" placeholder="如：官方渠道、某代销商" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showGenerateDialog = false">取消</el-button>
          <el-button type="primary" :loading="generating" @click="handleGenerate">立即生成</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Plus, Download, CopyDocument, CollectionTag } from '@element-plus/icons-vue'
import request from '../utils/request'
import useClipboard from 'vue-clipboard3'

const { toClipboard } = useClipboard()
const loading = ref(false)
const generating = ref(false)
const showGenerateDialog = ref(false)
const tableData = ref([])
const total = ref(0)
const batchOptions = ref<string[]>([])
const stats = ref([
  { label: '总卡密数', value: '0' },
  { label: '待核销', value: '0' },
  { label: '已核销', value: '0' },
  { label: '已失效', value: '0' }
])

const queryParams = reactive({
  page: 1,
  page_size: 20,
  status: 0,
  card_code: '',
  batch_no: ''
})

const generateForm = reactive({
  count: 100,
  card_type: 'once',
  valid_days: 365,
  channel: 'official'
})

const typeMap: any = {
  once: '次卡',
  month: '月卡',
  year: '年卡'
}

const statusMap: any = {
  0: { label: '未使用', type: 'success' },
  1: { label: '已使用', type: 'info' },
  2: { label: '已过期', type: 'warning' },
  3: { label: '已作废', type: 'danger' }
}

const formatCode = (code: string) => {
  return code.match(/.{1,4}/g)?.join('-') || code
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getRelativeTime = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = date.getTime() - now.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days < 0) return '已过期'
  if (days === 0) return '今日到期'
  return `${days}天后到期`
}

const handleSearch = async () => {
  loading.value = true
  try {
    const res: any = await request.get('/card/', { params: queryParams })
    tableData.value = res.items
    total.value = res.total
    
    // Update simple stats from result if available, or fetch separately
    // For now, just a placeholder
    stats.value[0].value = res.total.toString()
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const copyCode = async (code: string) => {
  try {
    await toClipboard(code)
    ElMessage.success('卡密已复制')
  } catch (e) {
    ElMessage.error('复制失败')
  }
}

const handleGenerate = async () => {
  generating.value = true
  try {
    await request.post('/card/generate', generateForm)
    ElMessage.success('批量生成成功')
    showGenerateDialog.value = false
    handleSearch()
  } catch (error) {
    console.error(error)
  } finally {
    generating.value = false
  }
}

const handleRevoke = async (id: number) => {
  try {
    await request.post(`/card/${id}/revoke`)
    ElMessage.success('卡密已作废')
    handleSearch()
  } catch (error) {
    console.error(error)
  }
}

const handleExport = () => {
  if (tableData.value.length === 0) {
    ElMessage.warning('没有可导出的数据')
    return
  }
  
  const headers = ['卡密', '批次号', '类型', '状态', '有效期至', '核销时间']
  const rows = tableData.value.map((item: any) => [
    formatCode(item.card_code),
    item.batch_no,
    typeMap[item.card_type],
    statusMap[item.status].label,
    formatDate(item.expire_at),
    item.used_at ? formatDate(item.used_at) : '-'
  ])

  let csvContent = "data:text/csv;charset=utf-8,\uFEFF"
  csvContent += headers.join(",") + "\n"
  rows.forEach(row => {
    csvContent += row.join(",") + "\n"
  })

  const encodedUri = encodeURI(csvContent)
  const link = document.createElement("a")
  link.setAttribute("href", encodedUri)
  link.setAttribute("download", `卡密导出_${new Date().getTime()}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const showDetail = (row: any) => {
  ElMessage.info('卡密详情: ' + row.card_code)
}

const fetchBatches = async () => {
  try {
    const res: any = await request.get('/card/batches')
    batchOptions.value = res
  } catch (error) {
    console.error('Failed to fetch batches:', error)
  }
}

onMounted(() => {
  handleSearch()
  fetchBatches()
})
</script>

<style scoped>
.card-list-container {
  animation: fadeIn 0.5s ease-out;
}

.stats-mini-card {
  background-color: #fff;
  padding: 16px 20px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  border: 1px solid #f1f5f9;
}

.stats-mini-card .label {
  color: #64748b;
  font-size: 13px;
  margin-bottom: 4px;
}

.stats-mini-card .value {
  color: #1e293b;
  font-size: 20px;
  font-weight: 700;
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

.batch-select {
  width: 220px;
}

.code-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.code-text {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  background-color: #f8fafc;
  padding: 2px 6px;
  border-radius: 4px;
  color: #334155;
  font-size: 13px;
}

.status-badge {
  margin-right: 8px;
}

.status-text {
  font-size: 13px;
  font-weight: 500;
}

.text-success { color: #10b981; }
.text-info { color: #94a3b8; }
.text-warning { color: #f59e0b; }
.text-danger { color: #ef4444; }

.time-column {
  display: flex;
  flex-direction: column;
}

.time {
  font-size: 13px;
  color: #334155;
}

.relative-time {
  font-size: 11px;
  color: #94a3b8;
}

.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

.generate-form {
  padding: 10px 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
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
