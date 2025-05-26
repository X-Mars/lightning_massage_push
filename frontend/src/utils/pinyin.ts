/**
 * 汉字转拼音工具函数
 */
import pinyin from 'pinyin';

/**
 * 判断是否包含中文
 * @param str 要检测的字符串
 * @returns 是否包含中文
 */
export function hasChinese(str: string): boolean {
  return /[\u4e00-\u9fa5]/.test(str);
}

/**
 * 将中文转换成拼音 (驼峰命名法)
 * @param str 包含中文的字符串
 * @returns 拼音字符串，使用驼峰命名法
 */
export function toPinyin(str: string): string {
  // 对空字符串进行处理
  if (!str) {
    return '';
  }

  // 去除字符串中的空格
  const trimmedStr = str.replace(/\s+/g, '');
  
  // 如果去空格后为空字符串
  if (!trimmedStr) {
    return '';
  }

  // 如果不包含中文，则直接返回去空格后的原字符串
  if (!hasChinese(trimmedStr)) {
    return trimmedStr;
  }

  // 将中文转换为拼音，不带声调
  const pinyinArray = pinyin(trimmedStr, {
    style: pinyin.STYLE_NORMAL, // 不带声调
    heteronym: false // 不启用多音字模式
  });
  
  // 将拼音数组转换为驼峰命名法格式
  return pinyinArray
    .map((item, index) => {
      // 首字母小写，其余首字母大写
      const word = item[0].toLowerCase();
      return index === 0 ? word : word.charAt(0).toUpperCase() + word.slice(1);
    })
    .join('');
}
