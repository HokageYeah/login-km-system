<template>
  <div class="dashboard-container">
    <section class="dashboard-header">
      <div class="header-copy">
        <span class="header-badge">Dashboard Overview</span>
        <h1 class="dashboard-title">授权系统数据仪表盘</h1>
        <p class="dashboard-subtitle">
          基于后台统计接口统一展示系统快照、状态结构与近 7 日增长趋势，帮助你快速判断整体运行情况。
        </p>
      </div>

      <div class="header-actions">
        <div class="header-info-card">
          <span>最近更新时间</span>
          <strong>{{ lastUpdatedText }}</strong>
        </div>
        <div class="header-info-card">
          <span>健康评分</span>
          <strong>{{ overallHealthScore }} 分</strong>
        </div>
        <el-button
          :icon="RefreshRight"
          :loading="loading"
          @click="loadStatistics"
          class="refresh-btn"
        >
          刷新数据
        </el-button>
      </div>
    </section>

    <section class="overview-grid">
      <article
        v-for="item in overviewCards"
        :key="item.key"
        class="overview-card"
      >
        <div class="overview-card-top">
          <div class="overview-icon" :class="item.iconClass">
            <el-icon :size="20">
              <component :is="item.icon" />
            </el-icon>
          </div>
          <span class="overview-tag">{{ item.tag }}</span>
        </div>

        <div class="overview-main">
          <span class="overview-label">{{ item.label }}</span>
          <strong class="overview-value">{{ formatNumber(item.value) }}</strong>
          <div class="overview-meta">
            <span>{{ item.metaLabel }}</span>
            <b>{{ item.metaValue }}</b>
          </div>
          <div class="overview-progress">
            <div class="overview-progress-track">
              <div class="overview-progress-bar" :style="{ width: `${item.rate}%` }" />
            </div>
            <span>{{ item.rate }}%</span>
          </div>
        </div>
      </article>
    </section>

    <section class="highlight-grid">
      <article class="panel-card panel-summary">
        <div class="panel-head">
          <div>
            <p class="panel-eyebrow">Today Focus</p>
            <h3 class="panel-title">当日增长摘要</h3>
          </div>
          <el-icon class="panel-icon"><TrendCharts /></el-icon>
        </div>

        <div class="summary-list">
          <div class="summary-item">
            <span>今日新增用户</span>
            <strong>{{ todayNewUsers }}</strong>
          </div>
          <div class="summary-item">
            <span>今日新增设备</span>
            <strong>{{ todayNewDevices }}</strong>
          </div>
          <div class="summary-item">
            <span>卡密使用率</span>
            <strong>{{ cardUsageRate }}%</strong>
          </div>
          <div class="summary-item">
            <span>未使用卡密储备</span>
            <strong>{{ cardReserveRate }}%</strong>
          </div>
        </div>
      </article>

      <article class="panel-card panel-status">
        <div class="panel-head">
          <div>
            <p class="panel-eyebrow">System Reading</p>
            <h3 class="panel-title">系统状态观察</h3>
          </div>
          <el-icon class="panel-icon"><DataAnalysis /></el-icon>
        </div>

        <div class="focus-list">
          <div v-for="item in focusItems" :key="item.label" class="focus-item">
            <span class="focus-dot" :class="item.levelClass" />
            <div class="focus-body">
              <strong>{{ item.label }}</strong>
              <p>{{ item.text }}</p>
            </div>
          </div>
        </div>
      </article>

      <article class="panel-card panel-gauge">
        <div class="panel-head">
          <div>
            <p class="panel-eyebrow">Health Score</p>
            <h3 class="panel-title">系统健康度</h3>
          </div>
          <el-icon class="panel-icon"><Odometer /></el-icon>
        </div>
        <div ref="healthGaugeRef" class="mini-chart-container"></div>
      </article>
    </section>

    <section class="charts-grid" v-loading="loading">
      <article class="chart-card chart-span-2">
        <div class="panel-head">
          <div>
            <p class="panel-eyebrow">Status Line</p>
            <h3 class="panel-title">状态趋势总览</h3>
          </div>
          <el-icon class="panel-icon"><Histogram /></el-icon>
        </div>
        <div ref="statusTrendRef" class="chart-container chart-medium"></div>
      </article>

      <article class="chart-card">
        <div class="panel-head">
          <div>
            <p class="panel-eyebrow">Card Mix</p>
            <h3 class="panel-title">卡密状态分布</h3>
          </div>
          <el-icon class="panel-icon"><Ticket /></el-icon>
        </div>
        <div ref="cardDonutRef" class="chart-container"></div>
      </article>

      <article class="chart-card chart-span-2">
        <div class="panel-head">
          <div>
            <p class="panel-eyebrow">Daily Compare</p>
            <h3 class="panel-title">每日新增用户 / 设备对比</h3>
          </div>
          <el-icon class="panel-icon"><TrendCharts /></el-icon>
        </div>
        <div ref="dailyCompareRef" class="chart-container chart-large"></div>
      </article>

      <article class="chart-card">
        <div class="panel-head">
          <div>
            <p class="panel-eyebrow">Status Board</p>
            <h3 class="panel-title">设备与应用健康</h3>
          </div>
          <el-icon class="panel-icon"><Monitor /></el-icon>
        </div>
        <div ref="healthBarRef" class="chart-container"></div>
      </article>

      <article class="chart-card chart-span-2">
        <div class="panel-head">
          <div>
            <p class="panel-eyebrow">Cumulative Trend</p>
            <h3 class="panel-title">近 7 日累计规模趋势</h3>
          </div>
          <el-icon class="panel-icon"><DataAnalysis /></el-icon>
        </div>
        <div ref="growthLineRef" class="chart-container chart-large"></div>
      </article>

      <article class="chart-card">
        <div class="panel-head">
          <div>
            <p class="panel-eyebrow">Radar View</p>
            <h3 class="panel-title">核心能力雷达</h3>
          </div>
          <el-icon class="panel-icon"><Grid /></el-icon>
        </div>
        <div ref="radarChartRef" class="chart-container"></div>
      </article>

      <article class="chart-card">
        <div class="panel-head">
          <div>
            <p class="panel-eyebrow">Quick Board</p>
            <h3 class="panel-title">数据摘要面板</h3>
          </div>
          <el-icon class="panel-icon"><Memo /></el-icon>
        </div>

        <div class="summary-board">
          <div v-for="metric in summaryMetrics" :key="metric.label" class="summary-board-item">
            <div class="summary-board-top">
              <span>{{ metric.label }}</span>
              <strong>{{ metric.value }}</strong>
            </div>
            <div class="summary-board-track">
              <div class="summary-board-bar" :style="{ width: `${metric.rate}%` }" />
            </div>
          </div>
        </div>
      </article>
    </section>
  </div>
