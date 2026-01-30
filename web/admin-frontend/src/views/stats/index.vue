<template>
  <div class="stats-container">
    <BaseCard title="统计数据">
      <p>这里是统计数据页面。</p>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import BaseCard from '@/components/BaseCard.vue'
</script>

<style scoped>
.stats-container {
  @reference "../../styles/index.css";
  @apply w-full h-full;
}
</style>
