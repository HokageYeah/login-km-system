<template>
  <button 
    class="base-button"
    :class="[`btn-${type || 'primary'}`, `btn-${size || 'md'}`]"
    @click="$emit('click')"
  >
    <slot></slot>
  </button>
</template>

<script setup lang="ts">
defineProps<{
  type?: 'primary' | 'success' | 'danger'
  size?: 'sm' | 'md' | 'lg'
}>()

defineEmits<{
  (e: 'click'): void
}>()
</script>

<style scoped>
.base-button {
  @reference "../styles/index.css";
  @apply px-4 py-2 rounded-lg font-medium transition-all duration-300;
  @apply hover:scale-105 active:scale-95;
}

.btn-primary {
  @apply bg-blue-500 text-white hover:bg-blue-600;
}

.btn-success {
  @apply bg-green-500 text-white hover:bg-green-600;
}

.btn-danger {
  @apply bg-red-500 text-white hover:bg-red-600;
}

.btn-sm { @apply px-3 py-1 text-sm; }
.btn-md { @apply px-4 py-2; }
.btn-lg { @apply px-6 py-3 text-lg; }
</style>
