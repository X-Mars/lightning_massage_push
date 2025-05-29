#!/usr/bin/env python
"""
测试多机器人分发功能
"""
import os
import sys
import django

# 设置Django环境
sys.path.append('/Users/mars/vscode/test/message-push-system/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messagepush.settings')
django.setup()

from push.models import Template, Robot, InstanceMapping, DistributionRule
from push.services import DistributionService, MessagePushService
from django.contrib.auth.models import User

def test_multi_robot_distribution():
    """测试多机器人分发功能"""
    print("🧪 开始测试多机器人分发功能...")
    
    # 1. 创建测试用户
    user, _ = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com', 'password': 'test123'}
    )
    print("✅ 创建测试用户")
    
    # 2. 创建测试机器人
    robot1, _ = Robot.objects.get_or_create(
        name='测试微信机器人',
        defaults={
            'robot_type': 'wechat',
            'webhook_url': 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test1',
            'created_by': user
        }
    )
    
    robot2, _ = Robot.objects.get_or_create(
        name='测试飞书机器人',
        defaults={
            'robot_type': 'feishu',
            'webhook_url': 'https://open.feishu.cn/open-apis/bot/v2/hook/test2',
            'created_by': user
        }
    )
    
    robot3, _ = Robot.objects.get_or_create(
        name='测试微信机器人2',
        defaults={
            'robot_type': 'wechat',
            'webhook_url': 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test3',
            'created_by': user
        }
    )
    print("✅ 创建测试机器人")
    
    # 3. 创建测试模板
    template, _ = Template.objects.get_or_create(
        name='多机器人测试模板',
        defaults={
            'robot_type': 'wechat',
            'content': '告警：{{instance_name}} - {{rule_name}}\n内容：{{content}}',
            'created_by': user
        }
    )
    print("✅ 创建测试模板")
    
    # 4. 创建测试规则
    rule, _ = DistributionRule.objects.get_or_create(
        name='JSON实例提取',
        defaults={
            'type': 'json',
            'extract_path': 'alerts[].labels.instance',
            'description': '从告警数据中提取实例名称',
            'is_active': True
        }
    )
    print("✅ 创建测试规则")
    
    # 5. 创建实例映射，配置多个机器人
    instance1, _ = InstanceMapping.objects.get_or_create(
        instance_name='server-001',
        defaults={'source_rule': rule, 'alert_count': 0}
    )
    
    instance2, _ = InstanceMapping.objects.get_or_create(
        instance_name='server-002',
        defaults={'source_rule': rule, 'alert_count': 0}
    )
    
    # 为实例1配置两个微信机器人
    instance1.robots.set([robot1, robot3])
    
    # 为实例2配置一个微信机器人和一个飞书机器人（飞书机器人类型不匹配，应该被跳过）
    instance2.robots.set([robot1, robot2])
    
    print("✅ 配置实例映射")
    print(f"   实例1 ({instance1.instance_name}) -> {instance1.robot_count} 个机器人")
    print(f"   实例2 ({instance2.instance_name}) -> {instance2.robot_count} 个机器人")
    
    # 6. 测试分发推送
    print("\n🚀 开始测试分发推送...")
    
    # 模拟告警数据
    test_alert_data = {
        "alerts": [
            {
                "status": "firing",
                "labels": {
                    "alertname": "HighCPUUsage",
                    "instance": "server-001",
                    "severity": "critical"
                },
                "annotations": {
                    "description": "CPU使用率过高"
                }
            },
            {
                "status": "firing", 
                "labels": {
                    "alertname": "DiskSpaceLow",
                    "instance": "server-002",
                    "severity": "warning"
                },
                "annotations": {
                    "description": "磁盘空间不足"
                }
            }
        ],
        "content": "系统告警通知"
    }
    
    print(f"📤 发送测试告警数据...")
    print(f"   告警实例: server-001, server-002")
    print(f"   模板类型: {template.robot_type}")
    print(f"   预期结果: server-001 -> 2个推送, server-002 -> 1个推送(飞书机器人被跳过)")
    
    # 处理告警数据并提取实例
    import json
    raw_data = json.dumps(test_alert_data)
    extracted_values = DistributionService.process_alert_data(rule, raw_data)
    print(f"   提取的实例: {extracted_values}")
    
    # 模拟分发推送逻辑
    success_count = 0
    error_count = 0
    results = []
    
    for instance_name in extracted_values:
        try:
            instance_mapping = InstanceMapping.objects.get(instance_name=instance_name)
            
            # 获取实例配置的所有匹配类型的机器人
            robots = instance_mapping.robots.filter(robot_type=template.robot_type)
            
            if robots.exists():
                print(f"   实例 {instance_name}: 找到 {robots.count()} 个匹配的机器人")
                
                # 向所有匹配类型的机器人推送消息
                for robot in robots:
                    enhanced_data = test_alert_data.copy()
                    enhanced_data['instance_name'] = instance_name
                    enhanced_data['rule_name'] = rule.name
                    
                    print(f"     -> 推送到机器人: {robot.name} ({robot.robot_type})")
                    
                    # 这里我们不实际发送消息，只模拟成功
                    success = True
                    if success:
                        success_count += 1
                        results.append({
                            'instance': instance_name,
                            'robot': robot.name,
                            'status': 'success'
                        })
                        print(f"        ✅ 推送成功")
                    else:
                        error_count += 1
                        results.append({
                            'instance': instance_name,
                            'robot': robot.name,
                            'status': 'error',
                            'error': 'Push failed'
                        })
                        print(f"        ❌ 推送失败")
            else:
                # 检查是否有配置机器人但类型不匹配的情况
                all_robots = instance_mapping.robots.all()
                if all_robots.exists():
                    print(f"   实例 {instance_name}: 有 {all_robots.count()} 个机器人但类型不匹配")
                    for robot in all_robots:
                        error_count += 1
                        results.append({
                            'instance': instance_name,
                            'robot': robot.name,
                            'status': 'error',
                            'error': f'模板类型({template.robot_type})与机器人类型({robot.robot_type})不匹配'
                        })
                        print(f"     -> 机器人 {robot.name} ({robot.robot_type}): ❌ 类型不匹配")
                else:
                    print(f"   实例 {instance_name}: 未配置机器人")
                    results.append({
                        'instance': instance_name,
                        'robot': None,
                        'status': 'skipped',
                        'error': '实例未配置机器人'
                    })
                    
        except InstanceMapping.DoesNotExist:
            print(f"   实例 {instance_name}: 映射不存在")
            results.append({
                'instance': instance_name,
                'robot': None,
                'status': 'skipped',
                'error': '实例映射不存在'
            })
    
    print(f"\n📊 测试结果统计:")
    print(f"   成功推送: {success_count}")
    print(f"   失败推送: {error_count}")
    print(f"   处理实例: {len(set(extracted_values))}")
    
    print(f"\n📋 详细结果:")
    for result in results:
        status_icon = "✅" if result['status'] == 'success' else "❌" if result['status'] == 'error' else "⏭️"
        robot_info = result['robot'] if result['robot'] else "无"
        error_info = f" ({result.get('error', '')})" if result.get('error') else ""
        print(f"   {status_icon} {result['instance']} -> {robot_info}{error_info}")
    
    # 清理测试数据
    print(f"\n🧹 清理测试数据...")
    InstanceMapping.objects.filter(instance_name__in=['server-001', 'server-002']).delete()
    Template.objects.filter(name='多机器人测试模板').delete()
    Robot.objects.filter(name__in=['测试微信机器人', '测试飞书机器人', '测试微信机器人2']).delete()
    DistributionRule.objects.filter(name='JSON实例提取').delete()
    User.objects.filter(username='test_user').delete()
    print("✅ 清理完成")
    
    print(f"\n🎉 多机器人分发功能测试完成!")
    return success_count > 0

if __name__ == '__main__':
    test_multi_robot_distribution()
