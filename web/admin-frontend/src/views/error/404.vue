<template>
  <div class="error-container">
    <BaseCard title="404 Not Found">
      <div class="error-content">
        <h1>404</h1>
        <p>抱歉，您访问的页面不存在。</p>
        <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
      </div>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import BaseCard from '@/components/BaseCard.vue'
</script>

<style scoped>
.error-container {
  @reference "../../styles/index.css";
  @apply flex justify-center items-center h-full;
}
.error-content {
  @apply text-center py-10;
}
.error-content h1 {
  @apply text-6xl font-bold text-gray-800 mb-4;
}
.error-content p {
  @apply text-gray-600 mb-8;
}
</style>
