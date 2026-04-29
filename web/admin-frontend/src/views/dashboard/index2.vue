<template>
  <div class="ink-dashboard">
    <section class="ink-hero">
      <el-button
        :icon="RefreshRight"
        :loading="loading"
        @click="loadStatistics"
        class="ink-refresh-btn"
      >
        刷新水墨看板
      </el-button>

      <!-- 总收入核心区 -->
      <div class="ink-revenue-center">
        <div class="ink-revenue-stamp">
          <span class="ink-revenue-stamp-text">收入总盘</span>
        </div>
        <div class="ink-revenue-main">
          <span class="ink-revenue-prefix">¥</span>
          <strong class="ink-revenue-amount">{{ formatCurrency(totalRevenue).replace('¥', '') }}</strong>
        </div>
        <div class="ink-revenue-breakdown">
          <div class="ink-revenue-chip ink-chip-active">
            <span class="ink-chip-dot" />
            <span>使用中 {{ formatCurrency(allTimeRevenue.used) }}</span>
          </div>
          <div class="ink-revenue-chip ink-chip-stock">
            <span class="ink-chip-dot" />
            <span>未使用 {{ formatCurrency(allTimeRevenue.unused) }}</span>
          </div>
        </div>
      </div>

      <!-- 指标横条 -->
      <div class="ink-hero-metrics">
        <div class="ink-metric-pill">
          <span class="ink-metric-pill-label">最近刷新</span>
          <strong class="ink-metric-pill-value">{{ lastUpdatedText }}</strong>
        </div>
        <div class="ink-metric-divider" />
        <div class="ink-metric-pill">
          <span class="ink-metric-pill-label">最新进账</span>
          <strong class="ink-metric-pill-value ink-value-revenue">{{ formatCurrency(todayRevenue) }}</strong>
        </div>
        <div class="ink-metric-divider" />
        <div class="ink-metric-pill">
          <span class="ink-metric-pill-label">活跃信号</span>
          <strong class="ink-metric-pill-value">{{ activitySignalScore }}<small> 分</small></strong>
        </div>
        <div class="ink-metric-divider" />
        <div class="ink-metric-pill">
          <span class="ink-metric-pill-label">增长质量</span>
          <strong class="ink-metric-pill-value">{{ currentGrowthQuality }}<small> 分</small></strong>
        </div>
      </div>
    </section>

    <section class="ink-growth-suite" v-loading="loading">
      <div class="ink-suite-toolbar">
        <div>
          <p class="ink-panel-eyebrow">Growth Scope</p>
          <h3 class="ink-panel-title">增长与销售联动分析</h3>
          <p class="ink-suite-text">{{ growthRangeText }}</p>
        </div>

        <div class="ink-suite-controls">
          <el-segmented
            v-model="growthRangeMode"
            :options="growthRangeModeOptions"
            @change="handleGrowthRangeModeChange"
          />

          <el-date-picker
            v-if="growthRangeMode === 'day'"
            v-model="selectedGrowthDay"
            type="date"
            value-format="YYYY-MM-DD"
            format="YYYY年MM月DD日"
            placeholder="选择日期"
            :clearable="false"
            @change="handleGrowthDateChange"
          />

          <el-date-picker
            v-if="growthRangeMode === 'month'"
            v-model="selectedGrowthMonth"
            type="month"
            value-format="YYYY-MM"
            format="YYYY年MM月"
            placeholder="选择月份"
            :clearable="false"
            @change="handleGrowthDateChange"
          />

          <el-date-picker
            v-if="growthRangeMode === 'range'"
            v-model="selectedGrowthRange"
            type="daterange"
            value-format="YYYY-MM-DD"
            format="YYYY年MM月DD日"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            :clearable="false"
            @change="handleGrowthDateChange"
          />
        </div>
      </div>

      <div class="ink-growth-chart-grid">
        <article class="ink-chart-card ink-chart-wide">
          <div class="ink-panel-head">
            <div>
              <p class="ink-panel-eyebrow">Sales Trend</p>
              <h3 class="ink-panel-title">每日销售额 / 订单数趋势</h3>
            </div>
            <el-icon class="ink-panel-icon"><DataLine /></el-icon>
          </div>
          <div class="ink-chart-summary">
            <div v-for="item in salesTrendSummary" :key="item.label" class="ink-chart-summary-item">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </div>
          </div>
          <div ref="salesTrendRef" class="ink-chart ink-chart-large"></div>
        </article>

        <article class="ink-chart-card ink-chart-wide">
          <div class="ink-panel-head">
            <div>
              <p class="ink-panel-eyebrow">Daily Growth</p>
              <h3 class="ink-panel-title">每日新增用户 / 设备 / 卡密对比</h3>
            </div>
            <el-icon class="ink-panel-icon"><DataAnalysis /></el-icon>
          </div>
          <div class="ink-chart-summary">
            <div v-for="item in growthCompareSummary" :key="item.label" class="ink-chart-summary-item">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </div>
          </div>
          <div ref="growthCompareRef" class="ink-chart ink-chart-large"></div>
        </article>

        <article class="ink-chart-card ink-chart-wide">
          <div class="ink-panel-head">
            <div>
              <p class="ink-panel-eyebrow">Growth Quality</p>
              <h3 class="ink-panel-title">增长质量指数</h3>
            </div>
            <el-icon class="ink-panel-icon"><DataLine /></el-icon>
          </div>
          <div class="ink-chart-summary">
            <div v-for="item in growthQualitySummary" :key="item.label" class="ink-chart-summary-item">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </div>
          </div>
          <div ref="growthQualityRef" class="ink-chart ink-chart-medium"></div>
        </article>

        <article class="ink-chart-card ink-chart-wide">
          <div class="ink-panel-head">
            <div>
              <p class="ink-panel-eyebrow">Cumulative Growth</p>
              <h3 class="ink-panel-title">累计增长与系统使用规模</h3>
            </div>
            <el-icon class="ink-panel-icon"><CollectionTag /></el-icon>
          </div>
          <div class="ink-chart-summary">
            <div v-for="item in cumulativeTrendSummary" :key="item.label" class="ink-chart-summary-item">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </div>
          </div>
          <div ref="cumulativeTrendRef" class="ink-chart ink-chart-large"></div>
        </article>

        <article class="ink-chart-card ink-chart-wide">
          <div class="ink-panel-head">
            <div>
              <p class="ink-panel-eyebrow">Usage Contrast</p>
              <h3 class="ink-panel-title">关键指标对比分析</h3>
            </div>
            <el-icon class="ink-panel-icon"><Histogram /></el-icon>
          </div>
          <div class="ink-chart-summary">
            <div v-for="item in keyMetricsSummary" :key="item.label" class="ink-chart-summary-item">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </div>
          </div>
          <div ref="keyMetricsRef" class="ink-chart ink-chart-medium"></div>
        </article>

        <article class="ink-chart-card ink-chart-wide">
          <div class="ink-panel-head">
            <div>
              <p class="ink-panel-eyebrow">Growth Scatter</p>
              <h3 class="ink-panel-title">增长协同散点图</h3>
            </div>
            <el-icon class="ink-panel-icon"><Grid /></el-icon>
          </div>
          <div class="ink-chart-summary">
            <div v-for="item in growthScatterSummary" :key="item.label" class="ink-chart-summary-item">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </div>
          </div>
          <div ref="growthScatterRef" class="ink-chart ink-chart-medium"></div>
        </article>
      </div>
    </section>

    <section class="ink-risk-suite" v-loading="loading">
      <div class="ink-suite-toolbar">
        <div>
          <p class="ink-panel-eyebrow">Risk Structure</p>
          <h3 class="ink-panel-title">异常与经营结构观察</h3>
          <p class="ink-suite-text">这一组聚焦风险用户、卡密状态和经营韧性，方便快速判断增长是否被风险侧侵蚀。</p>
        </div>
      </div>

      <div class="ink-risk-chart-grid">
        <article class="ink-chart-card">
          <div class="ink-panel-head">
            <div>
              <p class="ink-panel-eyebrow">User Risk</p>
              <h3 class="ink-panel-title">异常用户结构</h3>
            </div>
            <el-icon class="ink-panel-icon"><User /></el-icon>
          </div>
          <div ref="userRiskRef" class="ink-chart"></div>
        </article>

        <article class="ink-chart-card">
          <div class="ink-panel-head">
            <div>
              <p class="ink-panel-eyebrow">Card Flow</p>
              <h3 class="ink-panel-title">卡密使用 / 封禁对比</h3>
            </div>
            <el-icon class="ink-panel-icon"><Ticket /></el-icon>
          </div>
          <div ref="cardUsageRef" class="ink-chart"></div>
        </article>

        <article class="ink-chart-card">
          <div class="ink-panel-head">
            <div>
              <p class="ink-panel-eyebrow">Health Radar</p>
              <h3 class="ink-panel-title">增长经营雷达</h3>
            </div>
            <el-icon class="ink-panel-icon"><Opportunity /></el-icon>
          </div>
          <div ref="analysisRadarRef" class="ink-chart"></div>
        </article>
      </div>
    </section>

    <section class="ink-quote-strip">
      <div>
        <span class="ink-quote-tag">经营结论</span>
        <strong>{{ strategicHeadline }}</strong>
        <p>{{ strategicSubtitle }}</p>
      </div>
      <div class="ink-quote-meta">
        <span>库存支撑约 {{ inventorySupportDays }} 天</span>
        <span>风险压力 {{ riskPressureRate }}%</span>
        <span>增长协同 {{ userDeviceSynergyRate }}%</span>
      </div>
    </section>

    <section class="ink-metric-grid">
      <article
        v-for="item in coreAnalysisCards"
        :key="item.key"
        class="ink-metric-card"
      >
        <div class="ink-metric-head">
          <div class="ink-metric-icon" :class="item.iconClass">
            <el-icon :size="18">
              <component :is="item.icon" />
            </el-icon>
          </div>
          <span class="ink-metric-tag">{{ item.tag }}</span>
        </div>

        <div class="ink-metric-main">
          <span class="ink-metric-label">{{ item.label }}</span>
          <strong class="ink-metric-value">{{ item.value }}</strong>
          <div class="ink-metric-progress">
            <div class="ink-metric-progress-track">
              <div class="ink-metric-progress-bar" :style="{ width: `${item.rate}%` }" />
            </div>
            <span>{{ item.rate }}%</span>
          </div>
          <p class="ink-metric-desc">{{ item.desc }}</p>
        </div>
      </article>
    </section>

    <section class="ink-analysis-grid">
      <article class="ink-panel ink-analysis-panel">
        <div class="ink-panel-head">
          <div>
            <p class="ink-panel-eyebrow">Growth Reading</p>
            <h3 class="ink-panel-title">增长与使用联动分析</h3>
          </div>
          <el-icon class="ink-panel-icon"><TrendCharts /></el-icon>
        </div>

        <div class="ink-analysis-list">
          <div v-for="item in growthInsights" :key="item.label" class="ink-analysis-item">
            <span class="ink-analysis-dot" :class="item.levelClass" />
            <div class="ink-analysis-content">
              <strong>{{ item.label }}</strong>
              <p>{{ item.text }}</p>
            </div>
          </div>
        </div>
      </article>

      <article class="ink-panel ink-analysis-panel">
        <div class="ink-panel-head">
          <div>
            <p class="ink-panel-eyebrow">Risk Reading</p>
            <h3 class="ink-panel-title">异常与封禁分析</h3>
          </div>
          <el-icon class="ink-panel-icon"><WarningFilled /></el-icon>
        </div>

        <div class="ink-analysis-list">
          <div v-for="item in riskInsights" :key="item.label" class="ink-analysis-item">
            <span class="ink-analysis-dot" :class="item.levelClass" />
            <div class="ink-analysis-content">
              <strong>{{ item.label }}</strong>
              <p>{{ item.text }}</p>
            </div>
          </div>
        </div>
      </article>

      <article class="ink-panel ink-analysis-panel">
        <div class="ink-panel-head">
          <div>
            <p class="ink-panel-eyebrow">Decision Board</p>
            <h3 class="ink-panel-title">经营判断面板</h3>
          </div>
          <el-icon class="ink-panel-icon"><Odometer /></el-icon>
        </div>

        <div class="ink-analysis-list">
          <div v-for="item in decisionInsights" :key="item.label" class="ink-analysis-item">
            <span class="ink-analysis-dot" :class="item.levelClass" />
            <div class="ink-analysis-content">
              <strong>{{ item.label }}</strong>
              <p>{{ item.text }}</p>
            </div>
          </div>
        </div>
      </article>
    </section>

  </div>
