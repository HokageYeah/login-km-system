<template>
  <div class="dashboard-container">
    <section class="dashboard-header">
      <h1 class="dashboard-title">数据看板</h1>
      <div class="header-actions">
        <span class="header-updated">{{ lastUpdatedText }}</span>
        <el-button
          :icon="RefreshRight"
          :loading="loading"
          @click="loadStatistics"
          class="refresh-btn"
        >
          刷新
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
            <el-icon :size="18">
              <component :is="item.icon" />
            </el-icon>
          </div>
          <span class="overview-tag">{{ item.tag }}</span>
        </div>
        <span class="overview-label">{{ item.label }}</span>
        <strong class="overview-value">{{ formatNumber(item.value) }}</strong>
      </article>
    </section>
        <section class="revenue-panel" v-loading="loading">
      <div class="revenue-toolbar">
        <div>
          <h3 class="panel-title">收入数据总览</h3>
          <p class="revenue-range-text">{{ revenueRangeText }}</p>
        </div>

        <div class="revenue-controls">
          <el-segmented
            v-model="revenueRangeMode"
            :options="revenueRangeModeOptions"
            @change="handleRevenueRangeModeChange"
          />

          <el-date-picker
            v-if="revenueRangeMode === 'day'"
            v-model="selectedDay"
            type="date"
            value-format="YYYY-MM-DD"
            format="YYYY年MM月DD日"
            placeholder="选择日期"
            :clearable="false"
            @change="handleRevenueDateChange"
          />

          <el-date-picker
            v-if="revenueRangeMode === 'month'"
            v-model="selectedMonth"
            type="month"
            value-format="YYYY-MM"
            format="YYYY年MM月"
            placeholder="选择月份"
            :clearable="false"
            @change="handleRevenueDateChange"
          />

          <el-date-picker
            v-if="revenueRangeMode === 'range'"
            v-model="selectedRange"
            type="daterange"
            value-format="YYYY-MM-DD"
            format="YYYY年MM月DD日"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            :clearable="false"
            @change="handleRevenueDateChange"
          />
        </div>
      </div>

      <div class="revenue-chart-grid">
        <article class="chart-card">
          <h3 class="panel-title">收入结构</h3>
          <div ref="revenuePieRef" class="chart-container"></div>
        </article>

        <article class="chart-card chart-span-2">
          <h3 class="panel-title">权限收入分配</h3>
          <div ref="permissionRevenueRef" class="chart-container chart-medium"></div>
        </article>
      </div>
    </section>

    <section class="highlight-grid">
      <article class="panel-card panel-summary">
        <h3 class="panel-title">当日增长摘要</h3>
        <div class="summary-list">
          <div v-for="item in summaryItems" :key="item.label" class="summary-item">
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
            <em>{{ item.desc }}</em>
          </div>
        </div>
      </article>

      <article class="panel-card panel-status">
        <h3 class="panel-title">综合运营观察</h3>
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
    </section>

    <section class="trend-panel" v-loading="loading">
      <div class="trend-toolbar">
        <div>
          <h3 class="panel-title">核心资源增长趋势</h3>
          <p class="trend-range-text">{{ trendRangeText }}</p>
        </div>

        <div class="trend-controls">
          <el-segmented
            v-model="trendRangeMode"
            :options="trendRangeModeOptions"
            @change="handleTrendRangeModeChange"
          />

          <el-date-picker
            v-if="trendRangeMode === 'day'"
            v-model="selectedTrendDay"
            type="date"
            value-format="YYYY-MM-DD"
            format="YYYY年MM月DD日"
            placeholder="选择日期"
            :clearable="false"
            @change="handleTrendDateChange"
          />

          <el-date-picker
            v-if="trendRangeMode === 'month'"
            v-model="selectedTrendMonth"
            type="month"
            value-format="YYYY-MM"
            format="YYYY年MM月"
            placeholder="选择月份"
            :clearable="false"
            @change="handleTrendDateChange"
          />

          <el-date-picker
            v-if="trendRangeMode === 'range'"
            v-model="selectedTrendRange"
            type="daterange"
            value-format="YYYY-MM-DD"
            format="YYYY年MM月DD日"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            :clearable="false"
            @change="handleTrendDateChange"
          />
        </div>
      </div>

      <div class="trend-chart-grid">
        <article class="chart-card">
          <h3 class="panel-title">每日新增核心资源</h3>
          <div ref="dailyCompareRef" class="chart-container chart-large"></div>
        </article>

        <article class="chart-card">
          <h3 class="panel-title">资源新增矩阵</h3>
          <div ref="growthHeatmapRef" class="chart-container chart-medium"></div>
        </article>
      </div>
    </section>

    <section class="charts-grid" v-loading="loading">
      <article class="chart-card">
        <h3 class="panel-title">卡密状态分布</h3>
        <div ref="cardDonutRef" class="chart-container"></div>
      </article>

      <article class="chart-card">
        <h3 class="panel-title">核心状态占比走势</h3>
        <div ref="statusTrendRef" class="chart-container"></div>
      </article>

      <article class="chart-card">
        <h3 class="panel-title">设备与应用健康</h3>
        <div ref="healthBarRef" class="chart-container"></div>
      </article>
    </section>
  </div>
