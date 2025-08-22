<template>
  <div v-if="showEnvTag" class="env-tag" :class="envClass">
    <el-tag :type="tagType" size="small">
      {{ envDisplayName }}
    </el-tag>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { EnvConfig } from '../utils/envConfig';

defineOptions({
  name: 'EnvTag'
});

const showEnvTag = computed(() => EnvConfig.showEnvTag);
const envDisplayName = computed(() => EnvConfig.envDisplayName);

const tagType = computed(() => {
  switch (EnvConfig.envName) {
    case 'development':
      return 'info';
    case 'test':
      return 'warning';
    case 'staging':
      return 'danger';
    case 'production':
      return 'success';
    default:
      return 'info';
  }
});

const envClass = computed(() => {
  return `env-${EnvConfig.envName}`;
});
</script>

<style scoped>
.env-tag {
  position: fixed;
  top: 10px;
  right: 10px;
  z-index: 9999;
  opacity: 0.8;
  transition: opacity 0.3s;
}

.env-tag:hover {
  opacity: 1;
}

.env-development .el-tag {
  background-color: #909399;
  border-color: #909399;
  color: white;
}

.env-test .el-tag {
  background-color: #e6a23c;
  border-color: #e6a23c;
  color: white;
}

.env-staging .el-tag {
  background-color: #f56c6c;
  border-color: #f56c6c;
  color: white;
}

.env-production .el-tag {
  background-color: #67c23a;
  border-color: #67c23a;
  color: white;
}
</style>
