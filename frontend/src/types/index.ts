// 用户类型
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
}

// 机器人类型枚举
export const RobotType = {
  WECHAT: 'wechat',
  FEISHU: 'feishu',
  DINGTALK: 'dingtalk'
} as const;

// 类型定义
export type RobotType = typeof RobotType[keyof typeof RobotType];

// 机器人类型名称映射
export const RobotTypeNames = {
  [RobotType.WECHAT]: '企业微信',
  [RobotType.FEISHU]: '飞书',
  [RobotType.DINGTALK]: '钉钉',
};

// 模板类型
export interface Template {
  id: number;
  name: string;
  description: string;
  content: string;
  robot_type: RobotType;
  created_by: User;
  created_at: string;
  updated_at: string;
}

// 机器人类型
export interface Robot {
  id: number;
  name: string;
  english_name?: string;
  webhook_url: string;
  robot_type: RobotType;
  is_default: boolean;
  description: string;
  created_by: User;
  created_at: string;
  updated_at: string;
}

// 消息日志类型
export interface MessageLog {
  id: number;
  template: number;
  template_name: string;
  robot: number;
  robot_name: string;
  content: string;
  raw_data: string;
  formatted_content: string;
  status: boolean;
  error_message: string;
  created_by: number;
  created_by_username: string;
  created_at: string;
}

// 分页类型
export interface Pagination {
  page: number;
  size: number;
  total: number;
}

// 推送消息参数
export interface PushMessageParams {
  template_id: number;
  robot_id: number;
  content: Record<string, any>;
}