</template>

<script setup lang="ts">
/**
 * 综合仪表盘页面
 * @description 这一版继续围绕“综合数据总览”增强：
 * 1. 统一复用公共统计派生 helper，保证多个仪表盘的指标口径一致；
 * 2. 增加资源总量对比、可切换日期范围的资源新增矩阵和趋势联动分析卡；
 * 3. 所有图表都严格基于 /admin/statistics 当前返回，不拼接虚假趋势数据。
 */
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import type { ECharts, EChartsOption } from 'echarts'
import {
  Grid,
  Monitor,
  RefreshRight,
  Ticket,
  User
} from '@element-plus/icons-vue'
import { getStatistics } from '@/api/admin'
import type { Statistics } from '@/types'
import {
  clampPercent,
  createDashboardFallbackStatistics,
  formatDashboardNumber,
  getAverageValue,
  getLastValue,
  getRate,
  getSeriesPeak,
  getSeriesTotal,
  formatDashboardCurrency,
  toDashboardAmount
} from './dashboard-metrics'

type ChartKey =
  | 'statusTrend'
  | 'cardDonut'
  | 'dailyCompare'
  | 'growthHeatmap'
  | 'healthBar'
  | 'revenuePie'
  | 'permissionRevenue'

const loading = ref(false)                              // 页面加载状态
const statistics = ref<Statistics | null>(null)         // 仪表盘统计快照
const lastUpdatedAt = ref<Date | null>(null)            // 最近刷新时间

const statusTrendRef = ref<HTMLDivElement>()
const cardDonutRef = ref<HTMLDivElement>()
const dailyCompareRef = ref<HTMLDivElement>()
const growthHeatmapRef = ref<HTMLDivElement>()
const healthBarRef = ref<HTMLDivElement>()
const revenuePieRef = ref<HTMLDivElement>()
const permissionRevenueRef = ref<HTMLDivElement>()

const chartInstances: Partial<Record<ChartKey, ECharts>> = {}

type RevenueRangeMode = 'today' | 'day' | 'month' | 'range'
type TrendRangeMode = 'today' | 'day' | 'month' | 'range'

const padDateUnit = (value: number) => String(value).padStart(2, '0')

const getDateValue = (date: Date) => {
  return `${date.getFullYear()}-${padDateUnit(date.getMonth() + 1)}-${padDateUnit(date.getDate())}`
}

const getMonthValue = (date: Date) => {
  return `${date.getFullYear()}-${padDateUnit(date.getMonth() + 1)}`
}

const getShiftedDateValue = (offsetDays: number) => {
  const date = new Date()
  date.setDate(date.getDate() + offsetDays)
  return getDateValue(date)
}

const formatDisplayDate = (value: string) => {
  const [year, month, day] = value.split('-')
  return `${year}年${month}月${day}日`
}

const todayValue = getDateValue(new Date())
const createDefaultRangeValue = (): [string, string] => [getShiftedDateValue(-7), todayValue]
const revenueRangeMode = ref<RevenueRangeMode>('today')
const selectedDay = ref(todayValue)
const selectedMonth = ref(getMonthValue(new Date()))
const selectedRange = ref<[string, string]>(createDefaultRangeValue())
const trendRangeMode = ref<TrendRangeMode>('today')
const selectedTrendDay = ref(todayValue)
const selectedTrendMonth = ref(getMonthValue(new Date()))
const selectedTrendRange = ref<[string, string]>(createDefaultRangeValue())
const revenueRangeModeOptions = [
  { label: '今日', value: 'today' },
  { label: '指定日期', value: 'day' },
  { label: '指定月份', value: 'month' },
  { label: '自定义范围', value: 'range' }
]
const trendRangeModeOptions = [
  { label: '今日', value: 'today' },
  { label: '指定日期', value: 'day' },
  { label: '指定月份', value: 'month' },
  { label: '自定义范围', value: 'range' }
]

