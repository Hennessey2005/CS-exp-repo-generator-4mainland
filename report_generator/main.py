#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验报告生成器主程序
"""

import os
import sys
import argparse
import json
import logging
from typing import Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("report_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("report_generator")

# 导入核心模块
try:
    from report_generator.modules.report_generator import ReportGenerator
    from report_generator.modules.word_exporter import WordExporter
except ImportError as e:
    logger.error(f"导入模块失败: {e}")
    print(f"错误: 无法导入必要的模块。请确保PYTHONPATH正确设置。")
    sys.exit(1)


def print_banner():
    """
    打印程序横幅
    """
    banner = """
    ===================================================================
                   实验报告自动生成系统 v1.0
    ===================================================================
    功能：根据源代码和实验要求，利用大语言模型生成实验报告
    支持：PDF/Word格式要求文档，多语言代码分析，Word格式报告输出
    ===================================================================
    """
    print(banner)


def clear_screen():
    """
    清屏函数
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def pause():
    """
    暂停函数
    """
    input("\n按回车键继续...")


def setup_environment():
    """
    设置运行环境，确保必要的目录存在
    
    Returns:
        str: 输出目录路径
    """
    # 确保输出目录存在
    output_dir = "output"
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"创建输出目录: {output_dir}")
        return os.path.abspath(output_dir)
    except Exception as e:
        logger.error(f"创建输出目录失败: {e}")
        raise


