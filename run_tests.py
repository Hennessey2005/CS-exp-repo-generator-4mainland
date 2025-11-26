#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本
用于运行系统中的所有测试用例
"""

import os
import sys
import unittest
import argparse
import time
from unittest import TestLoader, TextTestRunner


def print_banner():
    """打印测试横幅"""
    banner = """
    ===================================================================
                   实验报告生成系统 - 测试套件
    ===================================================================
    """
    print(banner)


def get_test_suite(test_dir, pattern='test_*.py'):
    """获取测试套件"""
    print(f"正在收集测试用例... (目录: {test_dir}, 模式: {pattern})")
    
    # 添加项目根目录到Python路径
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # 加载测试
    loader = TestLoader()
    suite = loader.discover(test_dir, pattern=pattern)
    
    return suite


def run_tests(suite, verbose=False):
    """运行测试"""
    print(f"\n发现 {suite.countTestCases()} 个测试用例")
    print("开始运行测试...\n" + "="*70)
    
    start_time = time.time()
    
    # 创建测试运行器
    runner = TextTestRunner(
        verbosity=2 if verbose else 1,
        stream=sys.stdout,
        descriptions=True,
        failfast=False,
        buffer=False
    )
    
    # 运行测试
    result = runner.run(suite)
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    print("="*70)
    print(f"\n测试完成，耗时: {elapsed:.2f} 秒")
    
    # 打印结果摘要
    print(f"\n测试结果摘要:")
    print(f"总测试用例数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped)}")
    
    # 返回是否所有测试都通过
    return result.wasSuccessful()


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='运行实验报告生成系统的测试套件')
    parser.add_argument('--dir', '-d', default='report_generator/tests', 
                        help='测试目录路径 (默认: report_generator/tests)')
    parser.add_argument('--pattern', '-p', default='test_*.py', 
                        help='测试文件匹配模式 (默认: test_*.py)')
    parser.add_argument('--verbose', '-v', action='store_true', 
                        help='显示详细的测试输出')
    parser.add_argument('--specific', '-s', help='运行特定的测试文件')
    
    args = parser.parse_args()
    
    print_banner()
    
    try:
        if args.specific:
            # 运行特定的测试文件
            test_file = args.specific
            if not os.path.isabs(test_file):
                test_file = os.path.join(args.dir, test_file)
            
            if not os.path.exists(test_file):
                print(f"错误: 找不到测试文件 {test_file}")
                return 1
            
            # 提取文件名
            test_filename = os.path.basename(test_file)
            print(f"运行特定测试文件: {test_filename}")
            
            # 创建临时目录路径
            test_dir = os.path.dirname(test_file)
            suite = get_test_suite(test_dir, pattern=test_filename)
        else:
            # 运行所有测试
            suite = get_test_suite(args.dir, pattern=args.pattern)
        
        # 运行测试
        success = run_tests(suite, args.verbose)
        
        # 返回相应的退出码
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        return 130
    except Exception as e:
        print(f"\n测试运行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())