</template>

<script setup lang="ts">
/**
 * 水墨风格仪表盘
 * @description 这一页聚焦"增长、异常、卡密使用、封禁数量"的经营分析。
 * 相比综合版，它更强调：
 * 1. 用户增长是否真实发生；
 * 2. 新增用户是否有设备跟随和卡密使用支撑；
 * 3. 异常用户、封禁卡密是否正在侵蚀业务增长质量。
 */
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import type { ECharts, EChartsOption } from 'echarts'
import {
  CollectionTag,
  DataAnalysis,
  DataLine,
  Grid,
  Histogram,
  Odometer,
  Opportunity,
  RefreshRight,
  Ticket,
  TrendCharts,
  User,
  WarningFilled
} from '@element-plus/icons-vue'
import { getStatistics } from '@/api/admin'
import type { Statistics } from '@/types'
import {
  clampPercent,
  createDashboardFallbackStatistics,
  getAverageValue,
  getLastValue,
  getRate,
  getSeriesPeak,
  formatDashboardCurrency,
  toDashboardAmount
} from './dashboard-metrics'

type ChartKey =
  | 'salesTrend'
  | 'growthCompare'
  | 'userRisk'
  | 'growthQuality'
  | 'keyMetrics'
  | 'cardUsage'
  | 'growthScatter'
  | 'cumulativeTrend'
  | 'analysisRadar'

type ChartSummaryItem = {
  label: string
  value: string
}

const loading = ref(false)                              // 页面加载状态
const statistics = ref<Statistics | null>(null)         // 后端统计快照
const lastUpdatedAt = ref<Date | null>(null)            // 最近刷新时间

const padDateUnit = (value: number) => String(value).padStart(2, '0')
type GrowthRangeMode = 'today' | 'day' | 'month' | 'range'

const getDateValue = (date: Date) => {
  return `${date.getFullYear()}-${padDateUnit(date.getMonth() + 1)}-${padDateUnit(date.getDate())}`
}

const getMonthValue = (date: Date) => {
  return `${date.getFullYear()}-${padDateUnit(date.getMonth() + 1)}`
}

const formatDisplayDate = (value: string) => {
  const [year, month, day] = value.split('-')
  return `${year}年${month}月${day}日`
}

const getMonthRange = (monthValue: string): [string, string] => {
  const [year = new Date().getFullYear(), month = new Date().getMonth() + 1] = monthValue.split('-').map(Number)
  const firstDay = new Date(year, month - 1, 1)
  const lastDay = new Date(year, month, 0)
  return [getDateValue(firstDay), getDateValue(lastDay)]
}

const getShiftedDateValue = (offsetDays: number) => {
  const date = new Date()
  date.setDate(date.getDate() + offsetDays)
  return getDateValue(date)
}

const todayValue = getDateValue(new Date())
const createDefaultRangeValue = (): [string, string] => [getShiftedDateValue(-7), todayValue]
const growthRangeMode = ref<GrowthRangeMode>('today')
const selectedGrowthDay = ref(todayValue)
const selectedGrowthMonth = ref(getMonthValue(new Date()))
const selectedGrowthRange = ref<[string, string]>(createDefaultRangeValue())
const growthRangeModeOptions = [
  { label: '今日', value: 'today' },
  { label: '指定日期', value: 'day' },
  { label: '指定月份', value: 'month' },
  { label: '自定义范围', value: 'range' }
]

const growthCompareRef = ref<HTMLDivElement>()
const salesTrendRef = ref<HTMLDivElement>()
const userRiskRef = ref<HTMLDivElement>()
const growthQualityRef = ref<HTMLDivElement>()
const keyMetricsRef = ref<HTMLDivElement>()
const cardUsageRef = ref<HTMLDivElement>()
const growthScatterRef = ref<HTMLDivElement>()
const cumulativeTrendRef = ref<HTMLDivElement>()
const analysisRadarRef = ref<HTMLDivElement>()

