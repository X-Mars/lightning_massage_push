import json
import requests
import logging
import jinja2
from jinja2 import Template as JinjaTemplate
from django.utils import timezone

from .models import RobotType, MessageLog

logger = logging.getLogger(__name__)


class MessagePushService:
    """消息推送服务"""
    
    @staticmethod
    def format_message(template_content, data):
        """使用jinja2格式化消息"""
        try:
            jinja_template = JinjaTemplate(template_content)
            formatted_content = jinja_template.render(**data)
            return formatted_content, None
        except jinja2.exceptions.TemplateError as e:
            logger.error(f"Template rendering error: {str(e)}")
            return None, str(e)
        except Exception as e:
            logger.error(f"Unknown error in format_message: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def push_wechat_message(webhook_url, content):
        """推送消息到企业微信机器人"""
        try:
            headers = {'Content-Type': 'application/json'}
            # 企业微信机器人消息格式
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "content": content
                }
            }
            response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()
            if result.get('errcode') == 0:
                return True, None
            return False, result.get('errmsg')
        except requests.RequestException as e:
            logger.error(f"Wechat push error: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def push_feishu_message(webhook_url, content):
        """推送消息到飞书机器人"""
        try:
            headers = {'Content-Type': 'application/json'}
            # 飞书机器人消息格式 - interactive 类型
            payload = {
                "msg_type": "interactive",
                "card": {
                    "config": {
                        "wide_screen_mode": True
                    },
                    "elements": [
                        {
                            "tag": "markdown",
                            "content": content
                        }
                    ]
                }
            }
            response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()
            if result.get('StatusCode') == 0:
                return True, None
            return False, result.get('StatusMessage')
        except requests.RequestException as e:
            logger.error(f"Feishu push error: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def push_dingtalk_message(webhook_url, content):
        """推送消息到钉钉机器人"""
        try:
            headers = {'Content-Type': 'application/json'}
            # 钉钉机器人消息格式
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "title": "消息通知",
                    "text": content
                }
            }
            response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()
            if result.get('errcode') == 0:
                return True, None
            return False, result.get('errmsg')
        except requests.RequestException as e:
            logger.error(f"Dingtalk push error: {str(e)}")
            return False, str(e)
    
    @classmethod
    def push_message(cls, template, robot, data, user=None):
        """推送消息主方法"""
        # 创建消息日志
        message_log = MessageLog.objects.create(
            template=template,
            robot=robot,
            content=json.dumps(data),
            raw_data=json.dumps(data),
            created_by=user
        )
        
        # 格式化消息内容
        formatted_content, error = cls.format_message(template.content, data)
        if error:
            message_log.status = False
            message_log.error_message = f"模板格式化错误: {error}"
            message_log.save()
            return False, error
        
        # 根据机器人类型推送消息
        message_log.formatted_content = formatted_content
        success = False
        error_msg = None
        
        if robot.robot_type == RobotType.WECHAT:
            success, error_msg = cls.push_wechat_message(robot.webhook_url, formatted_content)
        elif robot.robot_type == RobotType.FEISHU:
            success, error_msg = cls.push_feishu_message(robot.webhook_url, formatted_content)
        elif robot.robot_type == RobotType.DINGTALK:
            success, error_msg = cls.push_dingtalk_message(robot.webhook_url, formatted_content)
        else:
            error_msg = f"不支持的机器人类型: {robot.robot_type}"
        
        # 更新消息日志
        message_log.status = success
        if not success and error_msg:
            message_log.error_message = error_msg
        message_log.save()
        
        return success, error_msg
    
    @classmethod
    def test_robot(cls, robot, test_message, user=None):
        """测试机器人接口"""
        # 创建消息日志
        message_log = MessageLog.objects.create(
            robot=robot,
            raw_data=json.dumps({"test_message": test_message}),
            formatted_content=test_message,
            created_by=user
        )
        
        # 根据机器人类型推送消息
        success = False
        error_msg = None
        
        if robot.robot_type == RobotType.WECHAT:
            success, error_msg = cls.push_wechat_message(robot.webhook_url, test_message)
        elif robot.robot_type == RobotType.FEISHU:
            success, error_msg = cls.push_feishu_message(robot.webhook_url, test_message)
        elif robot.robot_type == RobotType.DINGTALK:
            success, error_msg = cls.push_dingtalk_message(robot.webhook_url, test_message)
        else:
            error_msg = f"不支持的机器人类型: {robot.robot_type}"
        
        # 更新消息日志
        message_log.status = success
        if not success and error_msg:
            message_log.error_message = error_msg
        message_log.save()
        
        return success, error_msg