/**
 * 统计数据兜底
 * @description 使用统一 helper 生成空结构，避免模板和图表直接访问空对象。
 */
const statisticsSnapshot = computed<Statistics>(() => {
  return statistics.value ?? createDashboardFallbackStatistics()
})

const formatNumber = (num: number) => formatDashboardNumber(num)
const formatCurrency = (value: number | string | null | undefined) => formatDashboardCurrency(value)
const trendScopeLabel = computed(() => {
  const range = statisticsSnapshot.value.trend_range
  if (range.start_date === range.end_date) {
    return '当日'
  }
  return '当前范围'
})

const getMonthRange = (monthValue: string): [string, string] => {
  const [year = new Date().getFullYear(), month = new Date().getMonth() + 1] = monthValue.split('-').map(Number)
  const firstDay = new Date(year, month - 1, 1)
  const lastDay = new Date(year, month, 0)
  return [getDateValue(firstDay), getDateValue(lastDay)]
}

const revenueQueryRange = computed(() => {
  if (revenueRangeMode.value === 'day') {
    return {
      start_date: selectedDay.value,
      end_date: selectedDay.value
    }
  }

  if (revenueRangeMode.value === 'month') {
    const [startDate, endDate] = getMonthRange(selectedMonth.value)
    return {
      start_date: startDate,
      end_date: endDate
    }
  }

  if (revenueRangeMode.value === 'range') {
    return {
      start_date: selectedRange.value[0],
      end_date: selectedRange.value[1]
    }
  }

  return {
    start_date: todayValue,
    end_date: todayValue
  }
})

const revenueRangeText = computed(() => {
  const range = statisticsSnapshot.value.revenue_range
  if (range.start_date === range.end_date) {
    return `当前查看 ${formatDisplayDate(range.start_date)} 的收入、销售与权限贡献。`
  }
  return `当前查看 ${formatDisplayDate(range.start_date)} 至 ${formatDisplayDate(range.end_date)} 的收入、销售与权限贡献。`
})

const trendQueryRange = computed(() => {
  if (trendRangeMode.value === 'day') {
    return {
      trend_start_date: selectedTrendDay.value,
      trend_end_date: selectedTrendDay.value
    }
  }

  if (trendRangeMode.value === 'month') {
    const [startDate, endDate] = getMonthRange(selectedTrendMonth.value)
    return {
      trend_start_date: startDate,
      trend_end_date: endDate
    }
  }

  if (trendRangeMode.value === 'range') {
    return {
      trend_start_date: selectedTrendRange.value[0],
      trend_end_date: selectedTrendRange.value[1]
    }
  }

  return {
    trend_start_date: todayValue,
    trend_end_date: todayValue
  }
})

const trendRangeText = computed(() => {
  const range = statisticsSnapshot.value.trend_range
  if (range.start_date === range.end_date) {
    return `当前查看 ${formatDisplayDate(range.start_date)} 的新增与累计变化。`
  }
  return `当前查看 ${formatDisplayDate(range.start_date)} 至 ${formatDisplayDate(range.end_date)} 的新增与累计变化。`
})

const handleRevenueRangeModeChange = () => {
  if (revenueRangeMode.value === 'today') {
    selectedDay.value = todayValue
  }

  if (revenueRangeMode.value === 'range') {
    selectedRange.value = createDefaultRangeValue()
  }

  loadStatistics()
}

const handleRevenueDateChange = () => {
  loadStatistics()
}

const handleTrendRangeModeChange = () => {
  if (trendRangeMode.value === 'today') {
    selectedTrendDay.value = todayValue
  }

  if (trendRangeMode.value === 'month') {
    selectedTrendMonth.value = getMonthValue(new Date())
  }

  if (trendRangeMode.value === 'range') {
    selectedTrendRange.value = createDefaultRangeValue()
  }

  loadStatistics()
}

