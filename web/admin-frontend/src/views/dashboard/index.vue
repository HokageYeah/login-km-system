<template>
  <div class="dashboard-container">
    <!-- 页面标题区域 -->
    <div class="dashboard-header">
      <div>
        <h1 class="dashboard-title">数据统计仪表盘</h1>
        <p class="dashboard-subtitle">实时监控系统运行状态</p>
      </div>
      <div class="header-actions">
        <el-button
          :icon="Refresh"
          :loading="loading"
          @click="loadStatistics"
          class="refresh-btn"
        >
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 数据统计卡片区域 -->
    <div v-loading="loading" v-if="false" class="stats-section">
      <!-- 用户统计组 -->
      <div class="stat-group">
        <div class="stat-group-header">
          <el-icon class="group-icon"><User /></el-icon>
          <h3 class="group-title">用户统计</h3>
        </div>
        <div class="stat-group-cards">
          <div class="stat-card stat-primary">
            <div class="stat-icon-wrapper">
              <el-icon :size="32" class="stat-icon"><User /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">用户总数</div>
              <div class="stat-value">{{ formatNumber(statistics?.users?.total || 0) }}</div>
              <div class="stat-footer">
                <span class="footer-item success">
                  <el-icon><CircleCheck /></el-icon>
                  正常 {{ statistics?.users?.normal || 0 }}
                </span>
                <span class="footer-item danger">
                  <el-icon><CircleClose /></el-icon>
                  封禁 {{ statistics?.users?.banned || 0 }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 卡密统计组 -->
      <div class="stat-group">
        <div class="stat-group-header">
          <el-icon class="group-icon"><Ticket /></el-icon>
          <h3 class="group-title">卡密统计</h3>
        </div>
        <div class="stat-group-cards">
          <div class="stat-card stat-info">
            <div class="stat-icon-wrapper">
              <el-icon :size="32" class="stat-icon"><Key /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">卡密总数</div>
              <div class="stat-value">{{ formatNumber(statistics?.cards?.total || 0) }}</div>
            </div>
          </div>
          <div class="stat-card stat-success">
            <div class="stat-icon-wrapper">
              <el-icon :size="32" class="stat-icon"><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">未使用</div>
              <div class="stat-value">{{ formatNumber(statistics?.cards?.unused || 0) }}</div>
            </div>
          </div>
          <div class="stat-card stat-warning">
            <div class="stat-icon-wrapper">
              <el-icon :size="32" class="stat-icon"><DocumentChecked /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">已使用</div>
              <div class="stat-value">{{ formatNumber(statistics?.cards?.used || 0) }}</div>
            </div>
          </div>
          <div class="stat-card stat-danger">
            <div class="stat-icon-wrapper">
              <el-icon :size="32" class="stat-icon"><CircleClose /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">已禁用</div>
              <div class="stat-value">{{ formatNumber(statistics?.cards?.disabled || 0) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 设备统计组 -->
      <div class="stat-group">
        <div class="stat-group-header">
          <el-icon class="group-icon"><Monitor /></el-icon>
          <h3 class="group-title">设备统计</h3>
        </div>
        <div class="stat-group-cards">
          <div class="stat-card stat-primary">
            <div class="stat-icon-wrapper">
              <el-icon :size="32" class="stat-icon"><Monitor /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">设备总数</div>
              <div class="stat-value">{{ formatNumber(statistics?.devices?.total || 0) }}</div>
              <div class="stat-footer">
                <span class="footer-item success">
                  <el-icon><Connection /></el-icon>
                  活跃 {{ statistics?.devices?.active || 0 }}
                </span>
                <span class="footer-item danger">
                  <el-icon><RemoveFilled /></el-icon>
                  禁用 {{ statistics?.devices?.disabled || 0 }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 应用统计组 -->
      <div class="stat-group">
        <div class="stat-group-header">
          <el-icon class="group-icon"><Grid /></el-icon>
          <h3 class="group-title">应用统计</h3>
        </div>
        <div class="stat-group-cards">
          <div class="stat-card stat-purple">
            <div class="stat-icon-wrapper">
              <el-icon :size="32" class="stat-icon"><Grid /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">应用总数</div>
              <div class="stat-value">{{ formatNumber(statistics?.apps?.total || 0) }}</div>
              <div class="stat-footer">
                <span class="footer-item success">
                  <el-icon><CircleCheckFilled /></el-icon>
                  正常 {{ statistics?.apps?.active || 0 }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ECharts 图表区域 -->
    <div class="charts-section">
      <!-- 卡密使用情况饼图 -->
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">
            <el-icon class="title-icon"><Ticket /></el-icon>
            卡密使用情况
          </h3>
        </div>
        <div ref="pieChartRef" class="chart-container pie-chart-container"></div>
      </div>

      <!-- 用户状态对比柱状图 -->
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">
            <el-icon class="title-icon"><User /></el-icon>
            用户状态分布
          </h3>
        </div>
        <div ref="barChartRef" class="chart-container"></div>
      </div>

      <!-- 设备状态分布 -->
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">
            <el-icon class="title-icon"><Monitor /></el-icon>
            设备状态分布
          </h3>
        </div>
        <div ref="deviceChartRef" class="chart-container"></div>
      </div>

      <!-- 应用分布环形图 -->
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">
            <el-icon class="title-icon"><Grid /></el-icon>
            应用分布统计
          </h3>
        </div>
        <div ref="appChartRef" class="chart-container"></div>
      </div>

      <!-- 卡密趋势折线图（跨越整行） -->
      <div class="chart-card chart-wide">
        <div class="chart-header">
          <h3 class="chart-title">
            <el-icon class="title-icon"><TrendCharts /></el-icon>
            卡密状态趋势
          </h3>
        </div>
        <div ref="trendChartRef" class="chart-container trend-chart-container"></div>
      </div>

      <!-- 数据汇总表格 -->
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">
            <el-icon class="title-icon"><DataAnalysis /></el-icon>
            数据汇总
          </h3>
        </div>
        <div class="summary-table">
          <div class="summary-row">
            <div class="summary-item">
              <span class="summary-label">用户总数</span>
              <span class="summary-value">{{ formatNumber(statistics?.users?.total || 0) }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">正常用户</span>
              <span class="summary-value success">{{ formatNumber(statistics?.users?.normal || 0) }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">封禁用户</span>
              <span class="summary-value danger">{{ formatNumber(statistics?.users?.banned || 0) }}</span>
            </div>
          </div>
          <div class="summary-row">
            <div class="summary-item">
              <span class="summary-label">卡密总数</span>
              <span class="summary-value">{{ formatNumber(statistics?.cards?.total || 0) }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">未使用</span>
              <span class="summary-value success">{{ formatNumber(statistics?.cards?.unused || 0) }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">已使用</span>
              <span class="summary-value warning">{{ formatNumber(statistics?.cards?.used || 0) }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">已禁用</span>
              <span class="summary-value danger">{{ formatNumber(statistics?.cards?.disabled || 0) }}</span>
            </div>
          </div>
          <div class="summary-row">
            <div class="summary-item">
              <span class="summary-label">设备总数</span>
              <span class="summary-value">{{ formatNumber(statistics?.devices?.total || 0) }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">活跃设备</span>
              <span class="summary-value success">{{ formatNumber(statistics?.devices?.active || 0) }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">禁用设备</span>
              <span class="summary-value danger">{{ formatNumber(statistics?.devices?.disabled || 0) }}</span>
            </div>
          </div>
          <div class="summary-row">
            <div class="summary-item">
              <span class="summary-label">应用总数</span>
              <span class="summary-value">{{ formatNumber(statistics?.apps?.total || 0) }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">正常应用</span>
              <span class="summary-value success">{{ formatNumber(statistics?.apps?.active || 0) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 仪表盘页面
 * @description 展示系统的各项统计数据和 ECharts 图表
 */
import { ref, computed, onMounted, onBeforeUnmount, nextTick} from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'
import {
  User,
  Ticket,
  Monitor,
  Grid,
  CircleCheck,
  CircleClose,
  Connection,
  RemoveFilled,
  DocumentChecked,
  CircleCheckFilled,
  Key,
  Refresh,
  DataAnalysis,
  TrendCharts
} from '@element-plus/icons-vue'
import { getStatistics } from '@/api/admin'
import type { Statistics } from '@/types'

/**
 * 状态定义
 */
const loading = ref(false)                              // 加载状态
const statistics = ref<Statistics | null>(null)          // 统计数据

/**
 * ECharts 实例引用
 */
const pieChartRef = ref<HTMLDivElement>()
const barChartRef = ref<HTMLDivElement>()
const deviceChartRef = ref<HTMLDivElement>()
const appChartRef = ref<HTMLDivElement>()
const trendChartRef = ref<HTMLDivElement>()

/**
 * ECharts 实例
 */
let pieChartInstance: echarts.ECharts | null = null
let barChartInstance: echarts.ECharts | null = null
let deviceChartInstance: echarts.ECharts | null = null
let appChartInstance: echarts.ECharts | null = null
let trendChartInstance: echarts.ECharts | null = null

/**
 * 格式化数字
 * @description 使用千分位分隔符格式化数字
 * @param num 要格式化的数字
 * @returns 格式化后的字符串
 */
const formatNumber = (num: number) => {
  return num.toLocaleString()
}

/**
 * 初始化饼图
 * @description 卡密使用情况饼图
 */
const initPieChart = () => {
  if (!pieChartRef.value || !statistics.value) return

  pieChartInstance = echarts.init(pieChartRef.value)
  
  const option: EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>数量: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: ['未使用', '已使用', '已禁用']
    },
    series: [
      {
        name: '卡密使用情况',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c}'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { 
            value: statistics.value.cards.unused, 
            name: '未使用',
            itemStyle: { color: '#10B981' }
          },
          { 
            value: statistics.value.cards.used, 
            name: '已使用',
            itemStyle: { color: '#F59E0B' }
          },
          { 
            value: statistics.value.cards.disabled, 
            name: '已禁用',
            itemStyle: { color: '#EF4444' }
          }
        ]
      }
    ]
  }

  pieChartInstance.setOption(option)
}

/**
 * 初始化柱状图
 * @description 用户状态分布柱状图
 */
const initBarChart = () => {
  if (!barChartRef.value || !statistics.value) return

  barChartInstance = echarts.init(barChartRef.value)

  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['用户总数', '正常用户', '封禁用户']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '用户状态',
        type: 'bar',
        data: [
          { 
            value: statistics.value.users.total,
            itemStyle: { color: '#3B82F6' }
          },
          { 
            value: statistics.value.users.normal,
            itemStyle: { color: '#10B981' }
          },
          { 
            value: statistics.value.users.banned,
            itemStyle: { color: '#EF4444' }
          }
        ],
        barWidth: '60%',
        itemStyle: {
          borderRadius: [8, 8, 0, 0]
        }
      }
    ]
  }

  barChartInstance.setOption(option)
}

/**
 * 初始化设备分布图
 * @description 设备状态分布环形图
 */
const initDeviceChart = () => {
  if (!deviceChartRef.value || !statistics.value) return

  deviceChartInstance = echarts.init(deviceChartRef.value)

  const option: EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>数量: {c}'
    },
    series: [
      {
        name: '设备分布',
        type: 'pie',
        radius: [50, 70],
        center: ['50%', '50%'],
        avoidLabelOverlap: true,
        label: {
          show: false
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '20',
            fontWeight: 'bold'
          }
        },
        data: [
          {
            value: statistics.value.devices.active,
            name: '活跃设备',
            itemStyle: {
              color: '#10B981',
              borderWidth: 4,
              borderColor: '#fff'
            }
          },
          {
            value: statistics.value.devices.disabled,
            name: '禁用设备',
            itemStyle: {
              color: '#EF4444',
              borderWidth: 4,
              borderColor: '#fff'
            }
          }
        ]
      }
    ]
  }

  deviceChartInstance.setOption(option)
}

/**
 * 初始化应用分布图
 * @description 应用状态分布环形图
 */
const initAppChart = () => {
  if (!appChartRef.value || !statistics.value) return

  appChartInstance = echarts.init(appChartRef.value)

  const option: EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}'
    },
    series: [
      {
        name: '应用分布',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{c}'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        data: [
          {
            value: statistics.value.apps.active,
            name: '正常应用',
            itemStyle: {
              color: '#10B981'
            }
          },
          {
            value: statistics.value.apps.total - statistics.value.apps.active,
            name: '禁用应用',
            itemStyle: {
              color: '#EF4444'
            }
          }
        ]
      }
    ]
  }

  appChartInstance.setOption(option)
}

