#!/usr/bin/env python3
# run.py - 应用启动脚本

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        sys.exit(1)
    else:
        print(f"✅ Python版本检查通过: {sys.version.split()[0]}")

def check_dependencies():
    """检查依赖包是否安装"""
    required_packages = [
        "streamlit",
        "openbb", 
        "akshare",
        "pandas",
        "numpy",
        "plotly",
        "textblob",
        "yfinance"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: 已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}: 未安装")
    
    if missing_packages:
        print(f"\n缺少依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def install_dependencies():
    """安装依赖包"""
    print("正在安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖包安装完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ 依赖包安装失败")
        return False

def setup_environment():
    """设置环境"""
    print("设置环境变量...")
    
    # 设置默认环境
    os.environ.setdefault("FLASK_ENV", "development")
    os.environ.setdefault("STREAMLIT_THEME_BASE", "light")
    
    print("✅ 环境设置完成")

def run_streamlit():
    """运行Streamlit应用"""
    print("启动Streamlit应用...")
    
    # 检查主应用文件是否存在
    app_file = Path("comprehensive_stock_analyzer.py")
    if not app_file.exists():
        print("❌ 错误: 找不到主应用文件 comprehensive_stock_analyzer.py")
        sys.exit(1)
    
    try:
        # 启动Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "comprehensive_stock_analyzer.py",
            "--server.address", "0.0.0.0",
            "--server.port", "8501",
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def main():
    """主函数"""
    print("🚀 全维度AI选股系统启动器")
    print("=" * 50)
    
    # 检查Python版本
    check_python_version()
    
    # 检查并安装依赖
    if not check_dependencies():
        choice = input("\n是否自动安装缺少的依赖包? (y/n): ")
        if choice.lower() == 'y':
            if not install_dependencies():
                sys.exit(1)
        else:
            print("请手动安装依赖包后再运行")
            sys.exit(1)
    
    # 设置环境
    setup_environment()
    
    print("\n" + "=" * 50)
    print("🎉 环境检查完成，启动应用...")
    print("📱 应用将在浏览器中打开: http://localhost:8501")
    print("⏹️  按 Ctrl+C 停止应用")
    print("=" * 50)
    
    # 运行应用
    run_streamlit()

if __name__ == "__main__":
    main()