const handleTrendDateChange = () => {
  loadStatistics()
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

const abnormalAppCount = computed(() => {
  const snapshot = statisticsSnapshot.value
  return Math.max(snapshot.apps.total - snapshot.apps.active, 0)
})

const userHealthRate = computed(() => getRate(statisticsSnapshot.value.users.normal, statisticsSnapshot.value.users.total))
const cardUsageRate = computed(() => getRate(statisticsSnapshot.value.cards.used, statisticsSnapshot.value.cards.total))
const cardReserveRate = computed(() => getRate(statisticsSnapshot.value.cards.unused, statisticsSnapshot.value.cards.total))
const deviceHealthRate = computed(() => getRate(statisticsSnapshot.value.devices.active, statisticsSnapshot.value.devices.total))
const appAvailabilityRate = computed(() => getRate(statisticsSnapshot.value.apps.active, statisticsSnapshot.value.apps.total))

const todayNewUsers = computed(() => getLastValue(statisticsSnapshot.value.trends.daily_new.users))
const todayNewDevices = computed(() => getLastValue(statisticsSnapshot.value.trends.daily_new.devices))
const todayNewCards = computed(() => getLastValue(statisticsSnapshot.value.trends.daily_new.cards))
const todayNewApps = computed(() => getLastValue(statisticsSnapshot.value.trends.daily_new.apps))
const todayRevenue = computed(() => getLastValue(statisticsSnapshot.value.sales_trend.daily_revenue.map(toDashboardAmount)))
const todayOrders = computed(() => getLastValue(statisticsSnapshot.value.sales_trend.daily_orders))

const averageDailyUsers = computed(() => getAverageValue(statisticsSnapshot.value.trends.daily_new.users))
const averageDailyDevices = computed(() => getAverageValue(statisticsSnapshot.value.trends.daily_new.devices))
const averageDailyCards = computed(() => getAverageValue(statisticsSnapshot.value.trends.daily_new.cards))
const averageDailyApps = computed(() => getAverageValue(statisticsSnapshot.value.trends.daily_new.apps))
const averageDailyRevenue = computed(() => getAverageValue(statisticsSnapshot.value.sales_trend.daily_revenue.map(toDashboardAmount)))

const todayGrowthTotal = computed(() => {
  return todayNewUsers.value + todayNewDevices.value + todayNewCards.value + todayNewApps.value
})

const weeklyGrowthTotal = computed(() => {
  const trends = statisticsSnapshot.value.trends.daily_new
  return getSeriesTotal(trends.users) + getSeriesTotal(trends.devices) + getSeriesTotal(trends.cards) + getSeriesTotal(trends.apps)
})

const averageGrowthTotal = computed(() => {
  return averageDailyUsers.value + averageDailyDevices.value + averageDailyCards.value + averageDailyApps.value
})

/**
 * 增长动量
 * @description 观察今日总新增相对当前趋势统计均值的强弱，用于综合版首页快速判断。
 */
const growthMomentumRate = computed(() => {
  if (!averageGrowthTotal.value) {
    return todayGrowthTotal.value > 0 ? 100 : 0
  }
  return clampPercent((todayGrowthTotal.value / averageGrowthTotal.value) * 100)
})

/**
 * 风险暴露率
 * @description 用异常用户、禁用卡密、禁用设备、异常应用占整体资源的比例来观察系统风险面。
 */
const riskExposureRate = computed(() => {
  const snapshot = statisticsSnapshot.value
  const abnormalTotal =
    snapshot.users.banned +
    snapshot.cards.disabled +
    snapshot.devices.disabled +
    abnormalAppCount.value

  const resourceTotal =
    snapshot.users.total +
    snapshot.cards.total +
    snapshot.devices.total +
    snapshot.apps.total

  return getRate(abnormalTotal, resourceTotal)
})

/**
 * 资源协同分
 * @description 主要观察用户增长、设备跟随和卡密库存是否协同。
 */
const resourceSynergyScore = computed(() => {
  const deviceFollowRate = clampPercent((todayNewDevices.value / Math.max(todayNewUsers.value, 1)) * 100)
  const inventoryRate = cardReserveRate.value

  return Math.round(
    growthMomentumRate.value * 0.4 +
    deviceFollowRate * 0.28 +
    inventoryRate * 0.18 +
    appAvailabilityRate.value * 0.14
  )
})


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
      tag: `今日 +${todayNewUsers.value}`,
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
      tag: `库存 ${snapshot.cards.unused}`,
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
      tag: `今日 +${todayNewDevices.value}`,
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
      tag: `异常 ${abnormalAppCount.value}`,
      icon: Grid,
      iconClass: 'icon-app'
    }
  ]
})

