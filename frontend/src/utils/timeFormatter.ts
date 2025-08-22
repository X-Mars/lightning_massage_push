/**
 * 时间格式化工具
 * 用于将UTC时间转换为本地时区时间
 */

/**
 * 格式化时间为本地时区时间
 * @param utcTimeString UTC时间字符串
 * @returns 本地时区时间字符串
 */
export const formatToLocalTime = (utcTimeString: string | null | undefined): string => {
  if (!utcTimeString) {
    return '-';
  }

  try {
    // 如果时间字符串已经包含时区信息，直接使用
    // 否则假设是UTC时间
    let date: Date;
    
    if (utcTimeString.includes('Z') || utcTimeString.includes('+') || utcTimeString.includes('T')) {
      // 包含时区信息或ISO格式
      date = new Date(utcTimeString);
    } else {
      // 假设是UTC时间，添加UTC标识
      date = new Date(utcTimeString + ' UTC');
    }
    
    // 检查日期是否有效
    if (isNaN(date.getTime())) {
      console.warn('无效的时间格式:', utcTimeString);
      return utcTimeString;
    }
    
    // 转换为本地时间字符串
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
  } catch (error) {
    console.error('时间格式化错误:', error, '原始时间:', utcTimeString);
    return utcTimeString || '-';
  }
};

/**
 * 格式化时间为本地时区时间（不包含秒）
 * @param utcTimeString UTC时间字符串
 * @returns 本地时区时间字符串（不包含秒）
 */
export const formatToLocalTimeShort = (utcTimeString: string | null | undefined): string => {
  if (!utcTimeString) {
    return '-';
  }

  try {
    let date: Date;
    
    if (utcTimeString.includes('Z') || utcTimeString.includes('+') || utcTimeString.includes('T')) {
      date = new Date(utcTimeString);
    } else {
      date = new Date(utcTimeString + ' UTC');
    }
    
    if (isNaN(date.getTime())) {
      console.warn('无效的时间格式:', utcTimeString);
      return utcTimeString;
    }
    
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  } catch (error) {
    console.error('时间格式化错误:', error, '原始时间:', utcTimeString);
    return utcTimeString || '-';
  }
};

/**
 * 格式化时间为相对时间（如：刚刚、5分钟前、2小时前等）
 * @param utcTimeString UTC时间字符串
 * @returns 相对时间字符串
 */
export const formatToRelativeTime = (utcTimeString: string | null | undefined): string => {
  if (!utcTimeString) {
    return '-';
  }

  try {
    let date: Date;
    
    if (utcTimeString.includes('Z') || utcTimeString.includes('+') || utcTimeString.includes('T')) {
      date = new Date(utcTimeString);
    } else {
      date = new Date(utcTimeString + ' UTC');
    }
    
    if (isNaN(date.getTime())) {
      return utcTimeString;
    }
    
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSeconds = Math.floor(diffMs / 1000);
    const diffMinutes = Math.floor(diffSeconds / 60);
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffSeconds < 60) {
      return '刚刚';
    } else if (diffMinutes < 60) {
      return `${diffMinutes}分钟前`;
    } else if (diffHours < 24) {
      return `${diffHours}小时前`;
    } else if (diffDays < 7) {
      return `${diffDays}天前`;
    } else {
      // 超过一周显示具体日期
      return formatToLocalTimeShort(utcTimeString);
    }
  } catch (error) {
    console.error('相对时间格式化错误:', error, '原始时间:', utcTimeString);
    return utcTimeString || '-';
  }
};

/**
 * 格式化日期为本地时区日期（只显示日期部分）
 * @param utcTimeString UTC时间字符串
 * @returns 本地时区日期字符串
 */
export const formatToLocalDate = (utcTimeString: string | null | undefined): string => {
  if (!utcTimeString) {
    return '-';
  }

  try {
    let date: Date;
    
    if (utcTimeString.includes('Z') || utcTimeString.includes('+') || utcTimeString.includes('T')) {
      date = new Date(utcTimeString);
    } else {
      date = new Date(utcTimeString + ' UTC');
    }
    
    if (isNaN(date.getTime())) {
      console.warn('无效的时间格式:', utcTimeString);
      return utcTimeString;
    }
    
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
  } catch (error) {
    console.error('日期格式化错误:', error, '原始时间:', utcTimeString);
    return utcTimeString || '-';
  }
};
