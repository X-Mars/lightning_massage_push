import json
import re
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse

from .models import Template, Robot, MessageLog, RobotType
from .serializers import (
    TemplateSerializer, RobotSerializer, MessageLogSerializer,
    MessagePushSerializer
)
from .services import MessagePushService


class TemplateViewSet(viewsets.ModelViewSet):
    """模板视图集"""
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Template.objects.filter(created_by=self.request.user)


class RobotViewSet(viewsets.ModelViewSet):
    """机器人视图集"""
    queryset = Robot.objects.all()
    serializer_class = RobotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Robot.objects.filter(created_by=self.request.user).order_by('-created_at')


class MessageLogViewSet(viewsets.ReadOnlyModelViewSet):
    """消息日志视图集"""
    queryset = MessageLog.objects.all()
    serializer_class = MessageLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MessageLog.objects.filter(created_by=self.request.user)


class MessagePushView(APIView):
    """消息推送视图"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = MessagePushSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            template = serializer.validated_data['template']
            robot = serializer.validated_data['robot']
            content_data = serializer.validated_data['content']
            test_mode = serializer.validated_data.get('test_mode', False)
            direct_content = serializer.validated_data.get('direct_content', '')
            
            # 测试模式
            if test_mode:
                success, error_msg = MessagePushService.test_robot(
                    robot=robot,
                    test_message=direct_content or content_data.get('content', '测试消息'),
                    user=request.user
                )
            else:
                # 正常推送模式
                success, error_msg = MessagePushService.push_message(
                    template=template,
                    robot=robot,
                    data=content_data,
                    user=request.user
                )
            
            if success:
                return Response({"message": "消息推送成功"}, status=status.HTTP_200_OK)
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PublicMessagePushView(APIView):
    """公开的消息推送API，无需认证"""
    permission_classes = []  # 不需要认证
    
    def post(self, request, template_id, robot_id):
        # 获取模板和机器人
        template = get_object_or_404(Template, pk=template_id)
        robot = get_object_or_404(Robot, pk=robot_id)
        
        # 确保模板和机器人类型匹配
        if template.robot_type != robot.robot_type:
            return Response(
                {"error": "模板与机器人类型不匹配"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 获取POST中的数据
            content_data = request.data
            
            # 推送消息，使用模板创建者作为操作用户
            success, error_msg = MessagePushService.push_message(
                template=template,
                robot=robot,
                data=content_data,
                user=template.created_by  # 使用模板创建者作为操作用户
            )
            
            if success:
                return Response({"message": "消息推送成功"}, status=status.HTTP_200_OK)
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TemplateDirectPushView(APIView):
    """通过模板直接发送消息的API，无需认证，前端可直接调用此API
    
    POST /api/templates/{template_id}/send/
    
    请求体示例:
    {
        "title": "消息标题",
        "content": "消息内容",
        ...根据模板中定义的变量传递
    }
    """
    permission_classes = []  # 不需要认证
    
    def post(self, request, template_id):
        """
        直接通过模板ID发送消息
        系统会自动选择匹配的机器人发送
        """
        # 获取模板
        template = get_object_or_404(Template, pk=template_id)
        
        try:
            # 获取POST中的数据
            content_data = request.data
            
            # 找到与模板类型匹配的机器人
            try:
                # 优先选择模板创建者的机器人
                robot = Robot.objects.filter(
                    robot_type=template.robot_type,
                    created_by=template.created_by
                ).first()
                
                # 如果没有找到，则选择任意匹配类型的机器人
                if not robot:
                    robot = Robot.objects.filter(
                        robot_type=template.robot_type
                    ).first()
                
                if not robot:
                    return Response(
                        {"error": f"未找到匹配的{template.get_robot_type_display()}类型机器人"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Exception as e:
                return Response(
                    {"error": f"查找匹配机器人失败: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 推送消息
            success, error_msg = MessagePushService.push_message(
                template=template,
                robot=robot,
                data=content_data,
                user=template.created_by  # 使用模板创建者作为操作用户
            )
            
            if success:
                return Response({"message": "消息推送成功"}, status=status.HTTP_200_OK)
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TemplateInfoView(APIView):
    """获取模板API信息的接口"""
    permission_classes = []  # 不需要认证
    
    def get(self, request, template_id):
        """获取模板信息，包括变量列表和示例JSON"""
        template = get_object_or_404(Template, pk=template_id)
        
        try:
            # 分析模板中的变量
            content = template.content
            variable_regex = r'\{\{\s*([a-zA-Z0-9_]+)\s*\}\}'
            variables = set(re.findall(variable_regex, content))
            
            # 创建示例JSON对象
            example_json = {}
            for var in variables:
                example_json[var] = f"示例{var}"
            
            # 查找匹配的机器人列表
            matching_robots = Robot.objects.filter(
                robot_type=template.robot_type
            ).values('id', 'name', 'english_name')
            
            # 构建机器人类型名称映射
            robot_type_names = {
                RobotType.WECHAT: "企业微信",
                RobotType.FEISHU: "飞书",
                RobotType.DINGTALK: "钉钉"
            }
            
            # 构建响应数据
            response_data = {
                'name': template.name,
                'robot_type': template.robot_type,
                'robot_type_name': robot_type_names.get(template.robot_type, "未知"),
                'variables': list(variables),
                'example_json': example_json,
                'matching_robots': list(matching_robots)
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response(
                {"error": f"获取模板信息失败: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


class PublicMessagePushByNameView(APIView):
    """通过机器人英文名称推送消息的API，无需认证
    
    POST /api/public/push/{template_id}/?robot_english_name=name
    
    请求体示例:
    {
        "title": "消息标题",
        "content": "消息内容",
        ...根据模板中定义的变量传递
    }
    """
    permission_classes = []  # 不需要认证
    
    def post(self, request, template_id):
        # 获取robot_english_name参数
        robot_english_name = request.query_params.get('robot_english_name')
        
        # 获取模板
        template = get_object_or_404(Template, pk=template_id)
        robot = None

        if robot_english_name:
            robots_by_name = Robot.objects.filter(english_name=robot_english_name)
            if robots_by_name.count() > 1:
                return Response(
                    {"error": f"存在多个英文名称为'{robot_english_name}'的机器人，请确保英文名称唯一"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif robots_by_name.count() == 1:
                robot = robots_by_name.first()
            # 如果 robots_by_name.count() == 0, robot 保持为 None, 会进入下面的 if not robot 逻辑

        if not robot: # 如果robot_english_name未提供，或提供了但未找到唯一机器人
            # 尝试查找默认机器人
            # 1. 优先查找模板创建者的默认机器人
            default_robots_by_creator = Robot.objects.filter(is_default=True, created_by=template.created_by)
            if default_robots_by_creator.exists():
                robot = default_robots_by_creator.first() # 如果找到多个，取第一个
            else:
                # 2. 如果模板创建者没有默认机器人，则查找全局默认机器人
                global_default_robots = Robot.objects.filter(is_default=True)
                if global_default_robots.exists():
                    robot = global_default_robots.first() # 如果找到多个，取第一个
                else:
                    # 未找到任何默认机器人
                    error_message = ""
                    if robot_english_name: #提供了robot_english_name但未找到，且无默认
                        error_message = f"机器人 '{robot_english_name}' 未找到，且未配置默认机器人。"
                    else: # 未提供robot_english_name，且无默认
                        error_message = "未提供机器人英文名称，且未找到默认机器人。请指定机器人或设置一个默认机器人。"
                    return Response(
                        {"error": error_message},
                        status=status.HTTP_404_NOT_FOUND
                    )
        
        # 此时，如果robot仍然是None，说明逻辑有误，或者确实没有任何可用的机器人
        if not robot:
            # 这是一个备用检查，理论上不应该到达这里，因为前面的逻辑会处理所有情况
            return Response({"error": "无法确定用于发送消息的机器人。"}, status=status.HTTP_400_BAD_REQUEST)

        # 确保模板和机器人类型匹配
        if template.robot_type != robot.robot_type:
            return Response(
                {"error": f"模板类型({template.get_robot_type_display()})与机器人类型({robot.get_robot_type_display()})不匹配"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 获取POST中的数据
            content_data = request.data
            
            # 推送消息，使用模板创建者作为操作用户
            success, error_msg = MessagePushService.push_message(
                template=template,
                robot=robot,
                data=content_data,
                user=template.created_by  # 使用模板创建者作为操作用户
            )
            
            if success:
                return Response({"message": "消息推送成功"}, status=status.HTTP_200_OK)
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({"error": f"消息推送失败: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
