<template>
  <section class="app-main">
    <router-view v-slot="{ Component, route }">
      <transition name="fade-transform" mode="out-in">
        <component :is="Component" :key="route.path" />
      </transition>
    </router-view>
  </section>
</template>

<script setup lang="ts">
/**
 * 主内容区域组件
 * @description 负责渲染路由视图，提供页面切换动画
 * 支持一级和二级路由，子路由需要在对应的父组件中添加 <router-view>
 */
</script>

<style scoped>
.app-main {
  @reference "../../styles/index.css";
  /* 减去topbar高度 (64px) */
  @apply w-full relative overflow-hidden bg-gray-50 p-6;
  min-height: calc(100vh - 64px);
}

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