const chartInstances: Partial<Record<ChartKey, ECharts>> = {}

/**
 * 数据兜底
 * @description 保证水墨仪表盘在接口未返回前也能稳定渲染。
 */
const statisticsSnapshot = computed<Statistics>(() => {
  return statistics.value ?? createDashboardFallbackStatistics()
})

const formatCurrency = (value: number | string | null | undefined) => formatDashboardCurrency(value)
const growthScopeLabel = computed(() => {
  const range = statisticsSnapshot.value.trend_range
  if (range.start_date === range.end_date) {
    return '当日'
  }
  return '当前范围'
})

const growthRangeText = computed(() => {
  const trendRange = statisticsSnapshot.value.trend_range
  const revenueRange = statisticsSnapshot.value.revenue_range

  if (
    trendRange.start_date === trendRange.end_date &&
    trendRange.start_date === revenueRange.start_date &&
    revenueRange.start_date === revenueRange.end_date
  ) {
    return `当前查看 ${formatDisplayDate(trendRange.start_date)} 的销售、增长、质量与累计规模变化。`
  }

  return `当前查看 ${formatDisplayDate(trendRange.start_date)} 至 ${formatDisplayDate(trendRange.end_date)} 的销售、增长、质量与累计规模变化。`
})

const growthQueryRange = computed(() => {
  if (growthRangeMode.value === 'day') {
    return {
      start_date: selectedGrowthDay.value,
      end_date: selectedGrowthDay.value,
      trend_start_date: selectedGrowthDay.value,
      trend_end_date: selectedGrowthDay.value
    }
  }

  if (growthRangeMode.value === 'month') {
    const [startDate, endDate] = getMonthRange(selectedGrowthMonth.value)
    return {
      start_date: startDate,
      end_date: endDate,
      trend_start_date: startDate,
      trend_end_date: endDate
    }
  }

  if (growthRangeMode.value === 'range') {
    return {
      start_date: selectedGrowthRange.value[0],
      end_date: selectedGrowthRange.value[1],
      trend_start_date: selectedGrowthRange.value[0],
      trend_end_date: selectedGrowthRange.value[1]
    }
  }

  return {
    start_date: todayValue,
    end_date: todayValue,
    trend_start_date: todayValue,
    trend_end_date: todayValue
  }
})

const handleGrowthRangeModeChange = () => {
  if (growthRangeMode.value === 'today') {
    selectedGrowthDay.value = todayValue
  }

  if (growthRangeMode.value === 'month') {
    selectedGrowthMonth.value = getMonthValue(new Date())
  }

  if (growthRangeMode.value === 'range') {
    selectedGrowthRange.value = createDefaultRangeValue()
  }

  loadStatistics()
}

