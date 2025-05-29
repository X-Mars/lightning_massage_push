import json
import re
import logging
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse

from .models import Template, Robot, MessageLog, RobotType, DistributionRule, InstanceMapping, AlertRecord
from .serializers import (
    TemplateSerializer, RobotSerializer, MessageLogSerializer,
    MessagePushSerializer, DistributionRuleSerializer, InstanceMappingSerializer,
    AlertRecordSerializer, RuleTestSerializer
)
from .services import MessagePushService

logger = logging.getLogger(__name__)


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


class DistributionRuleViewSet(viewsets.ModelViewSet):
    """分发规则视图集"""
    queryset = DistributionRule.objects.all()
    serializer_class = DistributionRuleSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def test(self, request):
        """测试分发规则"""
        from .services import DistributionService
        
        serializer = RuleTestSerializer(data=request.data)
        if serializer.is_valid():
            rule_type = serializer.validated_data['type']
            extract_path = serializer.validated_data.get('extract_path', '')
            extract_pattern = serializer.validated_data.get('extract_pattern', '')
            test_data = serializer.validated_data['test_data']
            
            # 执行测试
            results = DistributionService.test_rule(
                rule_type, extract_path, extract_pattern, test_data
            )
            
            return Response({
                'extracted_values': results,
                'count': len(results)
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InstanceMappingViewSet(viewsets.ModelViewSet):
    """实例映射视图集"""
    queryset = InstanceMapping.objects.all()
    serializer_class = InstanceMappingSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def batch_configure(self, request):
        """批量配置实例映射"""
        instance_ids = request.data.get('instance_ids', [])
        robot_ids = request.data.get('robot_ids', [])
        
        if not instance_ids:
            return Response(
                {'error': '请提供实例ID列表'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not robot_ids:
            return Response(
                {'error': '请提供机器人ID列表'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 检查机器人是否存在
            robots = Robot.objects.filter(id__in=robot_ids)
            if robots.count() != len(robot_ids):
                return Response(
                    {'error': '部分机器人不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 获取实例
            instances = InstanceMapping.objects.filter(id__in=instance_ids)
            updated_count = 0
            
            for instance in instances:
                instance.robots.set(robot_ids)
                updated_count += 1
            
            return Response({
                'message': f'成功配置{updated_count}个实例',
                'updated_count': updated_count
            })
        except Exception as e:
            return Response(
                {'error': f'批量配置失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def batch_clear(self, request):
        """批量清除实例映射"""
        instance_ids = request.data.get('instance_ids', [])
        
        if not instance_ids:
            return Response(
                {'error': '请提供实例ID列表'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            instances = InstanceMapping.objects.filter(id__in=instance_ids)
            updated_count = 0
            
            for instance in instances:
                instance.robots.clear()
                updated_count += 1
            
            return Response({
                'message': f'成功清除{updated_count}个实例的配置',
                'updated_count': updated_count
            })
        except Exception as e:
            return Response(
                {'error': f'批量清除失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def alerts(self, request, pk=None):
        """获取实例的告警记录"""
        from .models import AlertRecord
        from .serializers import AlertRecordSerializer
        
        instance = self.get_object()
        alerts = AlertRecord.objects.filter(instance_mapping=instance).order_by('-alert_time')[:20]
        serializer = AlertRecordSerializer(alerts, many=True)
        return Response(serializer.data)


class DistributionAlertView(APIView):
    """分发告警视图"""
    permission_classes = []  # 不需要认证，用于接收外部告警
    
    def post(self, request):
        """处理告警数据"""
        from .models import DistributionRule
        from .services import DistributionService
        
        try:
            raw_data = request.body.decode('utf-8')
            
            # 获取所有启用的分发规则
            active_rules = DistributionRule.objects.filter(is_active=True)
            
            processed_instances = []
            for rule in active_rules:
                # 处理告警数据
                extracted_values = DistributionService.process_alert_data(rule, raw_data)
                if extracted_values:
                    processed_instances.extend(extracted_values)
            
            return Response({
                'message': '告警数据处理成功',
                'processed_instances': list(set(processed_instances)),
                'count': len(set(processed_instances))
            })
        except Exception as e:
            return Response(
                {'error': f'告警处理失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class RefreshInstancesView(APIView):
    """刷新实例数据视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """手动刷新实例数据"""
        # 这里可以添加定期任务或手动触发的实例数据更新逻辑
        try:
            # 可以添加更复杂的刷新逻辑，比如：
            # 1. 清理过期的实例数据
            # 2. 更新统计信息
            # 3. 触发重新扫描等
            
            return Response({
                'message': '实例数据刷新成功'
            })
        except Exception as e:
            return Response(
                {'error': f'刷新失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class DistributionPushView(APIView):
    """分发推送视图 - 根据告警数据自动分发到对应机器人
    
    POST /api/public/distribution/push/{template_id}/
    
    请求体示例:
    {
        "alerts": [
            {
                "labels": {
                    "instance": "dev-2",
                    "alertname": "ContainerAbsent"
                },
                "annotations": {
                    "description": "容器已停止"
                }
            }
        ]
    }
    """
    permission_classes = []  # 不需要认证，用于接收外部告警
    
    def post(self, request, template_id):
        """处理分发推送请求"""
        from .models import DistributionRule, InstanceMapping
        from .services import DistributionService, MessagePushService
        
        # 获取模板
        template = get_object_or_404(Template, pk=template_id)
        
        try:
            raw_data = json.dumps(request.data)
            content_data = request.data
            
            # 获取所有启用的分发规则
            active_rules = DistributionRule.objects.filter(is_active=True)
            
            processed_instances = []
            success_count = 0
            error_count = 0
            results = []
            
            for rule in active_rules:
                try:
                    # 处理告警数据，提取实例信息
                    extracted_values = DistributionService.process_alert_data(rule, raw_data)
                    
                    for instance_name in extracted_values:
                        # 查找实例映射
                        try:
                            instance_mapping = InstanceMapping.objects.get(
                                instance_name=instance_name
                            )
                            
                            # 获取实例配置的所有机器人
                            robots = instance_mapping.robots.filter(robot_type=template.robot_type)
                            
                            if robots.exists():
                                # 向所有匹配类型的机器人推送消息
                                for robot in robots:
                                    # 在消息数据中添加实例信息
                                    enhanced_data = content_data.copy()
                                    enhanced_data['instance_name'] = instance_name
                                    enhanced_data['rule_name'] = rule.name
                                    
                                    # 推送消息
                                    success, error_msg = MessagePushService.push_message(
                                        template=template,
                                        robot=robot,
                                        data=enhanced_data,
                                        user=template.created_by
                                    )
                                    
                                    if success:
                                        success_count += 1
                                        results.append({
                                            'instance': instance_name,
                                            'robot': robot.name,
                                            'status': 'success'
                                        })
                                    else:
                                        error_count += 1
                                        results.append({
                                            'instance': instance_name,
                                            'robot': robot.name,
                                            'status': 'error',
                                            'error': error_msg
                                        })
                            else:
                                # 检查是否有配置机器人但类型不匹配的情况
                                all_robots = instance_mapping.robots.all()
                                if all_robots.exists():
                                    # 有配置机器人但类型不匹配
                                    for robot in all_robots:
                                        error_count += 1
                                        results.append({
                                            'instance': instance_name,
                                            'robot': robot.name,
                                            'status': 'error',
                                            'error': f'模板类型({template.get_robot_type_display()})与机器人类型({robot.get_robot_type_display()})不匹配'
                                        })
                                else:
                                    # 实例没有配置任何机器人，记录但不推送
                                    results.append({
                                        'instance': instance_name,
                                        'robot': None,
                                        'status': 'skipped',
                                        'error': '实例未配置机器人'
                                    })
                                
                        except InstanceMapping.DoesNotExist:
                            # 实例映射不存在，记录但不推送
                            results.append({
                                'instance': instance_name,
                                'robot': None,
                                'status': 'skipped',
                                'error': '实例映射不存在'
                            })
                            
                        processed_instances.append(instance_name)
                        
                except Exception as e:
                    logger.error(f"处理规则 {rule.name} 时出错: {str(e)}")
                    continue
            
            return Response({
                'message': f'分发推送完成，成功: {success_count}, 失败: {error_count}',
                'success_count': success_count,
                'error_count': error_count,
                'processed_instances': list(set(processed_instances)),
                'total_instances': len(set(processed_instances)),
                'results': results
            })
            
        except Exception as e:
            logger.error(f"分发推送失败: {str(e)}")
            return Response(
                {'error': f'分发推送失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
