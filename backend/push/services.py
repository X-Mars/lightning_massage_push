import json
import requests
import logging
import jinja2
from jinja2 import Template as JinjaTemplate

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
