<template>
  <div class="user-container">
    <BaseCard title="用户管理">
      <p>这里是用户管理页面。</p>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import BaseCard from '@/components/BaseCard.vue'
</script>

<style scoped>
.user-container {
  @reference "../../styles/index.css";
  @apply w-full h-full;
}
</style>