const summaryItems = computed(() => {
  return [
    {
      label: '今日新增用户',
      value: `${todayNewUsers.value}`,
      desc: `${trendScopeLabel.value}均值 ${averageDailyUsers.value}`
    },
    {
      label: '今日新增设备',
      value: `${todayNewDevices.value}`,
      desc: `${trendScopeLabel.value}均值 ${averageDailyDevices.value}`
    },
    {
      label: '今日新增卡密',
      value: `${todayNewCards.value}`,
      desc: `${trendScopeLabel.value}均值 ${averageDailyCards.value}`
    },
    {
      label: '今日新增应用',
      value: `${todayNewApps.value}`,
      desc: `${trendScopeLabel.value}均值 ${averageDailyApps.value}`
    },
    {
      label: '今日总新增',
      value: `${todayGrowthTotal.value}`,
      desc: `${trendScopeLabel.value}累计 ${weeklyGrowthTotal.value}`
    },
    {
      label: '卡密使用率',
      value: `${cardUsageRate.value}%`,
      desc: `库存率 ${cardReserveRate.value}%`
    }
  ]
})

const focusItems = computed(() => {
  const snapshot = statisticsSnapshot.value

  return [
    {
      label: '增长动能',
      text: growthMomentumRate.value >= 100
        ? `今日总新增 ${todayGrowthTotal.value} 条，已经达到或超过${trendScopeLabel.value}均值 ${averageGrowthTotal.value.toFixed(1)}。`
        : `今日总新增 ${todayGrowthTotal.value} 条，低于${trendScopeLabel.value}均值 ${averageGrowthTotal.value.toFixed(1)}，建议继续观察接入节奏。`,
      levelClass: growthMomentumRate.value >= 100 ? 'level-success' : 'level-info'
    },
    {
      label: '用户与设备协同',
      text: todayNewDevices.value >= todayNewUsers.value
        ? `今日新增设备 ${todayNewDevices.value} 台，基本跟上新增用户 ${todayNewUsers.value} 人，接入转化表现稳定。`
        : `今日新增设备 ${todayNewDevices.value} 台，低于新增用户 ${todayNewUsers.value} 人，建议排查是否存在激活漏斗损耗。`,
      levelClass: todayNewDevices.value >= todayNewUsers.value ? 'level-success' : 'level-warning'
    },
    {
      label: '风险暴露',
      text: riskExposureRate.value > 10
        ? `当前异常资源暴露率为 ${riskExposureRate.value}%，相对偏高，需要重点关注封禁与禁用带来的经营影响。`
        : `当前异常资源暴露率为 ${riskExposureRate.value}%，整体仍处于可控区间。`,
      levelClass: riskExposureRate.value > 10 ? 'level-warning' : 'level-success'
    },
    {
      label: '应用可用性',
      text: abnormalAppCount.value > 0
        ? `当前有 ${abnormalAppCount.value} 个应用未处于正常状态，建议检查应用配置、接入参数和管理员操作记录。`
        : '当前所有应用都处于正常状态，应用侧没有明显可用性风险。',
      levelClass: abnormalAppCount.value > 0 ? 'level-warning' : 'level-success'
    }
  ]
})


const topPermissionRevenue = computed(() => {
  return statisticsSnapshot.value.permission_revenue.slice(0, 8)
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

const heatmapMatrix = computed(() => {
  const trends = statisticsSnapshot.value.trends.daily_new
  const rows = [
    { name: '用户', values: trends.users },
    { name: '设备', values: trends.devices },
    { name: '卡密', values: trends.cards },
    { name: '应用', values: trends.apps }
  ]

  return rows.flatMap((row, rowIndex) => {
    return row.values.map((value, colIndex) => [colIndex, rowIndex, value])
  })
})

const heatmapMaxValue = computed(() => {
  const allValues = [
    ...statisticsSnapshot.value.trends.daily_new.users,
    ...statisticsSnapshot.value.trends.daily_new.devices,
    ...statisticsSnapshot.value.trends.daily_new.cards,
    ...statisticsSnapshot.value.trends.daily_new.apps
  ]

  return Math.max(getSeriesPeak(allValues), 1)
})

const getChartElement = (chartKey: ChartKey) => {
  const elementMap: Record<ChartKey, HTMLDivElement | undefined> = {
    statusTrend: statusTrendRef.value,
    cardDonut: cardDonutRef.value,
    dailyCompare: dailyCompareRef.value,
    growthHeatmap: growthHeatmapRef.value,
    healthBar: healthBarRef.value,
    revenuePie: revenuePieRef.value,
    permissionRevenue: permissionRevenueRef.value
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
            { offset: 0, color: 'rgba(56, 189, 248, 0.26)' },
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
        symbolSize: 8,
        lineStyle: { width: 3, color: '#14b8a6' },
        itemStyle: { color: '#14b8a6' },
        data: trends.daily_new.users
      },
      {
        name: '新增设备',
        type: 'line',
        smooth: true,
        symbolSize: 8,
        lineStyle: { width: 3, color: '#60a5fa' },
        itemStyle: { color: '#60a5fa' },
        data: trends.daily_new.devices
      },
      {
        name: '新增卡密',
        type: 'line',
        smooth: true,
        symbolSize: 8,
        lineStyle: { width: 3, color: '#f59e0b' },
        itemStyle: { color: '#f59e0b' },
        data: trends.daily_new.cards
      },
      {
        name: '新增应用',
        type: 'bar',
        barWidth: 18,
        itemStyle: {
          color: 'rgba(139, 92, 246, 0.35)',
          borderRadius: [8, 8, 0, 0]
        },
        data: trends.daily_new.apps
      }
    ]
  }

  instance.setOption(option)
}

