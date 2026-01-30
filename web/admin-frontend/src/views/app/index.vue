<template>
  <div class="app-container">
    <BaseCard title="应用管理">
      <p>这里是应用管理页面。</p>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import BaseCard from '@/components/BaseCard.vue'
</script>

<style scoped>
.app-container {
  @reference "../../styles/index.css";
  @apply w-full h-full;
}
</style>
