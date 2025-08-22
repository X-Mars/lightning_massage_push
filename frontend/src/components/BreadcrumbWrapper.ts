// 面包屑组件的包装器
import { defineComponent, h } from 'vue';
import BreadcrumbComp from './Breadcrumb.vue';

export default defineComponent({
  name: 'BreadcrumbWrapper',
  setup() {
    return () => h(BreadcrumbComp);
  },
});