const renderGrowthHeatmap = () => {
  const instance = ensureChartInstance('growthHeatmap')
  if (!instance) return

  const option: EChartsOption = {
    tooltip: {
      position: 'top',
      formatter: (params: any) => {
        const [xIndex, yIndex, value] = params.value as [number, number, number]
        const labels = statisticsSnapshot.value.trends.labels
        const rows = ['用户', '设备', '卡密', '应用']
        return `${rows[yIndex]}<br/>${labels[xIndex]}：${value}`
      }
    },
    grid: {
      left: '6%',
      right: '6%',
      top: '10%',
      bottom: '12%'
    },
    xAxis: {
      type: 'category',
      data: statisticsSnapshot.value.trends.labels,
      splitArea: { show: true },
      axisTick: { show: false },
      axisLabel: { color: '#64748b' },
      axisLine: { lineStyle: { color: '#d7dee8' } }
    },
    yAxis: {
      type: 'category',
      data: ['用户', '设备', '卡密', '应用'],
      splitArea: { show: true },
      axisTick: { show: false },
      axisLabel: { color: '#475569', fontWeight: 600 },
      axisLine: { show: false }
    },
    visualMap: {
      min: 0,
      max: heatmapMaxValue.value,
      orient: 'horizontal',
      left: 'center',
      bottom: 0,
      textStyle: { color: '#64748b' },
      inRange: {
        color: ['#f8fafc', '#bae6fd', '#38bdf8', '#0284c7']
      }
    },
    series: [
      {
        type: 'heatmap',
        data: heatmapMatrix.value,
        label: {
          show: true,
          color: '#0f172a',
          fontWeight: 600
        },
        itemStyle: {
          borderRadius: 8,
          borderColor: 'rgba(255,255,255,0.8)',
          borderWidth: 2
        }
      }
    ]
  }

  instance.setOption(option)
}

const renderHealthBarChart = () => {
  const instance = ensureChartInstance('healthBar')
  if (!instance) return

  const snapshot = statisticsSnapshot.value

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
        data: [snapshot.devices.disabled, abnormalAppCount.value]
      }
    ]
  }

  instance.setOption(option)
}




const renderRevenuePieChart = () => {
  const instance = ensureChartInstance('revenuePie')
  if (!instance) return

  const revenue = statisticsSnapshot.value.revenue
  const totalRevenue = toDashboardAmount(revenue.total)
  const option: EChartsOption = {
    color: ['#14b8a6', '#f59e0b'],
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        return `${params.name}<br/>金额：${formatCurrency(params.value)} (${params.percent}%)`
      }
    },
    title: {
      text: formatCurrency(totalRevenue),
      subtext: '总收入',
      left: 'center',
      top: '36%',
      textStyle: {
        color: '#0f172a',
        fontSize: 22,
        fontWeight: 700
      },
      subtextStyle: {
        color: '#64748b',
        fontSize: 12
      }
    },
    legend: {
      bottom: 0,
      icon: 'circle',
      textStyle: { color: '#475569' }
    },
    series: [
      {
        name: '收入结构',
        type: 'pie',
        radius: ['48%', '72%'],
        center: ['50%', '42%'],
        label: {
          formatter: (params: any) => `${params.name}\n${formatCurrency(params.value)}`
        },
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 4,
          borderRadius: 10
        },
        data: [
          { value: toDashboardAmount(revenue.used), name: '使用中收入' },
          { value: toDashboardAmount(revenue.unused), name: '未使用库存金额' }
        ]
      }
    ]
  }

  instance.setOption(option)
}

