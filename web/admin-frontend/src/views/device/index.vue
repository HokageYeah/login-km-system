<template>
  <div class="device-container">
    <BaseCard title="设备管理">
      <p>这里是设备管理页面。</p>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import BaseCard from '@/components/BaseCard.vue'
</script>

<style scoped>
.device-container {
  @reference "../../styles/index.css";
  @apply w-full h-full;
}
</style>