/**
 * 初始化趋势图
 * @description 卡密状态趋势折线图（模拟数据）
 */
const initTrendChart = () => {
  if (!trendChartRef.value || !statistics.value) return

  trendChartInstance = echarts.init(trendChartRef.value)

  // 模拟最近7天的趋势数据
  const dates = []
  for (let i = 6; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    dates.push(`${date.getMonth() + 1}/${date.getDate()}`)
  }

  // 基于当前数据模拟历史趋势
  const total = statistics.value.cards.total
  const unused = statistics.value.cards.unused
  const used = statistics.value.cards.used
  const disabled = statistics.value.cards.disabled

  const unusedTrend = []
  const usedTrend = []
  const disabledTrend = []

  for (let i = 0; i < 7; i++) {
    const factor = 0.7 + (i * 0.3 / 6)
    unusedTrend.push(Math.floor(unused * factor))
    usedTrend.push(Math.floor(used * factor))
    disabledTrend.push(Math.floor(disabled * factor))
  }

  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['未使用', '已使用', '已禁用'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '未使用',
        type: 'line',
        smooth: true,
        data: unusedTrend,
        itemStyle: {
          color: '#10B981'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
              { offset: 1, color: 'rgba(16, 185, 129, 0)' }
            ]
          }
        }
      },
      {
        name: '已使用',
        type: 'line',
        smooth: true,
        data: usedTrend,
        itemStyle: {
          color: '#F59E0B'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(245, 158, 11, 0.3)' },
              { offset: 1, color: 'rgba(245, 158, 11, 0)' }
            ]
          }
        }
      },
      {
        name: '已禁用',
        type: 'line',
        smooth: true,
        data: disabledTrend,
        itemStyle: {
          color: '#EF4444'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(239, 68, 68, 0.3)' },
              { offset: 1, color: 'rgba(239, 68, 68, 0)' }
            ]
          }
        }
      }
    ]
  }

  trendChartInstance.setOption(option)
}

