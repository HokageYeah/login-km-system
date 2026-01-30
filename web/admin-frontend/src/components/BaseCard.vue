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
.base-card {
  @reference "../styles/index.css";
  @apply bg-white rounded-xl shadow-md hover:shadow-lg p-6 transition-all duration-300;
}

.card-header {
  @apply flex justify-between items-center mb-4 pb-4 border-b border-gray-200;
}

.card-title {
  @apply text-lg font-semibold text-gray-800;
}
</style>