const renderPermissionRevenueChart = () => {
  const instance = ensureChartInstance('permissionRevenue')
  if (!instance) return

  const data = topPermissionRevenue.value
  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const item = data[params[0].dataIndex]
        if (!item) return ''
        return `${item.permission_name}<br/>归因收入：${formatCurrency(item.revenue)}<br/>卡密数：${item.card_count}<br/>月价：${formatCurrency(item.monthly_price)}`
      }
    },
    grid: {
      left: '4%',
      right: '6%',
      bottom: '6%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#edf2f7' } },
      axisLabel: {
        color: '#64748b',
        formatter: (value: number) => formatCurrency(value)
      }
    },
    yAxis: {
      type: 'category',
      data: data.map(item => item.permission_name),
      axisTick: { show: false },
      axisLine: { show: false },
      axisLabel: { color: '#334155', fontWeight: 600 }
    },
    series: [
      {
        name: '权限收入',
        type: 'bar',
        barWidth: 16,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
            { offset: 0, color: '#0ea5e9' },
            { offset: 1, color: '#14b8a6' }
          ]),
          borderRadius: [0, 8, 8, 0]
        },
        label: {
          show: true,
          position: 'right',
          color: '#0f172a',
          formatter: (params: any) => formatCurrency(params.value)
        },
        data: data.map(item => toDashboardAmount(item.revenue))
      }
    ]
  }

  instance.setOption(option)
}

const renderAllCharts = async () => {
  await nextTick()

  if (!statistics.value) return

  console.info('[综合仪表盘] 开始渲染图表', {
    users: statistics.value.users,
    cards: statistics.value.cards,
    devices: statistics.value.devices,
    apps: statistics.value.apps,
    trends: statistics.value.trends
  })

  renderStatusTrendChart()
  renderCardDonut()
  renderDailyCompareChart()
  renderGrowthHeatmap()
  renderHealthBarChart()
  renderRevenuePieChart()
  renderPermissionRevenueChart()
}

const loadStatistics = async () => {
  loading.value = true
  const revenueRange = revenueQueryRange.value
  const trendRange = trendQueryRange.value
  const query = {
    ...revenueRange,
    ...trendRange
  }
  console.info('[综合仪表盘] 开始加载统计数据', query)

  try {
    const data = await getStatistics(query)
    statistics.value = data
    lastUpdatedAt.value = new Date()

    console.info('[综合仪表盘] 统计数据加载完成', {
      users: data.users,
      cards: data.cards,
      devices: data.devices,
      apps: data.apps,
      revenue: data.revenue,
      revenueRange: data.revenue_range,
      trendRange: data.trend_range,
      trendLabels: data.trends.labels
    })
    ElMessage.success('综合数据看板已刷新')

    await renderAllCharts()
  } catch (error) {
    ElMessage.error('加载综合数据看板失败')
    console.error('[综合仪表盘] 加载统计数据失败', error)
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
    'statusTrend',
    'cardDonut',
    'dailyCompare',
    'growthHeatmap',
    'healthBar',
    'revenuePie',
    'permissionRevenue'
  ]

  chartKeys.forEach((chartKey) => {
    chartInstances[chartKey]?.dispose()
    delete chartInstances[chartKey]
  })
}

onMounted(() => {
  console.info('[综合仪表盘] 页面挂载，准备初始化综合数据看板')
  loadStatistics()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  console.info('[综合仪表盘] 页面卸载，开始清理图表实例')
  window.removeEventListener('resize', handleResize)
  disposeCharts()
})
</script>

<style scoped>
@reference "../../styles/index.css";

@keyframes dash-fade-up {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ========== 页面容器 ========== */
.dashboard-container {
  @apply min-h-full px-6 py-8 lg:px-10;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
}

/* ========== 页头 ========== */
.dashboard-header {
  @apply flex items-center justify-between mb-10;
  animation: dash-fade-up 0.4s ease-out both;
}

.dashboard-title {
  @apply text-2xl font-bold text-slate-800;
}

.header-actions {
  @apply flex items-center gap-4;
}

.header-updated {
  @apply text-sm text-slate-400 tabular-nums;
}

.refresh-btn {
  @apply rounded-xl border border-slate-200 bg-white text-slate-600 font-medium;
  @apply shadow-sm;
  transition: all 0.2s ease;
}

.refresh-btn:hover {
  @apply border-sky-300 text-sky-700 bg-sky-50;
  box-shadow: 0 2px 8px rgba(56, 189, 248, 0.12);
}

/* ========== 总览卡片 ========== */
.overview-grid {
  @apply grid grid-cols-2 xl:grid-cols-4 gap-4 mb-8;
}

.overview-card {
  @apply rounded-2xl border border-slate-200/80 bg-white px-5 py-4;
  @apply flex items-center gap-4;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  animation: dash-fade-up 0.4s ease-out both;
}

.overview-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(15, 23, 42, 0.05);
}

