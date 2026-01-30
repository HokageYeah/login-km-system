<template>
  <div class="stat-card" :class="`stat-card-${type}`">
    <div class="stat-icon">
      <el-icon :size="28">
        <component :is="icon" />
      </el-icon>
    </div>
    <div class="stat-content">
      <div class="stat-label">{{ label }}</div>
      <div class="stat-value">{{ formatValue(value) }}</div>
      <div v-if="trend !== undefined" class="stat-trend" :class="`trend-${trend}`">
        <el-icon>
          <component :is="trend === 'up' ? 'ArrowUp' : 'ArrowDown'" />
        </el-icon>
        <span>{{ trendValue }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 统计卡片组件
 * @description 用于展示单个统计数据，支持趋势显示
 */
import { computed } from 'vue'
import type { Component } from 'vue'

/**
 * Props 接口定义
 */
interface Props {
  label: string        // 标签文本
  value: number       // 数值
  icon: Component     // 图标组件
  type?: 'primary' | 'success' | 'warning' | 'danger' | 'info'  // 卡片类型（影响颜色）
  trend?: 'up' | 'down'  // 趋势方向（可选）
  trendValue?: string // 趋势值（可选）
  suffix?: string    // 数值后缀（可选）
}

const props = withDefaults(defineProps<Props>(), {
  type: 'primary',
  suffix: ''
})

/**
 * 格式化数值
 * @description 根据数值大小自动格式化（千分位分隔）
 * @param num 要格式化的数值
 * @returns 格式化后的字符串
 */
const formatValue = (num: number) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toLocaleString() + props.suffix
}
</script>

<style scoped>
@reference "../../../styles/index.css";

.stat-card {
  @apply bg-white rounded-xl shadow-md hover:shadow-lg p-6;
  @apply transition-all duration-300 cursor-pointer;
  @apply border border-gray-100;
  @apply flex items-center gap-4;
  @apply transform hover:-translate-y-1;
}

/* 图标容器样式 */
.stat-icon {
  @apply w-14 h-14 rounded-full flex items-center justify-center;
  @apply transition-all duration-300;
}

/* 不同类型的图标颜色 */
.stat-card-primary .stat-icon {
  @apply bg-blue-50 text-blue-600;
}

.stat-card-success .stat-icon {
  @apply bg-green-50 text-green-600;
}

.stat-card-warning .stat-icon {
  @apply bg-yellow-50 text-yellow-600;
}

.stat-card-danger .stat-icon {
  @apply bg-red-50 text-red-600;
}

.stat-card-info .stat-icon {
  @apply bg-purple-50 text-purple-600;
}

/* 内容区域 */
.stat-content {
  @apply flex-1;
}

.stat-label {
  @apply text-sm text-gray-500 mb-1;
  @apply font-medium;
}

.stat-value {
  @apply text-2xl font-bold text-gray-900;
  @apply mb-1;
}

/* 趋势样式 */
.stat-trend {
  @apply flex items-center gap-1 text-sm font-medium;
  transition: color 0.2s ease;
}

.trend-up {
  @apply text-green-600;
}

.trend-down {
  @apply text-red-600;
}

/* 悬停效果 */
.stat-card:hover .stat-icon {
  @apply transform scale-110;
}
</style>