/**
 * 初始化所有图表
 * @description 在数据加载完成后初始化所有 ECharts 实例
 */
const initCharts = async () => {
  await nextTick()
  
  // 等待 DOM 更新后初始化图表
  setTimeout(() => {
    initPieChart()
    initBarChart()
    initDeviceChart()
    initAppChart()
    initTrendChart()
  }, 100)
}

/**
 * 更新所有图表
 * @description 当数据变化时更新图表
 */
const updateCharts = async () => {
  await nextTick()
  
  setTimeout(() => {
    pieChartInstance && initPieChart()
    barChartInstance && initBarChart()
    deviceChartInstance && initDeviceChart()
    appChartInstance && initAppChart()
    trendChartInstance && initTrendChart()
  }, 100)
}

/**
 * 加载统计数据
 * @description 从后端获取系统统计数据
 */
const loadStatistics = async () => {
  loading.value = true
  try {
    const data = await getStatistics()
    statistics.value = data
    ElMessage.success('数据刷新成功')
    
    // 数据加载完成后初始化图表
    await initCharts()
  } catch (error) {
    ElMessage.error('加载统计数据失败')
    console.error('加载统计数据失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 窗口大小变化时调整图表
 */
const handleResize = () => {
  pieChartInstance && pieChartInstance.resize()
  barChartInstance && barChartInstance.resize()
  deviceChartInstance && deviceChartInstance.resize()
  appChartInstance && appChartInstance.resize()
  trendChartInstance && trendChartInstance.resize()
}

/**
 * 组件挂载时加载数据
 */
onMounted(() => {
  loadStatistics()
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
})

/**
 * 组件卸载时清理资源
 */
onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  
  // 销毁 ECharts 实例
  pieChartInstance && pieChartInstance.dispose()
  barChartInstance && barChartInstance.dispose()
  deviceChartInstance && deviceChartInstance.dispose()
  appChartInstance && appChartInstance.dispose()
  trendChartInstance && trendChartInstance.dispose()
})
</script>

<style scoped>
@reference "../../styles/index.css";

.dashboard-container {
  @apply w-full h-full;
  @apply p-8;
  @apply bg-gradient-to-br from-gray-50 to-gray-100;
  min-height: calc(100vh - 64px);
}

/* 页面头部 */
.dashboard-header {
  @apply flex justify-between items-center mb-8;
}

.dashboard-title {
  @apply text-3xl font-bold text-gray-900;
  @apply mb-2;
  background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.dashboard-subtitle {
  @apply text-base text-gray-600;
}

.header-actions {
}

.refresh-btn {
  @apply px-6 py-2.5;
  background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
  @apply text-white font-medium rounded-xl;
  @apply shadow-lg shadow-blue-500/20;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  @apply shadow-xl shadow-blue-500/30;
  transform: translateY(-2px);
}

/* 统计分组 */
.stats-section {
  @apply space-y-6;
}

.stat-group {
  @apply bg-white rounded-2xl p-6;
  @apply shadow-sm border border-gray-100;
  transition: all 0.3s ease;
}

.stat-group:hover {
  @apply shadow-lg shadow-blue-500/10;
}

.stat-group-header {
  @apply flex items-center gap-3 mb-6;
}

.group-icon {
  @apply w-10 h-10 rounded-xl;
  @apply flex items-center justify-center;
  background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
  @apply text-white;
}

.group-title {
  @apply text-xl font-bold text-gray-900;
}

.stat-group-cards {
  @apply grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-4 gap-4;
}

/* 统计卡片 */
.stat-card {
  @apply bg-gradient-to-br rounded-xl p-5;
  @apply transition-all duration-300;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  transform: rotate(30deg);
  pointer-events: none;
}

.stat-card:hover {
  @apply transform scale-105 shadow-xl;
}

.stat-primary {
  @apply from-blue-50 to-blue-100/50;
}

.stat-success {
  @apply from-green-50 to-green-100/50;
}

.stat-warning {
  @apply from-yellow-50 to-yellow-100/50;
}

.stat-danger {
  @apply from-red-50 to-red-100/50;
}

.stat-purple {
  @apply from-purple-50 to-purple-100/50;
}

.stat-info {
  @apply from-cyan-50 to-cyan-100/50;
}

.stat-icon-wrapper {
  @apply w-14 h-14 rounded-xl mb-4;
  @apply flex items-center justify-center;
  transition: all 0.3s ease;
}

.stat-primary .stat-icon-wrapper {
  @apply bg-white shadow-lg shadow-blue-500/20;
}

.stat-success .stat-icon-wrapper {
  @apply bg-white shadow-lg shadow-green-500/20;
}

.stat-warning .stat-icon-wrapper {
  @apply bg-white shadow-lg shadow-yellow-500/20;
}

.stat-danger .stat-icon-wrapper {
  @apply bg-white shadow-lg shadow-red-500/20;
}

.stat-purple .stat-icon-wrapper {
  @apply bg-white shadow-lg shadow-purple-500/20;
}

.stat-info .stat-icon-wrapper {
  @apply bg-white shadow-lg shadow-cyan-500/20;
}

.stat-card:hover .stat-icon-wrapper {
  @apply transform scale-110 rotate-3;
}

.stat-primary .stat-icon {
  @apply text-blue-600;
}

.stat-success .stat-icon {
  @apply text-green-600;
}

.stat-warning .stat-icon {
  @apply text-yellow-600;
}

.stat-danger .stat-icon {
  @apply text-red-600;
}

.stat-purple .stat-icon {
  @apply text-purple-600;
}

.stat-info .stat-icon {
  @apply text-cyan-600;
}

.stat-content {
  @apply relative z-10;
}

.stat-label {
  @apply text-sm font-medium text-gray-600 mb-2;
}

.stat-value {
  @apply text-4xl font-bold text-gray-900 mb-4;
  line-height: 1;
}

.stat-footer {
  @apply flex gap-4 text-xs;
}

.footer-item {
  @apply flex items-center gap-1.5 font-medium;
}

.footer-item.success {
  @apply text-green-700;
}

.footer-item.danger {
  @apply text-red-700;
}

/* 图表区域 */
.charts-section {
  @apply grid grid-cols-1 lg:grid-cols-2 gap-6;
}

.chart-card {
  @apply bg-white rounded-2xl p-8;
  @apply shadow-sm border border-gray-100;
  transition: all 0.3s ease;
}

.chart-card:hover {
  @apply shadow-lg shadow-blue-500/10;
  transform: translateY(-2px);
}

/* 宽图表卡片（跨越整行） */
.chart-wide {
  @apply lg:col-span-2;
}

.chart-header {
  @apply flex justify-between items-center mb-6;
}

.chart-title {
  @apply text-xl font-bold text-gray-900;
  @apply flex items-center gap-2;
}

.title-icon {
  @apply text-blue-600;
}

.chart-legend {
  @apply flex gap-6;
}

.legend-item {
  @apply text-sm font-medium;
  @apply flex items-center gap-2;
}

.legend-unused {
  @apply text-green-600;
}

.legend-used {
  @apply text-yellow-600;
}

.legend-disabled {
  @apply text-red-600;
}

.chart-container {
  @apply w-full;
  min-height: 300px;
}

.pie-chart-container {
  min-height: 350px;
}

.trend-chart-container {
  min-height: 400px;
}

/* 汇总表格 */
.summary-table {
  @apply space-y-4;
}

.summary-row {
  @apply grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4;
  @apply py-3 border-b border-gray-100 last:border-b-0;
}

.summary-item {
  @apply flex flex-col gap-1;
}

.summary-label {
  @apply text-sm text-gray-600 font-medium;
}

.summary-value {
  @apply text-2xl font-bold text-gray-900;
}

.summary-value.success {
  @apply text-green-600;
}

.summary-value.warning {
  @apply text-yellow-600;
}

.summary-value.danger {
  @apply text-red-600;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .dashboard-header {
    @apply flex-col gap-4;
  }

  .header-actions {
    @apply w-full;
  }

  .refresh-btn {
    @apply w-full;
  }

  .stat-group-cards {
    @apply grid-cols-1;
  }

  .charts-section {
    @apply grid-cols-1;
  }
}

@media (min-width: 769px) and (max-width: 1023px) {
  .stat-group-cards {
    @apply grid-cols-2;
  }

  .charts-section {
    @apply grid-cols-1;
  }
}
</style>