const handleGrowthDateChange = () => {
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

const getSeriesTotal = (series: number[]) => {
  return series.reduce((total, value) => total + value, 0)
}

const todayNewUsers = computed(() => getLastValue(statisticsSnapshot.value.trends.daily_new.users))
const todayNewDevices = computed(() => getLastValue(statisticsSnapshot.value.trends.daily_new.devices))
const todayNewCards = computed(() => getLastValue(statisticsSnapshot.value.trends.daily_new.cards))
const todayRevenue = computed(() => getLastValue(statisticsSnapshot.value.sales_trend.daily_revenue.map(toDashboardAmount)))
const todayOrders = computed(() => getLastValue(statisticsSnapshot.value.sales_trend.daily_orders))
const allTimeRevenue = computed(() => statisticsSnapshot.value.all_time_revenue)
const totalRevenue = computed(() => toDashboardAmount(allTimeRevenue.value.total))

const averageDailyUsers = computed(() => getAverageValue(statisticsSnapshot.value.trends.daily_new.users))
const averageDailyCards = computed(() => getAverageValue(statisticsSnapshot.value.trends.daily_new.cards))
const averageDailyRevenue = computed(() => getAverageValue(statisticsSnapshot.value.sales_trend.daily_revenue.map(toDashboardAmount)))
const selectedRevenueTotal = computed(() => getSeriesTotal(statisticsSnapshot.value.sales_trend.daily_revenue.map(toDashboardAmount)))
const selectedOrderTotal = computed(() => getSeriesTotal(statisticsSnapshot.value.sales_trend.daily_orders))
const selectedNewUsersTotal = computed(() => getSeriesTotal(statisticsSnapshot.value.trends.daily_new.users))
const selectedNewDevicesTotal = computed(() => getSeriesTotal(statisticsSnapshot.value.trends.daily_new.devices))
const selectedNewCardsTotal = computed(() => getSeriesTotal(statisticsSnapshot.value.trends.daily_new.cards))

const abnormalUserRate = computed(() => {
  return getRate(statisticsSnapshot.value.users.banned, statisticsSnapshot.value.users.total)
})

const cardUsageRate = computed(() => {
  return getRate(statisticsSnapshot.value.cards.used, statisticsSnapshot.value.cards.total)
})

const cardDisableRate = computed(() => {
  return getRate(statisticsSnapshot.value.cards.disabled, statisticsSnapshot.value.cards.total)
})

const inventorySafetyRate = computed(() => {
  return getRate(statisticsSnapshot.value.cards.unused, statisticsSnapshot.value.cards.total)
})

/**
 * 增长协同率
 * @description 看新增设备是否跟上新增用户，代表进入系统的人是否真的完成设备接入。
 */
const userDeviceSynergyRate = computed(() => {
  return clampPercent((todayNewDevices.value / Math.max(todayNewUsers.value, 1)) * 100)
})

/**
 * 风险压力率
 * @description 把异常用户和封禁卡密合并为风险压力，更贴近业务分析视角。
 */
const riskPressureRate = computed(() => {
  const snapshot = statisticsSnapshot.value
  return getRate(snapshot.users.banned + snapshot.cards.disabled, snapshot.users.total + snapshot.cards.total)
})

const inventorySupportDays = computed(() => {
  return Math.round(statisticsSnapshot.value.cards.unused / Math.max(averageDailyUsers.value, 1))
})

/**
 * 系统采纳率
 * @description 作为"新用户进入后是否被使用"的粗略经营信号。
 */
const systemAdoptionRate = computed(() => {
  const growthSignal = clampPercent((todayNewUsers.value / Math.max(statisticsSnapshot.value.users.total, 1)) * 100)
  return Math.round(growthSignal * 0.35 + cardUsageRate.value * 0.45 + userDeviceSynergyRate.value * 0.2)
})

/**
 * 日增长质量序列
 * @description 用近 7 日新增用户、设备、卡密的相对强度构建一个趋势分数，
 * 方便从"量"进化到"质量"的观察。
 */
const growthQualitySeries = computed<number[]>(() => {
  const trends = statisticsSnapshot.value.trends.daily_new
  const userPeak = Math.max(getSeriesPeak(trends.users), 1)
  const devicePeak = Math.max(getSeriesPeak(trends.devices), 1)
  const cardPeak = Math.max(getSeriesPeak(trends.cards), 1)

  return trends.users.map((_, index) => {
    const userScore = ((trends.users[index] ?? 0) / userPeak) * 38
    const deviceScore = ((trends.devices[index] ?? 0) / devicePeak) * 30
    const cardScore = ((trends.cards[index] ?? 0) / cardPeak) * 20
    const stableScore = (100 - Math.min(riskPressureRate.value * 1.4, 100)) * 0.12

    return clampPercent(userScore + deviceScore + cardScore + stableScore)
  })
})

const currentGrowthQuality = computed(() => getLastValue(growthQualitySeries.value))
const averageGrowthQuality = computed(() => getAverageValue(growthQualitySeries.value))

/**
 * 活跃信号分
 * @description 把增长、卡密使用、异常压力和库存安全综合成一个更偏经营判断的分数。
 */
const activitySignalScore = computed(() => {
  const score = (
    systemAdoptionRate.value * 0.42 +
    currentGrowthQuality.value * 0.24 +
    (100 - Math.min(riskPressureRate.value * 1.5, 100)) * 0.18 +
    inventorySafetyRate.value * 0.16
  )

  return Math.round(score)
})

const strategicHeadline = computed(() => {
  const snapshot = statisticsSnapshot.value

  if (todayNewUsers.value > 0 && snapshot.cards.used > 0 && riskPressureRate.value <= 10) {
    return '当前已经形成"新增用户进入 + 卡密持续使用"的良性活跃信号'
  }

  if (todayNewUsers.value > 0 && snapshot.cards.used > 0) {
    return '当前存在增长和使用，但风险侧已经开始对经营质量形成压制'
  }

  return '当前总量仍在，但增长与卡密使用闭环信号偏弱，需要继续强化转化'
})

const strategicSubtitle = computed(() => {
  if (currentGrowthQuality.value >= averageGrowthQuality.value) {
    return `最新统计日增长质量分 ${currentGrowthQuality.value}，高于或等于${growthScopeLabel.value}均值 ${averageGrowthQuality.value.toFixed(1)}，经营状态偏积极。`
  }

  return `最新统计日增长质量分 ${currentGrowthQuality.value}，低于${growthScopeLabel.value}均值 ${averageGrowthQuality.value.toFixed(1)}，建议重点观察新增转化和风险拦截。`
})

const coreAnalysisCards = computed(() => {
  const snapshot = statisticsSnapshot.value

  return [
    {
      key: 'user-growth',
      label: '用户增长',
      value: `${todayNewUsers.value} 人`,
      rate: clampPercent((todayNewUsers.value / Math.max(snapshot.users.total, 1)) * 100),
      tag: `${growthScopeLabel.value}均值 ${averageDailyUsers.value}`,
      desc: `当前总用户 ${snapshot.users.total}，最新统计日新增与${growthScopeLabel.value}均值对比后更能看出增长是否还在持续。`,
      icon: User,
      iconClass: 'ink-user'
    },
    {
      key: 'abnormal-users',
      label: '异常用户',
      value: `${snapshot.users.banned} 人`,
      rate: abnormalUserRate.value,
      tag: `占比 ${abnormalUserRate.value}%`,
      desc: '异常用户越多，越要分辨是真风险上升，还是封禁策略过于敏感。 ',
      icon: WarningFilled,
      iconClass: 'ink-warning'
    },
    {
      key: 'card-usage',
      label: '最新销售额',
      value: formatCurrency(todayRevenue.value),
      rate: clampPercent((todayRevenue.value / Math.max(averageDailyRevenue.value, 1)) * 100),
      tag: `订单 ${todayOrders.value} 笔`,
      desc: `销售额按卡密生成日期统计，${growthScopeLabel.value}日均为 ${formatCurrency(averageDailyRevenue.value)}。`,
      icon: Ticket,
      iconClass: 'ink-ticket'
    },
    {
      key: 'ban-count',
      label: '封禁数量',
      value: `${snapshot.cards.disabled} 个`,
      rate: cardDisableRate.value,
      tag: `封禁率 ${cardDisableRate.value}%`,
      desc: '封禁数量既体现风险控制强度，也会直接压缩可用库存和新增承接能力。 ',
      icon: Grid,
      iconClass: 'ink-grid'
    }
  ]
})

const growthInsights = computed(() => {
  const snapshot = statisticsSnapshot.value

  return [
    {
      label: '用户增长对比',
      text: todayNewUsers.value >= averageDailyUsers.value
        ? `最新统计日新增用户 ${todayNewUsers.value} 人，高于或等于${growthScopeLabel.value}均值 ${averageDailyUsers.value}，拉新表现偏积极。`
        : `最新统计日新增用户 ${todayNewUsers.value} 人，低于${growthScopeLabel.value}均值 ${averageDailyUsers.value}，增长动能相对偏弱。`,
      levelClass: todayNewUsers.value >= averageDailyUsers.value ? 'level-info' : 'level-warning'
    },
    {
      label: '用户与卡密使用联动',
      text: snapshot.cards.used > 0 && todayNewUsers.value > 0
        ? `当前已使用卡密 ${snapshot.cards.used} 个，同时今日仍有新增用户，说明系统存在真实进入与使用行为。`
        : '当前用户增长或卡密使用信号不足，暂时还看不到明确的使用闭环。 ',
      levelClass: snapshot.cards.used > 0 && todayNewUsers.value > 0 ? 'level-success' : 'level-warning'
    },
    {
      label: '设备跟随增长',
      text: userDeviceSynergyRate.value >= 100
        ? `新增设备已经跟上新增用户，协同率 ${userDeviceSynergyRate.value}% ，接入转化较顺畅。`
        : `新增设备跟随不足，协同率 ${userDeviceSynergyRate.value}% ，需要关注用户进入后的激活漏损。`,
      levelClass: userDeviceSynergyRate.value >= 100 ? 'level-success' : 'level-info'
    },
    {
      label: '新增卡密承接',
      text: todayNewCards.value >= averageDailyCards.value
        ? `最新统计日新增卡密 ${todayNewCards.value} 个，已达到或超过${growthScopeLabel.value}均值 ${averageDailyCards.value}，库存承接较主动。`
        : `最新统计日新增卡密 ${todayNewCards.value} 个，低于${growthScopeLabel.value}均值 ${averageDailyCards.value}，新增承接力度一般。`,
      levelClass: todayNewCards.value >= averageDailyCards.value ? 'level-info' : 'level-warning'
    }
  ]
})

const riskInsights = computed(() => {
  const snapshot = statisticsSnapshot.value

  return [
    {
      label: '异常用户占比',
      text: abnormalUserRate.value > 10
        ? `异常用户占比为 ${abnormalUserRate.value}% ，相对偏高，建议重点复核风控策略和封禁原因。`
        : `异常用户占比为 ${abnormalUserRate.value}% ，当前仍在可控范围内。`,
      levelClass: abnormalUserRate.value > 10 ? 'level-danger' : 'level-success'
    },
    {
      label: '封禁卡密影响',
      text: snapshot.cards.disabled > 0
        ? `当前共有 ${snapshot.cards.disabled} 个封禁卡密，会直接挤压库存和新用户承接能力。`
        : '当前暂无封禁卡密，库存质量相对稳定。 ',
      levelClass: snapshot.cards.disabled > 0 ? 'level-warning' : 'level-success'
    },
    {
      label: '风险压力',
      text: riskPressureRate.value > 8
        ? `用户异常与卡密封禁合并后的风险压力为 ${riskPressureRate.value}% ，需要重点关注风险侧是否开始影响增长质量。`
        : `综合风险压力为 ${riskPressureRate.value}% ，暂未明显侵蚀增长质量。`,
      levelClass: riskPressureRate.value > 8 ? 'level-warning' : 'level-info'
    },
    {
      label: '库存安全',
      text: inventorySafetyRate.value > 20
        ? `未使用卡密占比 ${inventorySafetyRate.value}% ，库存仍有一定安全垫。`
        : `未使用卡密占比 ${inventorySafetyRate.value}% ，库存安全边际偏薄。`,
      levelClass: inventorySafetyRate.value > 20 ? 'level-success' : 'level-warning'
    }
  ]
})

const decisionInsights = computed(() => {
  const snapshot = statisticsSnapshot.value

  return [
    {
      label: '经营判断',
      text: strategicHeadline.value,
      levelClass: activitySignalScore.value >= 70 ? 'level-success' : 'level-warning'
    },
    {
      label: '质量判断',
      text: `最新统计日增长质量分 ${currentGrowthQuality.value}，${growthScopeLabel.value}均值 ${averageGrowthQuality.value.toFixed(1)}。`,
      levelClass: currentGrowthQuality.value >= averageGrowthQuality.value ? 'level-info' : 'level-warning'
    },
    {
      label: '库存判断',
      text: `当前库存预计还能支撑约 ${inventorySupportDays.value} 天，未使用卡密 ${snapshot.cards.unused} 个。`,
      levelClass: inventorySupportDays.value >= 7 ? 'level-success' : 'level-warning'
    },
    {
      label: '重点关注',
      text: riskPressureRate.value > 8
        ? '建议优先看异常用户与封禁卡密是否过快上升，再看增长是否还能转成有效使用。'
        : '建议继续观察新增用户和卡密使用是否同步增长，确认系统活跃度是否稳步抬升。',
      levelClass: riskPressureRate.value > 8 ? 'level-danger' : 'level-info'
    }
  ]
})

const growthScatterData = computed(() => {
  const trends = statisticsSnapshot.value.trends

  return trends.labels.map((label, index) => {
    return {
      name: label,
      value: [
        trends.daily_new.users[index] ?? 0,
        trends.daily_new.devices[index] ?? 0,
        trends.daily_new.cards[index] ?? 0
      ]
    }
  })
})

const salesTrendSummary = computed<ChartSummaryItem[]>(() => [
  { label: '范围销售额', value: formatCurrency(selectedRevenueTotal.value) },
  { label: '范围订单数', value: `${selectedOrderTotal.value} 笔` },
  { label: '日均销售额', value: formatCurrency(averageDailyRevenue.value) },
  { label: '最新客单价', value: formatCurrency(getLastValue(statisticsSnapshot.value.sales_trend.average_order_value.map(toDashboardAmount))) }
])

const growthCompareSummary = computed<ChartSummaryItem[]>(() => [
  { label: '新增用户', value: `${selectedNewUsersTotal.value} 人` },
  { label: '新增设备', value: `${selectedNewDevicesTotal.value} 台` },
  { label: '新增卡密', value: `${selectedNewCardsTotal.value} 个` },
  { label: '设备协同', value: `${userDeviceSynergyRate.value}%` }
])

const growthQualitySummary = computed<ChartSummaryItem[]>(() => [
  { label: '最新质量分', value: `${currentGrowthQuality.value} 分` },
  { label: '范围均值', value: `${averageGrowthQuality.value.toFixed(1)} 分` },
  { label: '最高质量分', value: `${getSeriesPeak(growthQualitySeries.value)} 分` },
  { label: '风险压力', value: `${riskPressureRate.value}%` }
])

const cumulativeTrendSummary = computed<ChartSummaryItem[]>(() => {
  const cumulative = statisticsSnapshot.value.trends.cumulative

  return [
    { label: '累计用户', value: `${getLastValue(cumulative.users)} 人` },
    { label: '累计设备', value: `${getLastValue(cumulative.devices)} 台` },
    { label: '累计卡密', value: `${getLastValue(cumulative.cards)} 个` },
    { label: '累计应用', value: `${getLastValue(cumulative.apps)} 个` }
  ]
})

const keyMetricsSummary = computed<ChartSummaryItem[]>(() => {
  const snapshot = statisticsSnapshot.value

  return [
    { label: '卡密使用率', value: `${cardUsageRate.value}%` },
    { label: '库存卡密', value: `${snapshot.cards.unused} 个` },
    { label: '异常用户', value: `${snapshot.users.banned} 人` },
    { label: '封禁卡密', value: `${snapshot.cards.disabled} 个` }
  ]
})

const growthScatterSummary = computed<ChartSummaryItem[]>(() => [
  { label: '新增用户峰值', value: `${getSeriesPeak(statisticsSnapshot.value.trends.daily_new.users)} 人` },
  { label: '新增设备峰值', value: `${getSeriesPeak(statisticsSnapshot.value.trends.daily_new.devices)} 台` },
  { label: '新增卡密峰值', value: `${getSeriesPeak(statisticsSnapshot.value.trends.daily_new.cards)} 个` },
  { label: '协同点数', value: `${statisticsSnapshot.value.trends.labels.length} 个` }
])

const radarMetrics = computed<number[]>(() => {
  const snapshot = statisticsSnapshot.value
  const userPeak = Math.max(getSeriesPeak(snapshot.trends.daily_new.users), 1)

  return [
    clampPercent((todayNewUsers.value / userPeak) * 100),
    userDeviceSynergyRate.value,
    cardUsageRate.value,
    100 - abnormalUserRate.value,
    100 - cardDisableRate.value,
    inventorySafetyRate.value
  ]
})

const getChartElement = (chartKey: ChartKey) => {
  const elementMap: Record<ChartKey, HTMLDivElement | undefined> = {
    salesTrend: salesTrendRef.value,
    growthCompare: growthCompareRef.value,
    userRisk: userRiskRef.value,
    growthQuality: growthQualityRef.value,
    keyMetrics: keyMetricsRef.value,
    cardUsage: cardUsageRef.value,
    growthScatter: growthScatterRef.value,
    cumulativeTrend: cumulativeTrendRef.value,
    analysisRadar: analysisRadarRef.value
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

const renderSalesTrend = () => {
  const instance = ensureChartInstance('salesTrend')
  if (!instance) return

  const salesTrend = statisticsSnapshot.value.sales_trend
  const revenueSeries = salesTrend.daily_revenue.map(toDashboardAmount)
  const averageOrderValue = salesTrend.average_order_value.map(toDashboardAmount)

  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const index = params[0].dataIndex
        return `${salesTrend.labels[index]}<br/>销售额：${formatCurrency(revenueSeries[index])}<br/>订单数：${salesTrend.daily_orders[index] ?? 0}<br/>客单价：${formatCurrency(averageOrderValue[index])}`
      }
    },
    legend: {
      top: 0,
      textStyle: { color: '#57534e' }
    },
    grid: {
      left: '4%',
      right: '5%',
      top: '14%',
      bottom: '6%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: salesTrend.labels,
      axisTick: { show: false },
      axisLine: { lineStyle: { color: '#d6d3d1' } },
      axisLabel: { color: '#57534e' }
    },
    yAxis: [
      {
        type: 'value',
        name: '销售额',
        splitLine: { lineStyle: { color: '#ece7e1' } },
        axisLabel: {
          color: '#78716c',
          formatter: (value: number) => formatCurrency(value)
        }
      },
      {
        type: 'value',
        name: '订单数',
        splitLine: { show: false },
        axisLabel: { color: '#78716c' }
      }
    ],
    series: [
      {
        name: '销售额',
        type: 'line',
        smooth: true,
        symbolSize: 9,
        lineStyle: { width: 3, color: '#111827' },
        itemStyle: { color: '#111827', borderColor: '#ffffff', borderWidth: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(17, 24, 39, 0.18)' },
            { offset: 1, color: 'rgba(17, 24, 39, 0.02)' }
          ])
        },
        data: revenueSeries
      },
      {
        name: '订单数',
        type: 'bar',
        yAxisIndex: 1,
        barWidth: 18,
        itemStyle: {
          color: 'rgba(180, 83, 9, 0.42)',
          borderRadius: [8, 8, 0, 0]
        },
        data: salesTrend.daily_orders
      }
    ]
  }

  instance.setOption(option)
}

