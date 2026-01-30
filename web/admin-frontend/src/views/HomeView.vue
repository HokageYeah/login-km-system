<template>
  <div class="p-10 bg-gray-100 min-h-screen">
    <BaseCard title="System Ready">
      <template #extra>
        <span class="text-sm text-gray-500">Phase 1 Complete</span>
      </template>
      <div class="space-y-4">
        <p class="text-gray-700">
          Vue 3 + TypeScript + Vite + Tailwind CSS + Element Plus + Pinia + Vue Router
        </p>
        <div class="flex gap-4">
          <BaseButton type="primary">Primary</BaseButton>
          <BaseButton type="success">Success</BaseButton>
          <BaseButton type="danger">Danger</BaseButton>
        </div>
        <div class="mt-4">
            <el-button type="primary">Element Plus Button</el-button>
        </div>
      </div>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import BaseCard from '@/components/BaseCard.vue'
import BaseButton from '@/components/BaseButton.vue'
</script>
