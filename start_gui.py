#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验报告生成器GUI启动脚本
用于跨平台启动图形界面
"""

import os
import sys
import subprocess
import platform


def print_info(message):
    """打印信息"""
    print(f"[信息] {message}")


def print_error(message):
    """打印错误信息"""
    print(f"[错误] {message}")


def check_python_version():
    """检查Python版本"""
    required_version = (3, 6)
    current_version = sys.version_info
    
    if current_version < required_version:
        print_error(f"Python版本过低，需要Python {required_version[0]}.{required_version[1]}或更高版本")
        print(f"当前Python版本: {current_version[0]}.{current_version[1]}.{current_version[2]}")
        return False
    return True


def activate_virtual_env():
    """激活虚拟环境"""
    venv_path = os.path.join(os.getcwd(), "venv")
    if os.path.exists(venv_path):
        print_info("检测到虚拟环境，尝试激活...")
        
        if platform.system() == "Windows":
            activate_script = os.path.join(venv_path, "Scripts", "activate")
            if os.path.exists(activate_script):
                # 在Windows上，我们不能直接激活虚拟环境，而是需要重新启动Python进程
                python_exe = os.path.join(venv_path, "Scripts", "python.exe")
                if os.path.exists(python_exe):
                    print_info(f"使用虚拟环境中的Python: {python_exe}")
                    return python_exe
        else:
            # Linux/macOS
            activate_script = os.path.join(venv_path, "bin", "activate")
            if os.path.exists(activate_script):
                python_exe = os.path.join(venv_path, "bin", "python")
                if os.path.exists(python_exe):
                    print_info(f"使用虚拟环境中的Python: {python_exe}")
                    return python_exe
    
    # 未找到虚拟环境或激活失败，返回系统Python
    return sys.executable


def install_dependencies():
    """安装依赖"""
    requirements_file = os.path.join(os.getcwd(), "requirements.txt")
    if os.path.exists(requirements_file):
        print_info("安装/更新依赖...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file, "--upgrade"])
            print_info("依赖安装完成")
        except subprocess.CalledProcessError as e:
            print_error(f"依赖安装失败: {e}")
            return False
    return True


def start_gui():
    """启动GUI"""
    print_info("正在启动实验报告生成器GUI...")
    
    try:
        # 确保在项目根目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        # 设置PYTHONPATH环境变量，确保能找到report_generator模块
        path_separator = ';' if os.name == 'nt' else ':'
        if 'PYTHONPATH' in os.environ:
            os.environ['PYTHONPATH'] = script_dir + path_separator + os.environ['PYTHONPATH']
        else:
            os.environ['PYTHONPATH'] = script_dir
        
        # 直接运行GUI模块
        subprocess.run([sys.executable, "-m", "report_generator.gui"])
        
    except KeyboardInterrupt:
        print_info("程序被用户中断")
    except Exception as e:
        print_error(f"启动GUI时发生错误: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键继续...")


def main():
    """主函数"""
    print("=" * 60)
    print("       实验报告生成器GUI启动脚本       ")
    print("=" * 60)
    
    # 检查Python版本
    if not check_python_version():
        input("按回车键退出...")
        return
    
    # 安装依赖
    install_dependencies()
    
    # 启动GUI
    start_gui()
    
    print("程序已退出")


if __name__ == "__main__":
    main()