const renderGrowthCompare = () => {
  const instance = ensureChartInstance('growthCompare')
  if (!instance) return

  const trends = statisticsSnapshot.value.trends

  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      top: 0,
      textStyle: { color: '#57534e' }
    },
    grid: {
      left: '4%',
      right: '4%',
      top: '14%',
      bottom: '6%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: trends.labels,
      axisTick: { show: false },
      axisLine: { lineStyle: { color: '#d6d3d1' } },
      axisLabel: { color: '#57534e' }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#ece7e1' } },
      axisLabel: { color: '#78716c' }
    },
    series: [
      {
        name: '新增用户',
        type: 'line',
        smooth: true,
        symbolSize: 8,
        lineStyle: { width: 3, color: '#111827' },
        itemStyle: { color: '#111827', borderColor: '#ffffff', borderWidth: 2 },
        data: trends.daily_new.users
      },
      {
        name: '新增设备',
        type: 'line',
        smooth: true,
        symbolSize: 8,
        lineStyle: { width: 3, color: '#6b7280' },
        itemStyle: { color: '#6b7280', borderColor: '#ffffff', borderWidth: 2 },
        data: trends.daily_new.devices
      },
      {
        name: '新增卡密',
        type: 'line',
        smooth: true,
        symbolSize: 8,
        lineStyle: { width: 3, color: '#b45309' },
        itemStyle: { color: '#b45309', borderColor: '#ffffff', borderWidth: 2 },
        data: trends.daily_new.cards
      }
    ]
  }

  instance.setOption(option)
}

const renderUserRisk = () => {
  const instance = ensureChartInstance('userRisk')
  if (!instance) return

  const snapshot = statisticsSnapshot.value

  const option: EChartsOption = {
    color: ['#1f2937', '#b45309'],
    tooltip: {
      trigger: 'item',
      formatter: '{b}<br/>数量：{c} ({d}%)'
    },
    legend: {
      bottom: 0,
      icon: 'circle',
      textStyle: { color: '#57534e' }
    },
    series: [
      {
        type: 'pie',
        radius: ['44%', '72%'],
        center: ['50%', '42%'],
        label: { show: true, formatter: '{b}\n{c}' },
        itemStyle: {
          borderColor: '#ffffff',
          borderWidth: 4,
          borderRadius: 8
        },
        data: [
          { value: snapshot.users.normal, name: '正常用户' },
          { value: snapshot.users.banned, name: '异常用户' }
        ]
      }
    ]
  }

  instance.setOption(option)
}