def create_config_file():
    """
    创建默认配置文件
    
    Returns:
        dict: 配置字典
    """
    config = {
        "llm_provider": "deepseek",  # 使用deepseek作为默认提供商
        "model": "deepseek-chat",
        "temperature": 0.3,
        "max_tokens": 2000
    }
    
    # 保存配置文件
    config_dir = "configs"
    try:
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            logger.info(f"创建配置目录: {config_dir}")
        
        config_path = os.path.join(config_dir, "config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"配置文件已创建: {config_path}")
        print(f"配置文件已创建: {config_path}")
        print("请根据需要修改配置文件中的参数")
        return config
    except Exception as e:
        logger.error(f"创建配置文件失败: {e}")
        raise


def load_config():
    """
    加载配置文件
    
    Returns:
        dict: 配置字典
    """
    config_path = os.path.join("configs", "config.json")
    
    if not os.path.exists(config_path):
        logger.info(f"配置文件不存在，创建默认配置: {config_path}")
        return create_config_file()
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            logger.info(f"成功加载配置文件: {config_path}")
            return config
    except json.JSONDecodeError as e:
        logger.error(f"配置文件格式错误: {e}")
        print(f"错误: 配置文件格式不正确。")
        return create_config_file()
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        print(f"错误: 加载配置文件失败，使用默认配置。")
        return create_config_file()


def interactive_menu():
    """
    交互式菜单
    """
    clear_screen()
    print_banner()
    
    # 加载配置
    config = load_config()
    output_dir = setup_environment()
    
    # 创建报告生成器
    generator = ReportGenerator(
        llm_provider="deepseek",
        model=config.get("deepseek_model", "deepseek-chat")
    )
    
    experiment_file = None
    code_path = None
    
    while True:
        print("\n=== 主菜单 ===")
        print("1. 加载实验要求文件")
        print("2. 分析源代码")
        print("3. 生成报告模块")
        print("4. 生成完整报告")
        print("5. 保存/加载进度")
        print("6. 配置设置")
        print("7. 退出")
        
        choice = input("\n请选择操作 [1-7]: ")
        
        if choice == '1':
            # 加载实验要求文件
            file_path = input("请输入实验要求文件路径 (PDF/Word): ").strip()
            if os.path.exists(file_path):
                if generator.load_experiment_requirements(file_path):
                    experiment_file = file_path
                    print(f"✓ 成功加载实验要求文件: {os.path.basename(file_path)}")
                else:
                    print("✗ 加载失败，请检查文件格式")
            else:
                print("✗ 文件不存在")
            pause()
            
        elif choice == '2':
            # 分析源代码
            path = input("请输入源代码文件或目录路径: ").strip()
            if os.path.exists(path):
                if generator.analyze_code(path):
                    code_path = path
                    print(f"✓ 成功分析代码: {os.path.basename(path) if os.path.isfile(path) else path}")
                    # 显示分析结果摘要
                    for lang, files in generator.code_analysis_results.items():
                        print(f"  - 语言: {lang}, 文件数量: {len(files)}")
                else:
                    print("[✗] 代码分析失败")
            else:
                print("✗ 路径不存在")
            pause()
            
        elif choice == '3':
            # 生成报告模块
            print("\n可选模块:")
            for i, module in enumerate(ReportGenerator.REPORT_MODULES, 1):
                status = "✓" if module in generator.generated_sections else "✗"
                print(f"{i}. {module} {status}")
            
            module_choice = input("\n请选择要生成的模块序号，或输入'a'生成所有模块: ").strip()
            
            if module_choice.lower() == 'a':
                # 生成所有模块
                print("\n开始生成所有模块...")
                results = generator.generate_all_modules()
                success_count = sum(1 for r in results.values() if r)
                print(f"\n生成完成，成功生成 {success_count}/{len(results)} 个模块")
            elif module_choice.isdigit():
                idx = int(module_choice) - 1
                if 0 <= idx < len(ReportGenerator.REPORT_MODULES):
                    module = ReportGenerator.REPORT_MODULES[idx]
                    print(f"\n开始生成 {module} 模块...")
                    content = generator.generate_module(module)
                    if content:
                        print("✓ 模块生成成功")
                        # 显示部分内容预览
                        preview = content[:200] + "..." if len(content) > 200 else content
                        print(f"\n内容预览:\n{preview}")
                    else:
                        print("✗ 模块生成失败")
                else:
                    print("✗ 无效的模块序号")
            else:
                print("✗ 无效的选择")
            pause()
            
        elif choice == '4':
            # 生成完整报告
            if not generator.generated_sections:
                print("✗ 请先生成至少一个报告模块")
            else:
                # 询问输出文件名
                default_filename = "实验报告.docx"
                filename = input(f"请输入输出文件名 [{default_filename}]: ").strip() or default_filename
                
                if not filename.endswith('.docx'):
                    filename += '.docx'
                
                output_path = os.path.join(output_dir, filename)
                
                # 导出报告
                print(f"\n正在导出报告到: {output_path}")
                exporter = WordExporter()
                if exporter.export_report(generator.generated_sections, output_path):
                    print("✓ 报告导出成功!")
                else:
                    print("✗ 报告导出失败")
            pause()
            
        elif choice == '5':
            # 保存/加载进度
            print("\n1. 保存当前进度")
            print("2. 加载之前的进度")
            sub_choice = input("请选择: ").strip()
            
            if sub_choice == '1':
                # 保存进度
                if not generator.generated_sections and not generator.experiment_requirements:
                    print("✗ 没有可保存的内容")
                else:
                    save_file = input("请输入保存文件名 [progress.json]: ").strip() or "progress.json"
                    save_path = os.path.join(output_dir, save_file)
                    if generator.save_progress(save_path):
                        print(f"✓ 进度已保存到: {save_path}")
            
            elif sub_choice == '2':
                # 加载进度
                load_file = input("请输入进度文件路径: ").strip()
                if not os.path.isabs(load_file):
                    load_file = os.path.join(output_dir, load_file)
                
                if os.path.exists(load_file):
                    if generator.load_progress(load_file):
                        # 更新状态变量
                        if generator.experiment_requirements:
                            print("✓ 实验要求已恢复")
                        if generator.code_analysis_results:
                            print("✓ 代码分析结果已恢复")
                        print(f"✓ 已恢复 {len(generator.generated_sections)} 个生成的模块")
                else:
                    print("✗ 文件不存在")
            pause()
            
        elif choice == '6':
            # 配置设置
            print("\n当前配置:")
            for key, value in config.items():
                print(f"{key}: {value}")
            
            print("\n配置文件位置: configs/config.json")
            print("请手动编辑配置文件以修改设置")
            pause()
            
        elif choice == '7':
            # 退出
            print("\n感谢使用实验报告生成系统，再见!")
            break
        
        else:
            print("✗ 无效的选择，请重新输入")
            pause()

def main():
    """
    主函数，处理命令行参数并执行相应操作
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='实验报告自动生成系统')
    parser.add_argument('--interactive', '-i', action='store_true', help='启动交互式模式')
    parser.add_argument('--requirements', '-r', help='实验要求文件路径')
    parser.add_argument('--code', '-c', help='源代码文件或目录路径')
    parser.add_argument('--output', '-o', help='输出报告文件路径')
    parser.add_argument('--auto', action='store_true', help='自动模式：加载文件、生成报告并导出')
    
    # 添加GUI兼容的参数
    parser.add_argument('--code_file', action='append', help='源代码文件路径列表 (GUI兼容)')
    parser.add_argument('--requirement_files', action='append', help='实验要求文件路径列表 (GUI兼容)')
    parser.add_argument('--output_file', help='输出报告文件路径 (GUI兼容)')
    
    args = parser.parse_args()
    
    # 确保环境设置正确
    setup_environment()
    
    # 如果没有参数或指定了interactive，则启动交互式模式
    if len(sys.argv) == 1 or args.interactive:
        interactive_menu()
    elif args.auto and ((args.requirements and args.code and args.output) or 
                        (args.requirement_files and args.code_file and args.output_file)):
        # 自动模式
        print_banner()
        logger.info("启动自动模式")
        
        try:
            # 加载配置
            config = load_config()
            logger.info(f"使用配置: {config}")
            
            # 根据提供商从配置中获取正确的模型名称和API密钥
            llm_provider = config.get("llm_provider", "deepseek")
            
            # 根据不同提供商选择对应的模型名称
            if llm_provider == "openai":
                model = config.get("openai_model", "gpt-3.5-turbo")
                api_key = os.getenv("OPENAI_API_KEY", "")
            elif llm_provider == "anthropic":
                model = config.get("anthropic_model", "claude-3-opus-20240229")
                api_key = os.getenv("ANTHROPIC_API_KEY", "")
            elif llm_provider == "deepseek":
                model = config.get("deepseek_model", "deepseek-chat")
                api_key = os.getenv("DEEPSEEK_API_KEY", "")
            else:
                # 默认使用DeepSeek
                llm_provider = "deepseek"
                model = "deepseek-chat"
                api_key = os.getenv("DEEPSEEK_API_KEY", "")
            
            # 创建报告生成器
            generator = ReportGenerator(
                llm_provider=llm_provider,
                model=model,
                api_key=api_key
            )
            
            logger.info(f"使用{llm_provider}提供商，模型: {model}")
            
            # 加载实验要求
            if args.requirement_files:  # GUI模式
                logger.info(f"加载实验要求文件列表: {args.requirement_files}")
                print(f"加载实验要求文件数量: {len(args.requirement_files)}")
                for req_file in args.requirement_files:
                    print(f"  - {req_file}")
                    if not generator.load_experiment_requirements(req_file):
                        logger.error(f"加载实验要求失败: {req_file}")
                        print(f"[✗] 加载实验要求失败: {req_file}")
                        sys.exit(1)
            else:  # 命令行模式
                logger.info(f"加载实验要求文件: {args.requirements}")
                print(f"加载实验要求: {args.requirements}")
                if not generator.load_experiment_requirements(args.requirements):
                    logger.error("加载实验要求失败")
                    print("[✗] 加载实验要求失败")
                    sys.exit(1)
            
            # 分析代码
            if args.code_file:  # GUI模式，可能有多个代码文件
                logger.info(f"分析源代码文件列表: {args.code_file}")
                print(f"分析源代码文件数量: {len(args.code_file)}")
                for code_file in args.code_file:
                    print(f"  - {code_file}")
                if not generator.analyze_multiple_code_files(args.code_file):
                    logger.error("代码分析失败")
                    print("[✗] 代码分析失败")
                    sys.exit(1)
            else:  # 命令行模式，单个文件或目录
                code_path = args.code
                logger.info(f"分析源代码: {code_path}")
                print(f"分析源代码: {code_path}")
                if not generator.analyze_code(code_path):
                    logger.error("代码分析失败")
                    print("✗ 代码分析失败")
                    sys.exit(1)
            
            # 生成所有模块
            logger.info("开始生成报告内容")
            print("生成报告内容...")
            generator.generate_all_modules()
            
            # 导出报告
            output_path = args.output_file if args.output_file else args.output
            logger.info(f"导出报告到: {output_path}")
            print(f"导出报告: {output_path}")
            exporter = WordExporter()
            if exporter.export_report(generator.generated_sections, output_path):
                logger.info("报告生成完成")
                print("[✓] 报告生成完成!")
            else:
                logger.error("报告导出失败")
                print("[✗] 报告导出失败")
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"自动模式执行失败: {e}")
            print(f"[✗] 错误: {e}")
            # 检查是否是API密钥错误
            if "API key" in str(e) or "401" in str(e):
                print("请检查您的API密钥配置，可能需要在.env文件中更新OpenAI API密钥。")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已中断")
    except Exception as e:
        try:
            print(f"程序发生错误: {e}")
        except UnicodeEncodeError:
            print("程序发生错误，包含不支持的字符。")
        import traceback
        traceback.print_exc()
    finally:
        print("程序已结束")