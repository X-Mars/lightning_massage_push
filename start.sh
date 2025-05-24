#!/bin/bash

# 消息推送系统启动脚本

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_ROOT=$(pwd)
BACKEND_PATH="$PROJECT_ROOT/backend"
FRONTEND_PATH="$PROJECT_ROOT/frontend"

# 打印标题
echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}        消息推送系统启动脚本               ${NC}"
echo -e "${GREEN}=============================================${NC}"

# 检查虚拟环境是否存在
setup_backend() {
    echo -e "\n${YELLOW}[1/4] 配置后端环境...${NC}"
    
    if [ ! -d "$BACKEND_PATH/venv" ]; then
        echo "创建Python虚拟环境..."
        cd "$BACKEND_PATH" && python3 -m venv venv
    fi
    
    echo "激活虚拟环境并安装依赖..."
    cd "$BACKEND_PATH" && source venv/bin/activate && pip install -r requirements.txt
    
    echo "执行数据库迁移..."
    cd "$BACKEND_PATH" && source venv/bin/activate && python manage.py makemigrations && python manage.py migrate
    
    if [ ! -f "$BACKEND_PATH/db.sqlite3" ]; then
        echo "创建超级用户..."
        cd "$BACKEND_PATH" && source venv/bin/activate && python manage.py createsuperuser
    fi
    
    echo -e "${GREEN}后端环境配置完成!${NC}"
}

# 设置前端环境
setup_frontend() {
    echo -e "\n${YELLOW}[2/4] 配置前端环境...${NC}"
    cd "$FRONTEND_PATH" && npm install
    echo -e "${GREEN}前端环境配置完成!${NC}"
}

# 启动后端
start_backend() {
    echo -e "\n${YELLOW}[3/4] 启动后端服务...${NC}"
    cd "$BACKEND_PATH" && source venv/bin/activate && python manage.py runserver 0.0.0.0:8000 &
    BACKEND_PID=$!
    echo "后端服务已启动，访问地址: http://localhost:8000"
}

# 启动前端
start_frontend() {
    echo -e "\n${YELLOW}[4/4] 启动前端服务...${NC}"
    cd "$FRONTEND_PATH" && npm run dev &
    FRONTEND_PID=$!
    echo "前端服务已启动，等待构建完成后访问地址将显示在控制台"
}

# 清理函数
cleanup() {
    echo -e "\n${YELLOW}正在关闭服务...${NC}"
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID
    fi
    echo "服务已关闭"
    exit 0
}

# 捕获中断信号
trap cleanup SIGINT

# 主要流程
main() {
    setup_backend
    setup_frontend
    
    start_backend
    start_frontend
    
    echo -e "\n${GREEN}=============================================${NC}"
    echo -e "${GREEN}所有服务已启动!${NC}"
    echo -e "${GREEN}* 后端API: http://localhost:8000${NC}"
    echo -e "${GREEN}* 前端界面: 见上方控制台输出${NC}"
    echo -e "${GREEN}* 按CTRL+C停止所有服务${NC}"
    echo -e "${GREEN}=============================================${NC}"
    
    # 保持脚本运行
    while true; do
        sleep 1
    done
}

# 执行主函数
main
