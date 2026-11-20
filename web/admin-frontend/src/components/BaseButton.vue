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
/*
 * 通用按钮（Brutalism 改版）：
 * 黑底白字主按钮 / 语义色按钮，全部直角 + 2px 黑框 + 硬阴影按压感。
 * 悬停位移 -1px 并放大阴影，替代原缩放动效（缩放会引起布局抖动）。
 */
.base-button {
  @reference "../styles/index.css";
  @apply px-4 py-2 font-bold cursor-pointer;
  border: 2px solid var(--ink);
  box-shadow: var(--shadow-brutal-sm);
  transition: transform 0.15s cubic-bezier(0.2, 0, 0, 1),
    box-shadow 0.15s cubic-bezier(0.2, 0, 0, 1),
    background-color 0.15s;
}

.base-button:hover {
  transform: translate(-1px, -1px);
  box-shadow: 4px 4px 0 var(--ink);
}

.base-button:active {
  transform: translate(1px, 1px);
  box-shadow: 1px 1px 0 var(--ink);
}

/* 主按钮：黑底暖白字，hover 反转黄底黑字 */
.btn-primary {
  background: var(--ink);
  color: var(--paper);
}
.btn-primary:hover {
  background: var(--accent);
  color: var(--ink);
}

.btn-success {
  background: #1a7f37;
  color: #fffdf6;
}
.btn-success:hover {
  background: #156029;
}

.btn-danger {
  background: var(--danger);
  color: #fffdf6;
}
.btn-danger:hover {
  background: #c73a3f;
}

.btn-sm { @apply px-3 py-1 text-sm; }
.btn-md { @apply px-4 py-2; }
.btn-lg { @apply px-6 py-3 text-lg; }
</style>
