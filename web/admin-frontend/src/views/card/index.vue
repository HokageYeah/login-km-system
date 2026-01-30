<template>
  <div class="card-container">
    <BaseCard title="卡密管理">
      <p>这里是卡密管理页面。</p>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import BaseCard from '@/components/BaseCard.vue'
</script>

<style scoped>
.card-container {
  @reference "../../styles/index.css";
  @apply w-full h-full;
}
</style>