const renderGrowthQuality = () => {
  const instance = ensureChartInstance('growthQuality')
  if (!instance) return

  const trends = statisticsSnapshot.value.trends

  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      top: 0,
      textStyle: { color: '#57534e' }
    },
    grid: {
      left: '4%',
      right: '6%',
      top: '14%',
      bottom: '6%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: trends.labels,
      axisTick: { show: false },
      axisLine: { lineStyle: { color: '#d6d3d1' } },
      axisLabel: { color: '#57534e' }
    },
    yAxis: [
      {
        type: 'value',
        min: 0,
        max: 100,
        splitLine: { lineStyle: { color: '#ece7e1' } },
        axisLabel: { color: '#78716c', formatter: '{value}' }
      },
      {
        type: 'value',
        splitLine: { show: false },
        axisLabel: { color: '#78716c' }
      }
    ],
    series: [
      {
        name: '增长质量分',
        type: 'line',
        smooth: true,
        symbolSize: 8,
        lineStyle: { width: 3, color: '#111827' },
        itemStyle: { color: '#111827' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(17, 24, 39, 0.18)' },
            { offset: 1, color: 'rgba(17, 24, 39, 0.02)' }
          ])
        },
        data: growthQualitySeries.value
      },
      {
        name: '新增用户',
        type: 'bar',
        yAxisIndex: 1,
        barWidth: 16,
        itemStyle: {
          color: 'rgba(180, 83, 9, 0.35)',
          borderRadius: [8, 8, 0, 0]
        },
        data: trends.daily_new.users
      }
    ]
  }

  instance.setOption(option)
}

const renderKeyMetrics = () => {
  const instance = ensureChartInstance('keyMetrics')
  if (!instance) return

  const snapshot = statisticsSnapshot.value

  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '4%',
      right: '4%',
      top: '12%',
      bottom: '6%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['最新新增用户', '最新新增设备', '已使用卡密', '异常用户', '封禁卡密', '库存卡密'],
      axisTick: { show: false },
      axisLine: { lineStyle: { color: '#d6d3d1' } },
      axisLabel: {
        color: '#57534e',
        interval: 0
      }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#ece7e1' } },
      axisLabel: { color: '#78716c' }
    },
    series: [
      {
        type: 'bar',
        barWidth: '42%',
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#111827' },
            { offset: 1, color: '#a8a29e' }
          ])
        },
        label: {
          show: true,
          position: 'top',
          color: '#111827'
        },
        data: [
          todayNewUsers.value,
          todayNewDevices.value,
          snapshot.cards.used,
          snapshot.users.banned,
          snapshot.cards.disabled,
          snapshot.cards.unused
        ]
      }
    ]
  }

  instance.setOption(option)
}

const renderCardUsage = () => {
  const instance = ensureChartInstance('cardUsage')
  if (!instance) return

  const snapshot = statisticsSnapshot.value

  const option: EChartsOption = {
    color: ['#0f766e', '#b45309', '#9f1239'],
    tooltip: {
      trigger: 'item',
      formatter: '{b}<br/>数量：{c} ({d}%)'
    },
    legend: {
      bottom: 0,
      icon: 'circle',
      textStyle: { color: '#57534e' }
    },
    series: [
      {
        type: 'pie',
        roseType: 'radius',
        radius: [24, 82],
        center: ['50%', '42%'],
        label: { formatter: '{b}\n{c}' },
        data: [
          { value: snapshot.cards.used, name: '已使用卡密' },
          { value: snapshot.cards.disabled, name: '封禁卡密' },
          { value: snapshot.cards.unused, name: '未使用卡密' }
        ]
      }
    ]
  }

  instance.setOption(option)
}

const renderGrowthScatter = () => {
  const instance = ensureChartInstance('growthScatter')
  if (!instance) return

  const option: EChartsOption = {
    tooltip: {
      formatter: (params: any) => {
        const point = params.data as { name: string, value: number[] }
        return `${point.name}<br/>新增用户：${point.value[0]}<br/>新增设备：${point.value[1]}<br/>新增卡密：${point.value[2]}`
      }
    },
    xAxis: {
      type: 'value',
      name: '新增用户',
      nameTextStyle: { color: '#57534e' },
      axisLine: { lineStyle: { color: '#d6d3d1' } },
      splitLine: { lineStyle: { color: '#ece7e1' } },
      axisLabel: { color: '#78716c' }
    },
    yAxis: {
      type: 'value',
      name: '新增设备',
      nameTextStyle: { color: '#57534e' },
      axisLine: { lineStyle: { color: '#d6d3d1' } },
      splitLine: { lineStyle: { color: '#ece7e1' } },
      axisLabel: { color: '#78716c' }
    },
    series: [
      {
        type: 'scatter',
        data: growthScatterData.value,
        symbolSize: (value: ArrayLike<number>) => {
          return 18 + (value[2] ?? 0) * 4
        },
        itemStyle: {
          color: 'rgba(17, 24, 39, 0.72)',
          borderColor: '#ffffff',
          borderWidth: 2,
          shadowBlur: 12,
          shadowColor: 'rgba(17, 24, 39, 0.12)'
        },
        label: {
          show: true,
          formatter: (params: any) => params.data.name,
          position: 'top',
          color: '#57534e'
        }
      }
    ]
  }

  instance.setOption(option)
}

const renderCumulativeTrend = () => {
  const instance = ensureChartInstance('cumulativeTrend')
  if (!instance) return

  const trends = statisticsSnapshot.value.trends

  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      top: 0,
      textStyle: { color: '#57534e' }
    },
    grid: {
      left: '4%',
      right: '4%',
      top: '14%',
      bottom: '6%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: trends.labels,
      axisTick: { show: false },
      axisLine: { lineStyle: { color: '#d6d3d1' } },
      axisLabel: { color: '#57534e' }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#ece7e1' } },
      axisLabel: { color: '#78716c' }
    },
    series: [
      {
        name: '累计用户',
        type: 'line',
        smooth: true,
        symbolSize: 7,
        lineStyle: { width: 2.5, color: '#111827' },
        itemStyle: { color: '#111827' },
        data: trends.cumulative.users
      },
      {
        name: '累计设备',
        type: 'line',
        smooth: true,
        symbolSize: 7,
        lineStyle: { width: 2.5, color: '#6b7280' },
        itemStyle: { color: '#6b7280' },
        data: trends.cumulative.devices
      },
      {
        name: '累计卡密',
        type: 'line',
        smooth: true,
        symbolSize: 7,
        lineStyle: { width: 2.5, color: '#b45309' },
        itemStyle: { color: '#b45309' },
        data: trends.cumulative.cards
      }
    ]
  }

  instance.setOption(option)
}