class DistributionService:
    """分发服务"""
    
    @classmethod
    def extract_json_values(cls, data, path):
        """从JSON数据中提取值"""
        try:
            # 解析JSON数据
            if isinstance(data, str):
                # 尝试处理可能的转义字符问题
                try:
                    json_data = json.loads(data)
                except json.JSONDecodeError as e:
                    # 如果解析失败，尝试先进行一次反转义
                    try:
                        # 尝试解码可能被双重转义的字符串
                        decoded_data = data.encode().decode('unicode_escape')
                        json_data = json.loads(decoded_data)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # 如果还是失败，尝试替换常见的转义字符
                        cleaned_data = data.replace('\\.', '.')
                        json_data = json.loads(cleaned_data)
            else:
                json_data = data
            
            results = set()
            
            # 支持数组语法的路径解析，如 alerts[].labels.instance
            if '[].' in path:
                # 解析数组路径
                parts = path.split('[].')
                if len(parts) == 2:
                    array_path = parts[0]  # alerts
                    field_path = parts[1]  # labels.instance
                    
                    # 获取数组
                    current = json_data
                    for key in array_path.split('.'):
                        if isinstance(current, dict) and key in current:
                            current = current[key]
                        else:
                            return []
                    
                    # 遍历数组元素
                    if isinstance(current, list):
                        for item in current:
                            # 在每个数组元素中查找字段
                            field_value = cls._extract_field_from_object(item, field_path)
                            if field_value is not None:
                                results.add(str(field_value))
            else:
                # 简单的路径解析（不含数组）
                field_value = cls._extract_field_from_object(json_data, path)
                if field_value is not None:
                    if isinstance(field_value, list):
                        results.update(str(item) for item in field_value)
                    else:
                        results.add(str(field_value))
            
            return list(results)
        except Exception as e:
            logger.error(f"JSON extraction error: {str(e)}")
            return []
    
    @staticmethod
    def _extract_field_from_object(obj, field_path):
        """从对象中提取字段值"""
        try:
            current = obj
            for key in field_path.split('.'):
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return None
            return current
        except Exception:
            return None
    
    @staticmethod
    def extract_string_values(data, pattern):
        """从字符串中提取值"""
        import re
        try:
            # 查找所有 {{variable}} 模式
            variables = re.findall(r'\{\{(\w+)\}\}', pattern)
            results = []
            
            for var in variables:
                # 构建正则表达式来提取值
                regex_pattern = pattern.replace(f'{{{{{var}}}}}', r'([^\s]+)')
                matches = re.findall(regex_pattern, data)
                results.extend(matches)
            
            return list(set(results))  # 去重
        except Exception as e:
            logger.error(f"String extraction error: {str(e)}")
            return []
    
    @classmethod
    def process_alert_data(cls, rule, raw_data):
        """处理告警数据，提取实例信息"""
        try:
            if rule.type == 'json':
                extracted_values = cls.extract_json_values(raw_data, rule.extract_path)
            else:  # string
                extracted_values = cls.extract_string_values(raw_data, rule.extract_pattern)
            
            # 更新或创建实例映射
            from .models import InstanceMapping
            from django.utils import timezone
            
            for value in extracted_values:
                instance, created = InstanceMapping.objects.get_or_create(
                    instance_name=value,
                    defaults={
                        'source_rule': rule,
                        'alert_count': 0
                    }
                )
                
                # 更新告警统计
                instance.alert_count += 1
                instance.last_alert_time = timezone.now()
                if not instance.source_rule:
                    instance.source_rule = rule
                instance.save()
                
                # 创建告警记录
                from .models import AlertRecord
                AlertRecord.objects.create(
                    instance_mapping=instance,
                    rule_name=rule.name,
                    alert_content=raw_data[:1000],  # 限制长度
                    raw_data=raw_data,
                    extracted_values=extracted_values
                )
            
            return extracted_values
        except Exception as e:
            logger.error(f"Alert processing error: {str(e)}")
            return []
    
    @classmethod
    def test_rule(cls, rule_type, extract_path, extract_pattern, test_data):
        """测试分发规则"""
        try:
            if rule_type == 'json':
                return cls.extract_json_values(test_data, extract_path)
            else:  # string
                return cls.extract_string_values(test_data, extract_pattern)
        except Exception as e:
            logger.error(f"Rule test error: {str(e)}")
            return []