</template>

<script setup lang="ts">
/**
 * 仪表盘页面
 * @description 这一版重点优化两点：
 * 1. 视觉配色减轻，改为更清晰的浅色数据看板；
 * 2. 统一接入真实统计趋势，新增最近 7 日新增用户/设备对比与累计规模折线图。
 */
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import type { ECharts, EChartsOption } from 'echarts'
import {
  DataAnalysis,
  Grid,
  Histogram,
  Memo,
  Monitor,
  Odometer,
  RefreshRight,
  Ticket,
  TrendCharts,
  User
} from '@element-plus/icons-vue'
import { getStatistics } from '@/api/admin'
import type { Statistics } from '@/types'

type ChartKey =
  | 'healthGauge'
  | 'statusTrend'
  | 'cardDonut'
  | 'dailyCompare'
  | 'healthBar'
  | 'growthLine'
  | 'radarChart'

const loading = ref(false)                              // 页面加载状态
const statistics = ref<Statistics | null>(null)         // 仪表盘统计快照
const lastUpdatedAt = ref<Date | null>(null)            // 最近刷新时间

const healthGaugeRef = ref<HTMLDivElement>()
const statusTrendRef = ref<HTMLDivElement>()
const cardDonutRef = ref<HTMLDivElement>()
const dailyCompareRef = ref<HTMLDivElement>()
const healthBarRef = ref<HTMLDivElement>()
const growthLineRef = ref<HTMLDivElement>()
const radarChartRef = ref<HTMLDivElement>()

const chartInstances: Partial<Record<ChartKey, ECharts>> = {}

