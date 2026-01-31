<template>
  <router-view v-slot="{ Component, route }">
    <transition name="fade-transform" mode="out-in">
      <component :is="Component" :key="route.path" />
    </transition>
  </router-view>
</template>

<script setup lang="ts">
/**
 * 路由包装器组件
 * @description 用于渲染二级路由，为有子路由的一级路由提供 router-view
 * 当路由配置了 children 时，使用此组件作为父组件，以支持子路由的渲染
 */
</script>

<style scoped>
/* 页面切换动画 */
.fade-transform-leave-active,
.fade-transform-enter-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-10px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(10px);
}
</style>
