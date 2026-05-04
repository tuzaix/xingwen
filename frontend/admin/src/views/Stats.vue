<template>
  <div class="stats-container">
    <el-row :gutter="20" class="mb-6">
      <el-col :span="6" v-for="s in summaryStats" :key="s.title">
        <el-card shadow="hover" class="stat-mini-card">
          <el-statistic :title="s.title" :value="s.value" :suffix="s.suffix">
            <template #prefix>
              <el-icon :style="{ color: s.color }" class="mr-1">
                <component :is="s.icon" />
              </el-icon>
            </template>
          </el-statistic>
          <div class="stat-footer">
            <span :class="s.trend > 0 ? 'text-success' : 'text-danger'">
              {{ s.trend > 0 ? '+' : '' }}{{ s.trend }}%
            </span>
            <span class="text-gray-400 ml-2">较昨日</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" class="main-stats-card">
      <template #header>
        <div class="card-header">
          <div class="title-group">
            <el-icon class="title-icon"><Histogram /></el-icon>
            <span class="title">流量与转化统计</span>
          </div>
          <el-radio-group v-model="timeRange" size="small">
            <el-radio-button label="7d">近7天</el-radio-button>
            <el-radio-button label="30d">近30天</el-radio-button>
            <el-radio-button label="90d">近90天</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      
      <div class="charts-grid">
        <div class="chart-item full-width">
          <div class="chart-title">每日访问与报告生成量</div>
          <div ref="mainChartRef" class="chart-box"></div>
        </div>
        <div class="chart-item">
          <div class="chart-title">用户画像 (性别比例)</div>
          <div ref="genderChartRef" class="chart-box"></div>
        </div>
        <div class="chart-item">
          <div class="chart-title">热门诉求分布</div>
          <div ref="areaChartRef" class="chart-box"></div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { 
  TrendCharts, 
  User, 
  Files, 
  CircleCheck,
  Histogram
} from '@element-plus/icons-vue'

const timeRange = ref('7d')
const mainChartRef = ref<HTMLElement>()
const genderChartRef = ref<HTMLElement>()
const areaChartRef = ref<HTMLElement>()

let charts: echarts.ECharts[] = []

const summaryStats = [
  { title: '累计总报告', value: 1284, icon: Files, color: '#6366f1', trend: 12.5 },
  { title: '今日活跃用户', value: 42, icon: User, color: '#3b82f6', trend: -2.4 },
  { title: '成功转化率', value: 98.5, suffix: '%', icon: CircleCheck, color: '#10b981', trend: 0.8 },
  { title: '平均生成耗时', value: 4.2, suffix: 's', icon: TrendCharts, color: '#f59e0b', trend: -5.2 }
]

const initCharts = () => {
  if (mainChartRef.value) {
    const chart = echarts.init(mainChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['访问量', '报告量'], bottom: 0 },
      grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
      xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
      yAxis: { type: 'value' },
      series: [
        { name: '访问量', type: 'bar', data: [120, 132, 101, 134, 90, 230, 210], itemStyle: { color: '#94a3b8' } },
        { name: '报告量', type: 'line', smooth: true, data: [20, 32, 11, 34, 40, 60, 50], itemStyle: { color: '#6366f1' } }
      ]
    })
    charts.push(chart)
  }

  if (genderChartRef.value) {
    const chart = echarts.init(genderChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        data: [
          { value: 735, name: '女性', itemStyle: { color: '#f43f5e' } },
          { value: 580, name: '男性', itemStyle: { color: '#3b82f6' } }
        ]
      }]
    })
    charts.push(chart)
  }

  if (areaChartRef.value) {
    const chart = echarts.init(areaChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        roseType: 'area',
        radius: [20, 100],
        data: [
          { value: 40, name: '事业财运' },
          { value: 30, name: '情感婚姻' },
          { value: 20, name: '身体健康' },
          { value: 10, name: '学业考试' }
        ]
      }]
    })
    charts.push(chart)
  }
}

const handleResize = () => {
  charts.forEach(c => c.resize())
}

onMounted(() => {
  initCharts()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  charts.forEach(c => c.dispose())
})
</script>

<style scoped>
.stats-container {
  animation: fadeIn 0.5s ease-out;
}

.stat-mini-card {
  border-radius: 12px;
  border: none;
}

.stat-footer {
  margin-top: 12px;
  font-size: 13px;
  display: flex;
  align-items: center;
}

.text-success { color: #10b981; }
.text-danger { color: #ef4444; }

.main-stats-card {
  border-radius: 12px;
  border: none;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.title-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-icon {
  font-size: 20px;
  color: #6366f1;
}

.title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.chart-item.full-width {
  grid-column: span 2;
}

.chart-title {
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
  margin-bottom: 16px;
  text-align: center;
}

.chart-box {
  height: 300px;
  width: 100%;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