/**
 * 统计数据兜底
 * @description 页面首屏和异常场景都使用这一层兜底，避免模板和图表出现空引用。
 */
const statisticsSnapshot = computed<Statistics>(() => {
  return statistics.value ?? {
    users: { total: 0, normal: 0, banned: 0 },
    cards: { total: 0, unused: 0, used: 0, disabled: 0 },
    devices: { total: 0, active: 0, disabled: 0 },
    apps: { total: 0, active: 0 },
    trends: {
      labels: Array.from({ length: 7 }, (_, index) => {
        const date = new Date()
        date.setDate(date.getDate() - (6 - index))
        return `${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
      }),
      daily_new: {
        users: Array(7).fill(0),
        devices: Array(7).fill(0),
        cards: Array(7).fill(0),
        apps: Array(7).fill(0)
      },
      cumulative: {
        users: Array(7).fill(0),
        devices: Array(7).fill(0),
        cards: Array(7).fill(0),
        apps: Array(7).fill(0)
      }
    }
  }
})

const formatNumber = (num: number) => num.toLocaleString('zh-CN')

const getLastValue = (values: number[]) => {
  return values.length > 0 ? values[values.length - 1] : 0
}

const getRate = (value: number, total: number) => {
  if (!total) return 0
  return Math.round((value / total) * 100)
}

const lastUpdatedText = computed(() => {
  if (!lastUpdatedAt.value) return '尚未刷新'
  return lastUpdatedAt.value.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
})

const userHealthRate = computed(() => {
  const snapshot = statisticsSnapshot.value
  return getRate(snapshot.users.normal, snapshot.users.total)
})

const cardUsageRate = computed(() => {
  const snapshot = statisticsSnapshot.value
  return getRate(snapshot.cards.used, snapshot.cards.total)
})

const cardReserveRate = computed(() => {
  const snapshot = statisticsSnapshot.value
  return getRate(snapshot.cards.unused, snapshot.cards.total)
})

const deviceHealthRate = computed(() => {
  const snapshot = statisticsSnapshot.value
  return getRate(snapshot.devices.active, snapshot.devices.total)
})

const appAvailabilityRate = computed(() => {
  const snapshot = statisticsSnapshot.value
  return getRate(snapshot.apps.active, snapshot.apps.total)
})

const overallHealthScore = computed(() => {
  const score = (
    userHealthRate.value * 0.28 +
    cardReserveRate.value * 0.18 +
    cardUsageRate.value * 0.14 +
    deviceHealthRate.value * 0.22 +
    appAvailabilityRate.value * 0.18
  )
  return Math.round(score)
})

const todayNewUsers = computed(() => {
  return getLastValue(statisticsSnapshot.value.trends.daily_new.users)
})

const todayNewDevices = computed(() => {
  return getLastValue(statisticsSnapshot.value.trends.daily_new.devices)
})

/**
 * 顶部概览卡片
 */
const overviewCards = computed(() => {
  const snapshot = statisticsSnapshot.value

  return [
    {
      key: 'users',
      label: '用户总数',
      value: snapshot.users.total,
      metaLabel: '正常用户',
      metaValue: `${snapshot.users.normal} 人`,
      rate: userHealthRate.value,
      tag: `封禁 ${snapshot.users.banned}`,
      icon: User,
      iconClass: 'icon-user'
    },
    {
      key: 'cards',
      label: '卡密总数',
      value: snapshot.cards.total,
      metaLabel: '已使用卡密',
      metaValue: `${snapshot.cards.used} 个`,
      rate: cardUsageRate.value,
      tag: `储备 ${snapshot.cards.unused}`,
      icon: Ticket,
      iconClass: 'icon-card'
    },
    {
      key: 'devices',
      label: '设备总数',
      value: snapshot.devices.total,
      metaLabel: '活跃设备',
      metaValue: `${snapshot.devices.active} 台`,
      rate: deviceHealthRate.value,
      tag: `禁用 ${snapshot.devices.disabled}`,
      icon: Monitor,
      iconClass: 'icon-device'
    },
    {
      key: 'apps',
      label: '应用总数',
      value: snapshot.apps.total,
      metaLabel: '可用应用',
      metaValue: `${snapshot.apps.active} 个`,
      rate: appAvailabilityRate.value,
      tag: `今日新增 ${getLastValue(statisticsSnapshot.value.trends.daily_new.apps)}`,
      icon: Grid,
      iconClass: 'icon-app'
    }
  ]
})

const summaryMetrics = computed(() => {
  const snapshot = statisticsSnapshot.value

  return [
    {
      label: '正常用户 / 总用户',
      value: `${snapshot.users.normal} / ${snapshot.users.total}`,
      rate: userHealthRate.value
    },
    {
      label: '已使用卡密 / 总卡密',
      value: `${snapshot.cards.used} / ${snapshot.cards.total}`,
      rate: cardUsageRate.value
    },
    {
      label: '活跃设备 / 总设备',
      value: `${snapshot.devices.active} / ${snapshot.devices.total}`,
      rate: deviceHealthRate.value
    },
    {
      label: '可用应用 / 总应用',
      value: `${snapshot.apps.active} / ${snapshot.apps.total}`,
      rate: appAvailabilityRate.value
    }
  ]
})

const focusItems = computed(() => {
  const snapshot = statisticsSnapshot.value
  const abnormalApps = Math.max(snapshot.apps.total - snapshot.apps.active, 0)

  return [
    {
      label: '增长观察',
      text: `今日新增用户 ${todayNewUsers.value} 人，新增设备 ${todayNewDevices.value} 台。`,
      levelClass: 'level-info'
    },
    {
      label: '用户状态',
      text: snapshot.users.banned > 0
        ? `当前有 ${snapshot.users.banned} 个封禁用户，建议持续关注异常账号。`
        : '当前暂无封禁用户，账号侧状态较为稳定。',
      levelClass: snapshot.users.banned > 0 ? 'level-warning' : 'level-success'
    },
    {
      label: '卡密库存',
      text: snapshot.cards.unused > 0
        ? `当前仍有 ${snapshot.cards.unused} 个未使用卡密，可继续支撑新授权。`
        : '未使用卡密已耗尽，建议尽快补充库存。',
      levelClass: snapshot.cards.unused > 0 ? 'level-success' : 'level-danger'
    },
    {
      label: '应用可用性',
      text: abnormalApps > 0
        ? `当前有 ${abnormalApps} 个应用未处于正常状态，建议检查接入配置。`
        : '所有应用均处于正常状态，可用性表现良好。',
      levelClass: abnormalApps > 0 ? 'level-warning' : 'level-success'
    }
  ]
})

const statusTrendIndicators = computed(() => {
  return [
    { label: '正常用户率', value: userHealthRate.value },
    { label: '卡密储备率', value: cardReserveRate.value },
    { label: '卡密使用率', value: cardUsageRate.value },
    { label: '设备活跃率', value: deviceHealthRate.value },
    { label: '应用可用率', value: appAvailabilityRate.value }
  ]
})

const getChartElement = (chartKey: ChartKey) => {
  const elementMap: Record<ChartKey, HTMLDivElement | undefined> = {
    healthGauge: healthGaugeRef.value,
    statusTrend: statusTrendRef.value,
    cardDonut: cardDonutRef.value,
    dailyCompare: dailyCompareRef.value,
    healthBar: healthBarRef.value,
    growthLine: growthLineRef.value,
    radarChart: radarChartRef.value
  }

  return elementMap[chartKey]
}

const ensureChartInstance = (chartKey: ChartKey) => {
  const element = getChartElement(chartKey)
  if (!element) return null

  const currentInstance = chartInstances[chartKey]
  if (currentInstance) return currentInstance

  const createdInstance = echarts.init(element)
  chartInstances[chartKey] = createdInstance
  return createdInstance
}

const renderHealthGauge = () => {
  const instance = ensureChartInstance('healthGauge')
  if (!instance) return

  const option: EChartsOption = {
    series: [
      {
        type: 'gauge',
        startAngle: 210,
        endAngle: -30,
        min: 0,
        max: 100,
        progress: {
          show: true,
          roundCap: true,
          width: 12,
          itemStyle: {
            color: overallHealthScore.value >= 80 ? '#14b8a6' : overallHealthScore.value >= 60 ? '#f59e0b' : '#fb7185'
          }
        },
        axisLine: {
          roundCap: true,
          lineStyle: {
            width: 12,
            color: [[1, '#e2e8f0']]
          }
        },
        pointer: { show: false },
        anchor: { show: false },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        detail: {
          formatter: '{value}',
          valueAnimation: true,
          color: '#0f172a',
          fontSize: 26,
          fontWeight: 'bold',
          offsetCenter: [0, '6%']
        },
        title: {
          color: '#64748b',
          fontSize: 12,
          offsetCenter: [0, '64%']
        },
        data: [
          {
            value: overallHealthScore.value,
            name: '综合健康度'
          }
        ]
      }
    ]
  }

  instance.setOption(option)
}

const renderStatusTrendChart = () => {
  const instance = ensureChartInstance('statusTrend')
  if (!instance) return

  const indicators = statusTrendIndicators.value

  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>占比：{c}%'
    },
    grid: {
      left: '4%',
      right: '4%',
      bottom: '5%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: indicators.map(item => item.label),
      axisTick: { show: false },
      axisLine: { lineStyle: { color: '#d7dee8' } },
      axisLabel: { color: '#475569' }
    },
    yAxis: {
      type: 'value',
      max: 100,
      splitLine: { lineStyle: { color: '#edf2f7' } },
      axisLabel: {
        color: '#64748b',
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: '状态指标',
        type: 'line',
        smooth: true,
        symbolSize: 10,
        lineStyle: {
          width: 3,
          color: '#38bdf8'
        },
        itemStyle: {
          color: '#0ea5e9',
          borderColor: '#ffffff',
          borderWidth: 2
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(56, 189, 248, 0.28)' },
            { offset: 1, color: 'rgba(56, 189, 248, 0.04)' }
          ])
        },
        data: indicators.map(item => item.value)
      }
    ]
  }

  instance.setOption(option)
}

const renderCardDonut = () => {
  const instance = ensureChartInstance('cardDonut')
  if (!instance) return

  const snapshot = statisticsSnapshot.value

  const option: EChartsOption = {
    color: ['#5eead4', '#fbbf24', '#fda4af'],
    tooltip: {
      trigger: 'item',
      formatter: '{b}<br/>数量：{c} ({d}%)'
    },
    legend: {
      bottom: 0,
      icon: 'circle',
      textStyle: { color: '#475569' }
    },
    series: [
      {
        type: 'pie',
        radius: ['48%', '72%'],
        center: ['50%', '42%'],
        label: {
          show: true,
          formatter: '{b}\n{c}'
        },
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 4
        },
        data: [
          { value: snapshot.cards.unused, name: '未使用' },
          { value: snapshot.cards.used, name: '已使用' },
          { value: snapshot.cards.disabled, name: '已禁用' }
        ]
      }
    ]
  }

  instance.setOption(option)
}

const renderDailyCompareChart = () => {
  const instance = ensureChartInstance('dailyCompare')
  if (!instance) return

  const trends = statisticsSnapshot.value.trends

  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      top: 0,
      textStyle: { color: '#475569' }
    },
    grid: {
      left: '4%',
      right: '4%',
      bottom: '5%',
      top: '14%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: trends.labels,
      axisLine: { lineStyle: { color: '#d7dee8' } },
      axisTick: { show: false },
      axisLabel: { color: '#64748b' }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#edf2f7' } },
      axisLabel: { color: '#64748b' }
    },
    series: [
      {
        name: '新增用户',
        type: 'line',
        smooth: true,
        symbolSize: 9,
        lineStyle: { width: 3, color: '#14b8a6' },
        itemStyle: { color: '#14b8a6' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(20, 184, 166, 0.25)' },
            { offset: 1, color: 'rgba(20, 184, 166, 0.03)' }
          ])
        },
        data: trends.daily_new.users
      },
      {
        name: '新增设备',
        type: 'line',
        smooth: true,
        symbolSize: 9,
        lineStyle: { width: 3, color: '#60a5fa' },
        itemStyle: { color: '#60a5fa' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(96, 165, 250, 0.22)' },
            { offset: 1, color: 'rgba(96, 165, 250, 0.03)' }
          ])
        },
        data: trends.daily_new.devices
      }
    ]
  }

  instance.setOption(option)
}

const renderHealthBarChart = () => {
  const instance = ensureChartInstance('healthBar')
  if (!instance) return

  const snapshot = statisticsSnapshot.value
  const abnormalApps = Math.max(snapshot.apps.total - snapshot.apps.active, 0)

  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: {
      bottom: 0,
      textStyle: { color: '#475569' }
    },
    grid: {
      left: '4%',
      right: '4%',
      bottom: '14%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#edf2f7' } },
      axisLabel: { color: '#64748b' }
    },
    yAxis: {
      type: 'category',
      data: ['设备', '应用'],
      axisTick: { show: false },
      axisLine: { show: false },
      axisLabel: { color: '#334155', fontWeight: 600 }
    },
    series: [
      {
        name: '正常 / 活跃',
        type: 'bar',
        stack: 'total',
        itemStyle: { color: '#5eead4', borderRadius: [0, 8, 8, 0] },
        label: { show: true, color: '#0f172a' },
        data: [snapshot.devices.active, snapshot.apps.active]
      },
      {
        name: '异常 / 禁用',
        type: 'bar',
        stack: 'total',
        itemStyle: { color: '#fda4af', borderRadius: [0, 8, 8, 0] },
        label: { show: true, color: '#0f172a' },
        data: [snapshot.devices.disabled, abnormalApps]
      }
    ]
  }

  instance.setOption(option)
}

const renderGrowthLineChart = () => {
  const instance = ensureChartInstance('growthLine')
  if (!instance) return

  const trends = statisticsSnapshot.value.trends

  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      top: 0,
      textStyle: { color: '#475569' }
    },
    grid: {
      left: '4%',
      right: '4%',
      bottom: '5%',
      top: '14%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: trends.labels,
      axisTick: { show: false },
      axisLine: { lineStyle: { color: '#d7dee8' } },
      axisLabel: { color: '#64748b' }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#edf2f7' } },
      axisLabel: { color: '#64748b' }
    },
    series: [
      {
        name: '累计用户',
        type: 'line',
        smooth: true,
        symbolSize: 7,
        lineStyle: { width: 2.5, color: '#14b8a6' },
        itemStyle: { color: '#14b8a6' },
        data: trends.cumulative.users
      },
      {
        name: '累计设备',
        type: 'line',
        smooth: true,
        symbolSize: 7,
        lineStyle: { width: 2.5, color: '#60a5fa' },
        itemStyle: { color: '#60a5fa' },
        data: trends.cumulative.devices
      },
      {
        name: '累计卡密',
        type: 'line',
        smooth: true,
        symbolSize: 7,
        lineStyle: { width: 2.5, color: '#f59e0b' },
        itemStyle: { color: '#f59e0b' },
        data: trends.cumulative.cards
      },
      {
        name: '累计应用',
        type: 'line',
        smooth: true,
        symbolSize: 7,
        lineStyle: { width: 2.5, color: '#a78bfa' },
        itemStyle: { color: '#a78bfa' },
        data: trends.cumulative.apps
      }
    ]
  }

  instance.setOption(option)
}

const renderRadarChart = () => {
  const instance = ensureChartInstance('radarChart')
  if (!instance) return

  const option: EChartsOption = {
    color: ['#38bdf8'],
    radar: {
      radius: '64%',
      splitNumber: 5,
      axisName: {
        color: '#334155',
        fontWeight: 600
      },
      splitLine: {
        lineStyle: { color: 'rgba(203, 213, 225, 0.7)' }
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(248,250,252,0.4)', 'rgba(241,245,249,0.9)']
        }
      },
      indicator: [
        { name: '用户健康', max: 100 },
        { name: '卡密储备', max: 100 },
        { name: '卡密使用', max: 100 },
        { name: '设备活跃', max: 100 },
        { name: '应用可用', max: 100 }
      ]
    },
    series: [
      {
        type: 'radar',
        areaStyle: {
          color: 'rgba(56, 189, 248, 0.18)'
        },
        lineStyle: {
          width: 3
        },
        symbolSize: 8,
        data: [
          {
            value: [
              userHealthRate.value,
              cardReserveRate.value,
              cardUsageRate.value,
              deviceHealthRate.value,
              appAvailabilityRate.value
            ]
          }
        ]
      }
    ]
  }

  instance.setOption(option)
}

const renderAllCharts = async () => {
  await nextTick()

  if (!statistics.value) return

  console.info('[仪表盘] 开始渲染图表', {
    users: statistics.value.users,
    cards: statistics.value.cards,
    devices: statistics.value.devices,
    apps: statistics.value.apps,
    trendLabels: statistics.value.trends.labels
  })

  renderHealthGauge()
  renderStatusTrendChart()
  renderCardDonut()
  renderDailyCompareChart()
  renderHealthBarChart()
  renderGrowthLineChart()
  renderRadarChart()
}

const loadStatistics = async () => {
  loading.value = true
  console.info('[仪表盘] 开始加载统计数据')

  try {
    const data = await getStatistics()
    statistics.value = data
    lastUpdatedAt.value = new Date()

    console.info('[仪表盘] 统计数据加载完成', data)
    ElMessage.success('仪表盘数据已刷新')

    await renderAllCharts()
  } catch (error) {
    ElMessage.error('加载统计数据失败')
    console.error('[仪表盘] 加载统计数据失败', error)
  } finally {
    loading.value = false
  }
}

const handleResize = () => {
  Object.values(chartInstances).forEach(instance => {
    instance?.resize()
  })
}

const disposeCharts = () => {
  const chartKeys: ChartKey[] = [
    'healthGauge',
    'statusTrend',
    'cardDonut',
    'dailyCompare',
    'healthBar',
    'growthLine',
    'radarChart'
  ]

  chartKeys.forEach((chartKey) => {
    chartInstances[chartKey]?.dispose()
    delete chartInstances[chartKey]
  })
}

onMounted(() => {
  console.info('[仪表盘] 页面挂载，准备初始化轻量化看板')
  loadStatistics()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  console.info('[仪表盘] 页面卸载，开始清理图表实例')
  window.removeEventListener('resize', handleResize)
  disposeCharts()
})
</script>

<style scoped>
@reference "../../styles/index.css";

.dashboard-container {
  @apply min-h-full px-6 py-6 lg:px-8;
  background:
    radial-gradient(circle at top left, rgba(125, 211, 252, 0.18), transparent 26%),
    radial-gradient(circle at top right, rgba(196, 181, 253, 0.12), transparent 24%),
    linear-gradient(180deg, #f8fbfd 0%, #f4f8fb 52%, #f8fafc 100%);
}

.dashboard-header {
  @apply flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between mb-6;
}

.header-copy {
  @apply max-w-3xl;
}

.header-badge {
  @apply inline-flex items-center rounded-full px-3 py-1 text-xs tracking-[0.18em] uppercase;
  @apply bg-sky-100 text-sky-700 border border-sky-200;
}

.dashboard-title {
  @apply mt-4 text-3xl lg:text-4xl font-semibold text-slate-900;
}

.dashboard-subtitle {
  @apply mt-3 text-sm lg:text-base leading-7 text-slate-500;
}

.header-actions {
  @apply flex flex-col sm:flex-row gap-3 xl:items-center;
}

.header-info-card {
  @apply min-w-[168px] rounded-2xl border border-slate-200 bg-white/90 px-4 py-3 shadow-sm;
}

.header-info-card span {
  @apply block text-xs text-slate-400 mb-1;
}

.header-info-card strong {
  @apply text-sm font-semibold text-slate-900;
}

.refresh-btn {
  @apply rounded-2xl border border-sky-200 bg-sky-50 text-sky-700 font-medium;
  @apply shadow-sm hover:bg-sky-100 hover:text-sky-800;
}

.overview-grid {
  @apply grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mb-6;
}

.overview-card,
.panel-card,
.chart-card {
  @apply rounded-[28px] border border-slate-200/80 bg-white/88 shadow-sm;
  @apply backdrop-blur-sm;
}

.overview-card {
  @apply p-5;
}

.overview-card-top {
  @apply flex items-center justify-between mb-5;
}

.overview-icon {
  @apply flex items-center justify-center w-11 h-11 rounded-2xl;
}

.icon-user {
  @apply bg-sky-100 text-sky-700;
}

.icon-card {
  @apply bg-amber-100 text-amber-700;
}

.icon-device {
  @apply bg-teal-100 text-teal-700;
}

.icon-app {
  @apply bg-violet-100 text-violet-700;
}

.overview-tag {
  @apply inline-flex items-center rounded-full px-3 py-1 text-xs font-medium text-slate-500 bg-slate-100;
}

.overview-label {
  @apply block text-sm text-slate-500;
}

.overview-value {
  @apply block mt-2 text-3xl font-semibold text-slate-900;
}

.overview-meta {
  @apply mt-4 flex items-center justify-between text-sm;
}

.overview-meta span {
  @apply text-slate-400;
}

.overview-meta b {
  @apply text-slate-700 font-semibold;
}

.overview-progress {
  @apply mt-4 flex items-center gap-3;
}

.overview-progress-track {
  @apply flex-1 h-2 rounded-full bg-slate-100 overflow-hidden;
}

.overview-progress-bar {
  @apply h-full rounded-full;
  background: linear-gradient(90deg, #38bdf8 0%, #22c55e 100%);
}

.overview-progress span {
  @apply text-xs font-semibold text-slate-500;
}

.highlight-grid {
  @apply grid grid-cols-1 xl:grid-cols-[1fr_1.2fr_0.8fr] gap-4 mb-6;
}

.panel-card,
.chart-card {
  @apply p-5 lg:p-6;
}

.panel-head {
  @apply flex items-start justify-between gap-4 mb-5;
}

.panel-eyebrow {
  @apply text-xs uppercase tracking-[0.2em] text-slate-400;
}

.panel-title {
  @apply mt-1 text-xl font-semibold text-slate-900;
}

.panel-icon {
  @apply flex items-center justify-center w-11 h-11 rounded-2xl bg-slate-100 text-slate-600;
}

.summary-list {
  @apply grid grid-cols-2 gap-3;
}

.summary-item {
  @apply rounded-2xl bg-slate-50 px-4 py-4;
}

.summary-item span {
  @apply block text-xs text-slate-400 mb-2;
}

.summary-item strong {
  @apply text-2xl font-semibold text-slate-900;
}

.focus-list {
  @apply space-y-4;
}

.focus-item {
  @apply flex items-start gap-3;
}

.focus-dot {
  @apply mt-2 w-2.5 h-2.5 rounded-full shrink-0;
}

.focus-body strong {
  @apply block text-sm font-semibold text-slate-900;
}

.focus-body p {
  @apply mt-1 text-sm leading-6 text-slate-500;
}

.level-success {
  @apply bg-emerald-500;
}

.level-info {
  @apply bg-sky-500;
}

.level-warning {
  @apply bg-amber-500;
}

.level-danger {
  @apply bg-rose-500;
}

.mini-chart-container {
  width: 100%;
  height: 220px;
}

.charts-grid {
  @apply grid grid-cols-1 xl:grid-cols-3 gap-4;
}

.chart-span-2 {
  @apply xl:col-span-2;
}

.chart-container {
  width: 100%;
  height: 320px;
}

.chart-medium {
  height: 340px;
}

.chart-large {
  height: 360px;
}

.summary-board {
  @apply space-y-4;
}

.summary-board-item {
  @apply rounded-2xl bg-slate-50 px-4 py-4;
}

.summary-board-top {
  @apply flex items-center justify-between gap-4 mb-3;
}

.summary-board-top span {
  @apply text-sm text-slate-500;
}

.summary-board-top strong {
  @apply text-sm font-semibold text-slate-900;
}

.summary-board-track {
  @apply h-2 rounded-full bg-slate-200 overflow-hidden;
}

.summary-board-bar {
  @apply h-full rounded-full;
  background: linear-gradient(90deg, #7dd3fc 0%, #22c55e 100%);
}

@media (max-width: 768px) {
  .dashboard-container {
    @apply px-4 py-4;
  }

  .dashboard-title {
    @apply text-3xl;
  }

  .overview-card,
  .panel-card,
  .chart-card {
    @apply rounded-3xl p-4;
  }

  .summary-list {
    @apply grid-cols-1;
  }

  .mini-chart-container {
    height: 190px;
  }

  .chart-container,
  .chart-medium,
  .chart-large {
    height: 300px;
  }
}
</style>
