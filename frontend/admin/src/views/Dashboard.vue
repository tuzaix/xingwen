<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :md="6" v-for="item in statsCards" :key="item.title">
        <el-card shadow="hover" class="stats-card" v-loading="loading">
          <div class="stats-icon" :style="{ backgroundColor: item.bgColor }">
            <el-icon :style="{ color: item.color }">
              <component :is="item.icon" />
            </el-icon>
          </div>
          <div class="stats-info">
            <div class="stats-title">{{ item.title }}</div>
            <div class="stats-value" :style="{ color: item.color }">{{ item.value }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-6">
      <el-col :span="16">
        <el-card shadow="hover" class="chart-card" v-loading="loading">
          <template #header>
            <div class="chart-header">
              <span class="title">报告生成趋势 (近7天)</span>
              <div class="header-actions">
                <el-button link :icon="Refresh" @click="initCharts">刷新</el-button>
                <el-tag size="small" type="primary">实时更新</el-tag>
              </div>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-box">
            <el-empty v-if="!loading && trendDataEmpty" description="暂无趋势数据" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="chart-card" v-loading="loading">
          <template #header>
            <div class="chart-header">
              <span class="title">卡密类型分布</span>
            </div>
          </template>
          <div ref="pieChartRef" class="chart-box">
            <el-empty v-if="!loading && pieDataEmpty" description="暂无分布数据" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import request from '../utils/request'
import { User, Ticket, Files, Warning, Refresh } from '@element-plus/icons-vue'

const summary = ref({
  dau: 0,
  card_verifications: 0,
  total_reports: 0,
  failed_reports: 0
})

const statsCards = computed(() => [
  {
    title: '今日 DAU',
    value: summary.value.dau,
    icon: User,
    color: '#6366f1',
    bgColor: '#e0e7ff'
  },
  {
    title: '今日核销',
    value: summary.value.card_verifications,
    icon: Ticket,
    color: '#3b82f6',
    bgColor: '#dbeafe'
  },
  {
    title: '报告总数',
    value: summary.value.total_reports,
    icon: Files,
    color: '#10b981',
    bgColor: '#d1fae5'
  },
  {
    title: '异常报告',
    value: summary.value.failed_reports,
    icon: Warning,
    color: '#ef4444',
    bgColor: '#fee2e2'
  }
])

const trendChartRef = ref<HTMLElement>()
const pieChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null
let pieChart: echarts.ECharts | null = null

const loading = ref(false)
const trendDataEmpty = ref(true)
const pieDataEmpty = ref(true)

const initCharts = async () => {
  loading.value = true
  try {
    const [summaryData, trendData, distData]: any = await Promise.all([
      request.get('/stats/summary').catch(err => {
        console.error('Summary error:', err)
        return null
      }),
      request.get('/stats/trend').catch(err => {
        console.error('Trend error:', err)
        return []
      }),
      request.get('/stats/distribution').catch(err => {
        console.error('Distribution error:', err)
        return []
      })
    ])

    if (summaryData) {
      summary.value = summaryData
    }

    trendDataEmpty.value = !trendData || trendData.length === 0
    if (trendChart) {
      trendChart.dispose()
      trendChart = null
    }
    if (trendChartRef.value && !trendDataEmpty.value) {
      trendChart = echarts.init(trendChartRef.value)
      trendChart.setOption({
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'cross' }
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: trendData.map((d: any) => d.date || ''),
          axisLine: { lineStyle: { color: '#94a3b8' } }
        },
        yAxis: {
          type: 'value',
          splitLine: { lineStyle: { type: 'dashed', color: '#e2e8f0' } },
          axisLine: { show: false }
        },
        series: [{
          name: '生成报告数',
          data: trendData.map((d: any) => d.count || 0),
          type: 'line',
          smooth: true,
          showSymbol: false,
          itemStyle: { color: '#6366f1' },
          lineStyle: { width: 3 },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(99, 102, 241, 0.2)' },
              { offset: 1, color: 'rgba(99, 102, 241, 0)' }
            ])
          }
        }]
      })
    }

    pieDataEmpty.value = !distData || distData.length === 0
    if (pieChart) {
      pieChart.dispose()
      pieChart = null
    }
    if (pieChartRef.value && !pieDataEmpty.value) {
      pieChart = echarts.init(pieChartRef.value)
      pieChart.setOption({
        tooltip: { trigger: 'item' },
        legend: {
          bottom: '5%',
          left: 'center',
          icon: 'circle'
        },
        series: [{
          name: '卡密分布',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: { show: false },
          emphasis: {
            label: {
              show: true,
              fontSize: 16,
              fontWeight: 'bold'
            }
          },
          data: distData
        }]
      })
    }
  } catch (error) {
    console.error('Failed to initialize dashboard:', error)
  } finally {
    loading.value = false
  }
}

const handleResize = () => {
  trendChart?.resize()
  pieChart?.resize()
}

onMounted(() => {
  initCharts()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  pieChart?.dispose()
})
</script>

<style scoped>
.dashboard-container {
  animation: fadeIn 0.5s ease-out;
}

.stats-card {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 12px;
  border: none;
  transition: transform 0.3s;
}

.stats-card:hover {
  transform: translateY(-5px);
}

:deep(.el-card__body) {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 16px;
}

.stats-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stats-info {
  flex: 1;
}

.stats-title {
  color: #64748b;
  font-size: 14px;
  margin-bottom: 4px;
}

.stats-value {
  font-size: 24px;
  font-weight: 700;
  line-height: 1;
}

.chart-card {
  border-radius: 12px;
  border: none;
  margin-bottom: 20px;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chart-header .title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.chart-box {
  height: 320px;
  width: 100%;
}

.mt-6 {
  margin-top: 24px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