const renderAnalysisRadar = () => {
  const instance = ensureChartInstance('analysisRadar')
  if (!instance) return

  const option: EChartsOption = {
    color: ['#111827'],
    radar: {
      radius: '64%',
      splitNumber: 5,
      axisName: { color: '#44403c', fontWeight: 600 },
      splitLine: { lineStyle: { color: 'rgba(214, 211, 209, 0.8)' } },
      splitArea: {
        areaStyle: {
          color: ['rgba(255,255,255,0.18)', 'rgba(245,245,244,0.9)']
        }
      },
      indicator: [
        { name: '新增动能', max: 100 },
        { name: '设备协同', max: 100 },
        { name: '卡密使用', max: 100 },
        { name: '异常控制', max: 100 },
        { name: '封禁压力', max: 100 },
        { name: '库存安全', max: 100 }
      ]
    },
    series: [
      {
        type: 'radar',
        areaStyle: {
          color: 'rgba(17, 24, 39, 0.14)'
        },
        lineStyle: {
          width: 3
        },
        symbolSize: 8,
        data: [
          {
            value: radarMetrics.value
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

  console.info('[水墨仪表盘] 开始渲染图表', {
    users: statistics.value.users,
    cards: statistics.value.cards,
    devices: statistics.value.devices,
    apps: statistics.value.apps,
    trends: statistics.value.trends,
    growthQualitySeries: growthQualitySeries.value
  })

  renderSalesTrend()
  renderGrowthCompare()
  renderUserRisk()
  renderGrowthQuality()
  renderKeyMetrics()
  renderCardUsage()
  renderGrowthScatter()
  renderCumulativeTrend()
  renderAnalysisRadar()
}

const loadStatistics = async () => {
  loading.value = true
  const query = growthQueryRange.value
  console.info('[水墨仪表盘] 开始加载统计数据', query)

  try {
    const data = await getStatistics(query)
    statistics.value = data
    lastUpdatedAt.value = new Date()

    console.info('[水墨仪表盘] 统计数据加载成功', {
      users: data.users,
      cards: data.cards,
      devices: data.devices,
      apps: data.apps,
      revenueRange: data.revenue_range,
      trendRange: data.trend_range,
      trendLabels: data.trends.labels
    })
    ElMessage.success('水墨仪表盘数据已刷新')

    await renderAllCharts()
  } catch (error) {
    ElMessage.error('加载水墨仪表盘数据失败')
    console.error('[水墨仪表盘] 加载统计数据失败', error)
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
    'salesTrend',
    'growthCompare',
    'userRisk',
    'growthQuality',
    'keyMetrics',
    'cardUsage',
    'growthScatter',
    'cumulativeTrend',
    'analysisRadar'
  ]

  chartKeys.forEach((chartKey) => {
    chartInstances[chartKey]?.dispose()
    delete chartInstances[chartKey]
  })
}

onMounted(() => {
  console.info('[水墨仪表盘] 页面挂载，准备初始化增长分析看板')
  loadStatistics()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  console.info('[水墨仪表盘] 页面卸载，开始清理图表实例')
  window.removeEventListener('resize', handleResize)
  disposeCharts()
})
</script>

<style scoped>
@reference "../../styles/index.css";

.ink-dashboard {
  @apply min-h-full px-6 py-6 lg:px-8;
  background:
    radial-gradient(circle at top left, rgba(17, 24, 39, 0.06), transparent 22%),
    radial-gradient(circle at 86% 10%, rgba(146, 64, 14, 0.1), transparent 20%),
    linear-gradient(180deg, #f6f4ef 0%, #f3f0e8 48%, #f8f6f1 100%);
  position: relative;
  overflow: hidden;
}

.ink-dashboard::before {
  content: '';
  position: absolute;
  inset: 40px auto auto -120px;
  width: 360px;
  height: 360px;
  border-radius: 9999px;
  background: radial-gradient(circle, rgba(17, 24, 39, 0.08), transparent 70%);
  filter: blur(20px);
  pointer-events: none;
}

.ink-dashboard::after {
  content: '';
  position: absolute;
  right: -100px;
  top: 320px;
  width: 300px;
  height: 420px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(180, 83, 9, 0.08), transparent 72%);
  filter: blur(30px);
  pointer-events: none;
}

.ink-hero,
.ink-quote-strip,
.ink-metric-card,
.ink-panel,
.ink-chart-card {
  position: relative;
  overflow: hidden;
}

.ink-quote-strip > * {
  position: relative;
  z-index: 1;
}

.ink-quote-tag {
  @apply inline-flex items-center rounded-full px-3 py-1 text-xs uppercase tracking-[0.22em];
  @apply border border-stone-300 bg-stone-100/90 text-stone-700;
}

.ink-panel-title {
  font-family: "Noto Serif SC", "Songti SC", "STSong", serif;
}

.ink-hero {
  @apply rounded-[34px] border border-stone-300/80 px-6 py-6 lg:px-10 lg:py-8 mb-5;
  @apply shadow-sm flex flex-col items-center text-center;
  background:
    radial-gradient(circle at 50% 30%, rgba(17, 24, 39, 0.06), transparent 50%),
    radial-gradient(circle at 80% 60%, rgba(180, 83, 9, 0.06), transparent 35%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.92) 0%, rgba(250, 248, 243, 0.88) 100%);
}

.ink-hero::before {
  content: '';
  position: absolute;
  inset: -20% auto auto 55%;
  width: 280px;
  height: 280px;
  border-radius: 9999px;
  background: radial-gradient(circle, rgba(17, 24, 39, 0.08), transparent 68%);
  filter: blur(18px);
}

.ink-hero::after {
  content: '';
  position: absolute;
  left: 50%;
  bottom: -40px;
  width: 60%;
  height: 80px;
  transform: translateX(-50%);
  background: radial-gradient(ellipse, rgba(120, 113, 108, 0.06), transparent 72%);
  filter: blur(16px);
}

/* 刷新按钮 */
.ink-refresh-btn {
  @apply absolute right-6 top-6 z-10;
  @apply rounded-2xl border border-stone-700 bg-stone-900 text-white font-medium;
  @apply hover:bg-stone-800 hover:text-white;
}

/* 总收入核心区 */
.ink-revenue-center {
  @apply relative z-[1] flex flex-col items-center;
}

.ink-revenue-stamp {
  @apply mb-3;
}

.ink-revenue-stamp-text {
  @apply inline-flex items-center rounded-full px-4 py-1.5 text-xs uppercase tracking-[0.24em] font-medium;
  @apply border border-stone-400/60 bg-stone-200/50 text-stone-600;
  letter-spacing: 0.28em;
}

.ink-revenue-main {
  @apply flex items-baseline gap-1;
}

.ink-revenue-prefix {
  @apply text-2xl lg:text-3xl font-light text-stone-400;
  font-family: "Noto Serif SC", "Songti SC", "STSong", serif;
}

.ink-revenue-amount {
  @apply text-4xl sm:text-5xl lg:text-6xl font-bold text-stone-900 tracking-tight;
  font-family: "Noto Serif SC", "Songti SC", "STSong", serif;
  line-height: 1.1;
}

.ink-revenue-breakdown {
  @apply mt-4 flex flex-wrap justify-center gap-3;
}

.ink-revenue-chip {
  @apply inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-sm font-medium;
  @apply border border-stone-200/80 bg-white/70 backdrop-blur-sm;
}

.ink-chip-dot {
  @apply w-2 h-2 rounded-full;
}

.ink-chip-active .ink-chip-dot {
  background: #111827;
  box-shadow: 0 0 6px rgba(17, 24, 39, 0.3);
}

.ink-chip-stock .ink-chip-dot {
  background: #a8a29e;
}

/* 指标横条 */
.ink-hero-metrics {
  @apply relative z-[1] mt-6 flex flex-wrap items-center justify-center gap-0;
  @apply rounded-2xl border border-stone-200/80 bg-white/60 backdrop-blur-sm px-2 py-0;
}

.ink-metric-pill {
  @apply flex flex-col items-center px-5 py-3;
}

.ink-metric-pill-label {
  @apply text-xs text-stone-400 font-medium tracking-wide;
}

.ink-metric-pill-value {
  @apply mt-1 text-sm font-semibold text-stone-900 tabular-nums;
}

.ink-metric-pill-value small {
  @apply text-xs font-normal text-stone-500 ml-0.5;
}

.ink-value-revenue {
  color: #92400e;
}

.ink-metric-divider {
  @apply w-px h-8 bg-stone-200/80;
}

.ink-quote-strip {
  @apply mb-6 rounded-[28px] border border-stone-300/80 px-6 py-6 lg:px-8 lg:py-7;
  background:
    radial-gradient(circle at top left, rgba(17, 24, 39, 0.05), transparent 40%),
    radial-gradient(circle at bottom right, rgba(180, 83, 9, 0.04), transparent 35%),
    linear-gradient(135deg, rgba(255,255,255,0.80) 0%, rgba(248,245,240,0.88) 100%);
}

.ink-quote-strip::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, rgba(17, 24, 39, 0.6), rgba(180, 83, 9, 0.25), transparent);
  border-radius: 9999px;
}

.ink-quote-strip::after {
  content: '';
  position: absolute;
  right: -20px;
  bottom: -30px;
  width: 180px;
  height: 180px;
  border-radius: 9999px;
  background: radial-gradient(circle, rgba(120, 113, 108, 0.06), transparent 70%);
  filter: blur(14px);
  pointer-events: none;
}

.ink-quote-strip strong {
  @apply mt-3 block text-lg lg:text-xl font-semibold text-stone-900 leading-8;
  font-family: "Noto Serif SC", "Songti SC", "STSong", serif;
}

.ink-quote-strip p {
  @apply mt-2 text-sm leading-7 text-stone-600;
}

.ink-quote-meta {
  @apply mt-5 pt-4 border-t border-stone-200/60 flex flex-wrap gap-2;
}

.ink-quote-meta span {
  @apply inline-flex items-center gap-1.5 rounded-full px-3.5 py-1.5 text-xs font-medium;
  @apply border border-stone-200/70 bg-white/60 text-stone-600;
}

/* ========== Suite 通用 ========== */
.ink-growth-suite,
.ink-risk-suite {
  @apply mb-6 rounded-[28px] border border-stone-300/70 p-5 lg:p-7 shadow-sm;
  background:
    radial-gradient(circle at top left, rgba(17, 24, 39, 0.03), transparent 35%),
    linear-gradient(180deg, rgba(255,255,255,0.86) 0%, rgba(248,245,240,0.90) 100%);
}

.ink-suite-toolbar {
  @apply flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between mb-6;
  @apply pb-5 border-b border-stone-200/50;
}

.ink-suite-text {
  @apply mt-2 text-sm leading-6 text-stone-500 max-w-xl;
}

.ink-suite-controls {
  @apply flex flex-col gap-3 lg:flex-row lg:flex-wrap lg:items-center xl:justify-end;
}

/* ========== 指标卡片网格 ========== */
.ink-metric-grid {
  @apply grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mb-6;
}

.ink-metric-card,
.ink-panel,
.ink-chart-card {
  @apply rounded-[24px] border border-stone-300/60 shadow-sm;
  background:
    linear-gradient(180deg, rgba(255,255,255,0.88) 0%, rgba(250,248,243,0.92) 100%);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.ink-metric-card:hover {
  box-shadow: 0 8px 24px rgba(17, 24, 39, 0.06);
  transform: translateY(-1px);
}

.ink-metric-card::before,
.ink-panel::before,
.ink-chart-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 24px;
  width: 48px;
  height: 3px;
  border-radius: 9999px;
  background: linear-gradient(90deg, rgba(17,24,39,0.55), rgba(180,83,9,0.2));
}

.ink-metric-card {
  @apply p-5 lg:p-6;
}

.ink-metric-head {
  @apply flex items-center justify-between mb-4;
}

.ink-metric-icon {
  @apply w-11 h-11 rounded-xl flex items-center justify-center;
  border: 1px solid rgba(0,0,0,0.04);
}

.ink-user {
  @apply bg-stone-100 text-stone-700;
}

.ink-warning {
  @apply bg-amber-50 text-amber-700;
  border-color: rgba(217, 119, 6, 0.1);
}

.ink-ticket {
  @apply bg-emerald-50 text-emerald-700;
  border-color: rgba(4, 120, 87, 0.1);
}

.ink-grid {
  @apply bg-rose-50 text-rose-700;
  border-color: rgba(190, 18, 60, 0.1);
}

.ink-metric-tag {
  @apply inline-flex items-center rounded-full px-3 py-1 text-xs font-medium;
  @apply text-stone-500 bg-stone-50 border border-stone-200/60;
}

.ink-metric-label {
  @apply block text-xs text-stone-400 font-medium tracking-wide uppercase;
}

.ink-metric-value {
  @apply block mt-2 text-3xl font-bold text-stone-900 tabular-nums;
  font-family: "Noto Serif SC", "Songti SC", "STSong", serif;
}

.ink-metric-progress {
  @apply mt-4 flex items-center gap-3;
}

.ink-metric-progress-track {
  @apply flex-1 h-1.5 rounded-full overflow-hidden;
  background: rgba(168, 162, 158, 0.15);
}

.ink-metric-progress-bar {
  @apply h-full rounded-full;
  background: linear-gradient(90deg, rgba(17, 24, 39, 0.7), rgba(168, 162, 158, 0.5));
}

.ink-metric-progress span {
  @apply text-xs font-semibold text-stone-400 tabular-nums;
}

.ink-metric-desc {
  @apply mt-4 text-xs leading-6 text-stone-500;
  min-height: 48px;
}

/* ========== 分析面板网格 ========== */
.ink-analysis-grid {
  @apply grid grid-cols-1 xl:grid-cols-3 gap-4 mb-6;
}

.ink-panel,
.ink-chart-card {
  @apply p-5 lg:p-6;
}

.ink-panel-head {
  @apply flex items-start justify-between gap-4 mb-5 pb-4 border-b border-stone-100;
}

.ink-chart-summary {
  @apply grid grid-cols-2 lg:grid-cols-4 gap-2 mb-4;
}

.ink-chart-summary-item {
  @apply rounded-xl border border-stone-200/70 bg-white/60 px-3 py-2;
}

.ink-chart-summary-item span {
  @apply block text-[11px] leading-4 text-stone-400 font-medium;
}

.ink-chart-summary-item strong {
  @apply mt-1 block text-sm font-semibold text-stone-900 tabular-nums;
}

.ink-panel-eyebrow {
  @apply text-[11px] uppercase tracking-[0.22em] text-stone-400 font-medium;
}

.ink-panel-title {
  @apply mt-1 text-lg font-semibold text-stone-900;
  font-family: "Noto Serif SC", "Songti SC", "STSong", serif;
}

.ink-panel-icon {
  @apply flex items-center justify-center w-10 h-10 rounded-xl;
  @apply bg-stone-50 text-stone-600;
  border: 1px solid rgba(0,0,0,0.04);
}

.ink-analysis-list {
  @apply space-y-3;
}

.ink-analysis-item {
  @apply flex items-start gap-3 rounded-xl p-3;
  transition: background 0.15s ease;
}

.ink-analysis-item:hover {
  background: rgba(245, 243, 238, 0.5);
}

.ink-analysis-dot {
  @apply mt-1.5 w-2 h-2 rounded-full shrink-0;
  box-shadow: 0 0 4px currentColor;
}

.ink-analysis-content strong {
  @apply block text-sm font-semibold text-stone-800;
}

.ink-analysis-content p {
  @apply mt-1 text-[13px] leading-6 text-stone-500;
}

/* 水墨色系：浓淡墨 + 赭石 */
.level-success {
  background: #047857;
  color: #047857;
}

.level-info {
  background: #374151;
  color: #374151;
}

.level-warning {
  background: #b45309;
  color: #b45309;
}

.level-danger {
  background: #9f1239;
  color: #9f1239;
}

/* ========== 图表网格 ========== */
.ink-chart-grid {
  @apply grid grid-cols-1 xl:grid-cols-3 gap-4;
}

.ink-growth-chart-grid {
  @apply grid grid-cols-1 xl:grid-cols-4 gap-4;
}

.ink-risk-chart-grid {
  @apply grid grid-cols-1 xl:grid-cols-3 gap-4;
}

.ink-chart-wide {
  @apply xl:col-span-2;
}

.ink-chart {
  width: 100%;
  height: 320px;
}

.ink-chart-medium {
  height: 340px;
}

.ink-chart-large {
  height: 360px;
}

/* ========== 响应式 ========== */
@media (max-width: 768px) {
  .ink-dashboard {
    @apply px-4 py-4;
  }

  .ink-hero,
  .ink-growth-suite,
  .ink-risk-suite,
  .ink-quote-strip,
  .ink-metric-card,
  .ink-panel,
  .ink-chart-card {
    @apply rounded-2xl p-4;
  }

  .ink-refresh-btn {
    @apply static self-start mb-4;
  }

  .ink-revenue-amount {
    @apply text-3xl;
  }

  .ink-hero-metrics {
    @apply flex-col gap-0;
  }

  .ink-metric-divider {
    @apply w-16 h-px;
  }

  .ink-metric-pill {
    @apply py-2;
  }

  .ink-chart-summary {
    @apply grid-cols-2;
  }

  .ink-suite-toolbar {
    @apply pb-4;
  }

  .ink-metric-value {
    @apply text-2xl;
  }

  .ink-chart,
  .ink-chart-medium,
  .ink-chart-large {
    height: 280px;
  }
}
</style>
