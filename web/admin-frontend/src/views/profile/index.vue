<template>
  <div class="profile-container">
    <BaseCard title="个人中心">
      <p>这里是个人中心页面。</p>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import BaseCard from '@/components/BaseCard.vue'
</script>

<style scoped>
.profile-container {
  @reference "../../styles/index.css";
  @apply w-full h-full;
}
</style>
