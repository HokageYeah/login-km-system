<template>
  <div class="error-container">
    <BaseCard title="403 Forbidden">
      <div class="error-content">
        <h1>403</h1>
        <p>抱歉，您没有权限访问该页面。</p>
        <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
      </div>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import BaseCard from '@/components/BaseCard.vue'
</script>

<style scoped>
/* 错误页（Brutalism 改版）：超大号 403 数字 + 黄色荧光衬底 */
.error-container {
  @reference "../../styles/index.css";
  @apply flex justify-center items-center h-full;
  background: var(--paper);
}
.error-content {
  @apply text-center py-10;
}
.error-content h1 {
  @apply text-7xl mb-4;
  font-weight: 900;
  color: var(--ink);
  background: linear-gradient(to top, var(--accent) 30%, transparent 30%);
  display: inline-block;
  padding: 0 0.15em;
  line-height: 1.1;
}
.error-content p {
  @apply mb-8 font-semibold;
  color: var(--ink-soft);
}
</style>
