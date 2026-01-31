<template>
  <div class="stats-container">
    <BaseCard title="仪表盘">
      <p>这里是仪表盘页面2。</p>
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
