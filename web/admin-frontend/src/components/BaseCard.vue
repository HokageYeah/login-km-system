<template>
  <div class="base-card">
    <div v-if="title" class="card-header">
      <h3 class="card-title">{{ title }}</h3>
      <div class="card-extra">
        <slot name="extra"></slot>
      </div>
    </div>
    <div class="card-body">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title?: string
}>()
</script>

<style scoped>
/*
 * 通用卡片（Brutalism 改版）：
 * 暖白表面 + 2px 黑框 + 硬阴影，悬停位移放大阴影。
 */
.base-card {
  @reference "../styles/index.css";
  @apply p-6;
  background: var(--surface);
  border: 2px solid var(--ink);
  box-shadow: var(--shadow-brutal);
  transition: transform 0.15s cubic-bezier(0.2, 0, 0, 1),
    box-shadow 0.15s cubic-bezier(0.2, 0, 0, 1);
}

.base-card:hover {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0 var(--ink);
}

.card-header {
  @apply flex justify-between items-center mb-4 pb-4;
  border-bottom: 2px solid var(--ink);
}

.card-title {
  @apply text-lg;
  font-weight: 900;
  color: var(--ink);
}
</style>