.overview-card-top {
  @apply flex items-center justify-between;
}

.overview-icon {
  @apply flex items-center justify-center w-10 h-10 rounded-xl shrink-0;
}

.icon-user { @apply bg-sky-50 text-sky-600; }
.icon-card { @apply bg-amber-50 text-amber-600; }
.icon-device { @apply bg-teal-50 text-teal-600; }
.icon-app { @apply bg-violet-50 text-violet-600; }

.overview-tag {
  @apply text-xs font-medium text-slate-400;
}

.overview-label {
  @apply block text-xs text-slate-400;
}

.overview-value {
  @apply block text-2xl font-bold text-slate-900 tabular-nums mt-0.5;
}

/* ========== 面板标题 ========== */
.panel-title {
  @apply text-base font-semibold text-slate-800 mb-1;
}

.panel-card {
  @apply rounded-2xl border border-slate-200/80 bg-white p-5;
  animation: dash-fade-up 0.5s ease-out both;
}

/* ========== 收入面板 ========== */
.revenue-panel {
  @apply mb-8 rounded-2xl border border-emerald-200/60 bg-white p-6 shadow-sm;
  animation: dash-fade-up 0.5s ease-out both;
}

.revenue-toolbar {
  @apply flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between mb-6 pb-5 border-b border-slate-100;
}

.revenue-range-text {
  @apply text-sm text-slate-400;
}

.revenue-controls {
  @apply flex flex-col gap-3 lg:flex-row lg:flex-wrap lg:items-center xl:justify-end;
}

.revenue-chart-grid {
  @apply grid grid-cols-1 xl:grid-cols-3 gap-5;
}

/* ========== 高亮面板 ========== */
.highlight-grid {
  @apply grid grid-cols-1 xl:grid-cols-2 gap-5 mb-8;
}

/* ========== 摘要列表 ========== */
.summary-list {
  @apply grid grid-cols-2 xl:grid-cols-3 gap-3 mt-4;
}

.summary-item {
  @apply rounded-xl bg-slate-50 px-4 py-3;
}

.summary-item span {
  @apply block text-xs text-slate-400 mb-1;
}

.summary-item strong {
  @apply block text-xl font-bold text-slate-900 tabular-nums;
}

.summary-item em {
  @apply block text-xs text-slate-400 not-italic mt-1;
}

/* ========== 焦点列表 ========== */
.focus-list {
  @apply space-y-3 mt-4;
}

.focus-item {
  @apply flex items-start gap-3 p-2;
}

.focus-dot {
  @apply mt-1.5 w-2 h-2 rounded-full shrink-0;
}

.focus-body strong {
  @apply block text-sm font-semibold text-slate-800;
}

.focus-body p {
  @apply mt-0.5 text-[13px] leading-5 text-slate-500;
}

/* ========== 趋势面板 ========== */
.trend-panel {
  @apply mb-8 rounded-2xl border border-sky-200/60 bg-white p-6 shadow-sm;
  animation: dash-fade-up 0.5s ease-out 0.05s both;
}

.trend-toolbar {
  @apply flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between mb-6 pb-5 border-b border-slate-100;
}

.trend-range-text {
  @apply text-sm text-slate-400;
}

.trend-controls {
  @apply flex flex-col gap-3 lg:flex-row lg:flex-wrap lg:items-center xl:justify-end;
}

.trend-chart-grid {
  @apply flex flex-col gap-5 mt-6;
}

/* ========== 图表区 ========== */
.charts-grid {
  @apply grid grid-cols-1 md:grid-cols-3 gap-5 mb-8;
}

.chart-card {
  @apply rounded-2xl border border-slate-200/80 bg-white p-5;
  animation: dash-fade-up 0.5s ease-out both;
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

/* ========== 状态色 ========== */
.level-success { background: #10b981; color: #10b981; }
.level-info { background: #0ea5e9; color: #0ea5e9; }
.level-warning { background: #f59e0b; color: #f59e0b; }
.level-danger { background: #f43f5e; color: #f43f5e; }

/* ========== 响应式 ========== */
@media (max-width: 768px) {
  .dashboard-container {
    @apply px-4 py-5;
  }

  .dashboard-title {
    @apply text-xl;
  }

  .summary-list {
    @apply grid-cols-1;
  }

  .overview-card,
  .panel-card,
  .chart-card,
  .revenue-panel,
  .trend-panel {
    @apply rounded-xl;
  }

  .chart-container,
  .chart-medium,
  .chart-large {
    height: 260px;
  }
}
</style>
