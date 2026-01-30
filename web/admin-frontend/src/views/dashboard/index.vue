<template>
  <div class="dashboard-container">
    <BaseCard title="仪表盘">
      <p>这里是仪表盘页面，后续将展示统计图表。</p>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import BaseCard from '@/components/BaseCard.vue'
</script>

<style scoped>
.dashboard-container {
  @reference "../../styles/index.css";
  @apply w-full h-full;
}
</style>
