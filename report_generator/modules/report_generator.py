import os
import json
from typing import Dict, List, Optional, Any
from report_generator.modules.file_reader import FileReader
from report_generator.modules.code_parser import CodeParser
from report_generator.modules.llm_api import APIClientFactory, MockLLMClient


class ReportGenerator:
    """
    实验报告生成器，负责根据实验要求和代码分析结果生成报告内容
    """
    
    REPORT_MODULES = [
        'title',          # 标题和基本信息
        'introduction',   # 引言/实验目的
        'background',     # 实验背景和原理
        'implementation', # 实验实现（代码分析）
        'results',        # 实验结果
        'analysis',       # 结果分析
        'conclusion'      # 结论
        # 移除references模块
    ]
    
    def __init__(self, llm_provider: str = "openai", **kwargs):
        """
        初始化报告生成器
        
        Args:
            llm_provider: LLM提供商
            **kwargs: 额外参数，如model、api_key等
        """
        self.llm_client = APIClientFactory.create_client(llm_provider, **kwargs)
        self.experiment_requirements = ""
        self.code_analysis_results = {}
        self.generated_sections = {}
    
    def load_experiment_requirements(self, file_path: str) -> bool:
        """
        加载实验要求文件
        
        Args:
            file_path: 实验要求文件路径
            
        Returns:
            是否加载成功
        """
        try:
            reader = FileReader()
            content = reader.read_file(file_path)
            if content:
                self.experiment_requirements = content
                return True
        except Exception as e:
            print(f"加载实验要求失败: {e}")
        return False
    
    def analyze_code(self, code_path: str) -> bool:
        """
        分析源代码
        
        Args:
            code_path: 源代码文件或目录路径
            
        Returns:
            是否分析成功
        """
        try:
            if os.path.isfile(code_path):
                # 单个文件分析
                result = CodeParser.parse_code(code_path)
                if result:
                    language = result['language']
                    self.code_analysis_results = {language: [result]}
                    return True
            elif os.path.isdir(code_path):
                # 目录分析
                results = CodeParser.parse_code_directory(code_path)
                if results:
                    self.code_analysis_results = results
                    return True
        except Exception as e:
            print(f"代码分析失败: {e}")
        return False
    
    def analyze_multiple_code_files(self, code_files: List[str]) -> bool:
        """
        分析多个源代码文件
        
        Args:
            code_files: 源代码文件路径列表
            
        Returns:
            是否分析成功
        """
        try:
            # 初始化结果字典
            self.code_analysis_results = {}
            
            # 分析每个文件
            for code_file in code_files:
                if os.path.isfile(code_file):
                    result = CodeParser.parse_code(code_file)
                    if result:
                        language = result['language']
                        # 将文件分析结果按语言分类
                        if language not in self.code_analysis_results:
                            self.code_analysis_results[language] = []
                        self.code_analysis_results[language].append(result)
            
            # 检查是否有成功分析的文件
            return any(len(files) > 0 for files in self.code_analysis_results.values())
        except Exception as e:
            print(f"多文件代码分析失败: {e}")
            return False
    
    def _compress_text_with_llm(self, text: str, target_length: int = 2000) -> str:
        """
        使用LLM压缩文本，保留关键信息
        
        Args:
            text: 需要压缩的文本
            target_length: 目标长度限制
            
        Returns:
            压缩后的文本
        """
        # 构建压缩提示词
        compress_prompt = f"""
你是一个专业的文本压缩助手。请将以下实验要求文本压缩为约{target_length}字符的摘要，保留所有关键信息。

文本内容:
{text}

要求:
1. 保留所有关于实验目的、要求、步骤、评估标准的关键信息
2. 移除冗余描述，但确保不丢失重要细节
3. 保持内容的逻辑连贯性和可读性
4. 压缩后的文本应适合作为实验报告生成的输入

请直接输出压缩后的文本，不要添加额外说明。
"""
        
        try:
            # 使用LLM进行压缩
            compressed_text = self.llm_client.generate(compress_prompt, temperature=0.3)
            return compressed_text
        except Exception as e:
            print(f"文本压缩失败，使用截断方案: {e}")
            # 如果压缩失败，回退到简单截断
            return text[:target_length] + "...（文本压缩失败，已截断）"
    
    def _generate_prompt_for_module(self, module: str) -> str:
        """
        为指定模块生成提示词
        
        Args:
            module: 模块名称
            
        Returns:
            提示词文本
        """
        base_prompt = f"你是一位专业的实验报告撰写助手。请根据以下信息生成实验报告的{module}部分。\n\n"
        
        # 添加实验要求
        base_prompt += "【实验要求】\n"
        if len(self.experiment_requirements) > 2000:
            # 使用LLM压缩知识
            compressed_requirements = self._compress_text_with_llm(self.experiment_requirements)
            base_prompt += compressed_requirements
            base_prompt += "\n\n（实验要求内容已压缩处理，保留关键信息）\n"
        else:
            # 直接使用原始内容
            base_prompt += self.experiment_requirements
        base_prompt += "\n\n"
        
        # 添加代码分析结果
        if self.code_analysis_results:
            base_prompt += "【代码分析结果】\n"
            for lang, files in self.code_analysis_results.items():
                base_prompt += f"语言: {lang}, 文件数量: {len(files)}\n"
                for file in files[:3]:  # 只显示前3个文件的详细信息
                    if lang == 'python':
                        base_prompt += f"- 文件分析: 函数数量 {len(file.get('functions', []))}, "
                        base_prompt += f"类数量 {len(file.get('classes', []))}\n"
                        # 添加主要函数信息
                        for func in file.get('functions', [])[:3]:
                            base_prompt += f"  * 函数: {func['name']}({func['arguments']})\n"
                    else:
                        base_prompt += f"- 代码行数: {file.get('code_lines', 0)}\n"
        base_prompt += "\n\n"
        
        # 根据模块类型添加特定指令，优化为更自然的人类书写风格，添加小标题和分论点要求
        module_instructions = {
            'title': "请生成一个合适的实验报告标题，并添加作者信息、日期等基本信息。标题应简洁明了，反映实验内容。",
            'introduction': "请生成实验报告的引言部分，使用合适的小标题（如'实验目的'、'实验意义'等）和分论点结构。清晰描述实验的目的和意义，说明实验要解决的问题和预期达到的目标。确保内容逻辑清晰，层次分明。",
            'background': "请生成实验背景和原理部分，使用合适的小标题（如'理论基础'、'技术背景'等）和分论点结构。详细介绍实验相关的背景知识和理论原理，包括必要的公式、算法说明等。确保内容逻辑清晰，层次分明。",
            'implementation': "请生成实验实现部分，使用合适的小标题（如'代码结构'、'核心算法'等）和分论点结构。详细分析代码实现，说明关键算法、数据结构和实现细节。务必引用并分析完整的程序代码内容。重点突出代码的创新性和技术亮点。确保内容逻辑清晰，层次分明。务必包含对源代码的分析，在引用代码的时候不要写多少行，要复制源代码",
            'results': "请生成实验结果部分，使用合适的小标题（如'功能验证'、'性能测试'等）和分论点结构。总结实验的主要结果，包括程序的功能、运行情况等。可以提及关键的输出或性能指标。确保内容逻辑清晰，层次分明。",
            'analysis': "请生成结果分析部分，使用合适的小标题（如'问题分析'、'解决方案'等）和分论点结构。对实验结果进行深入分析，讨论实验中遇到的问题及解决方案，评估代码的优缺点。在分析过程中，请务必引用并分析具体的实验源代码片段，通过代码示例来支持你的分析观点。例如：或者\"从代码片段中可以看出...\"。确保内容逻辑清晰，层次分明。",
            'conclusion': "请生成结论部分，使用合适的小标题（如'实验总结'、'改进建议'等）和分论点结构。总结本次实验的收获和体会，提出改进建议和未来工作方向。确保内容逻辑清晰，层次分明。"
        }
        
        base_prompt += f"【{module}部分写作要求】\n"
        base_prompt += module_instructions.get(module, "请生成该部分内容")
        base_prompt += "\n\n写作风格要求：\n"
        base_prompt += "1. 请使用自然、流畅的语言，避免过于机械和格式化的表达\n"
        base_prompt += "2. 减少使用分点列表（除非绝对必要），优先使用连贯的段落形式\n"
        base_prompt += "3. 适当使用连接词使内容过渡自然\n"
        base_prompt += "4. 避免连续的短句，合理组织句子结构\n"
        base_prompt += "5. 注意控制段落长度，避免过长或过短\n"
        base_prompt += "6. 请确保文本中没有多余的空行或不必要的空格\n"
        base_prompt += "\n请直接生成该部分内容，不需要额外的解释。"
        
        return base_prompt
    
    def generate_module(self, module: str) -> Optional[str]:
        """
        生成单个模块的内容
        
        Args:
            module: 模块名称
            
        Returns:
            生成的模块内容
        """
        if module not in self.REPORT_MODULES:
            print(f"未知的报告模块: {module}")
            return None
        
        # 检查必要信息
        if not self.experiment_requirements:
            print("请先加载实验要求")
            return None
        
        try:
            # 生成提示词
            prompt = self._generate_prompt_for_module(module)
            
            # 调用LLM生成内容
            content = self.llm_client.generate(prompt, temperature=0.3)
            
            if content:
                self.generated_sections[module] = content
                return content
        except Exception as e:
            print(f"生成{module}模块失败: {e}")
        
        return None
    
    def generate_all_modules(self) -> Dict[str, Optional[str]]:
        """
        生成所有报告模块
        
        Returns:
            各模块生成结果字典
        """
        results = {}
        
        for module in self.REPORT_MODULES:
            print(f"正在生成 {module} 模块...")
            results[module] = self.generate_module(module)
        
        return results
    
    def get_generated_content(self) -> Dict[str, str]:
        """
        获取已生成的所有内容
        
        Returns:
            已生成内容的字典
        """
        return self.generated_sections.copy()
    
    def save_progress(self, file_path: str) -> bool:
        """
        保存当前进度
        
        Args:
            file_path: 保存文件路径
            
        Returns:
            是否保存成功
        """
        try:
            data = {
                'experiment_requirements': self.experiment_requirements,
                'code_analysis_results': self.code_analysis_results,
                'generated_sections': self.generated_sections
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存进度失败: {e}")
            return False
    
    def load_progress(self, file_path: str) -> bool:
        """
        加载之前保存的进度
        
        Args:
            file_path: 进度文件路径
            
        Returns:
            是否加载成功
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.experiment_requirements = data.get('experiment_requirements', '')
            self.code_analysis_results = data.get('code_analysis_results', {})
            self.generated_sections = data.get('generated_sections', {})
            
            print(f"成功加载进度，已生成{len(self.generated_sections)}个模块")
            return True
        except Exception as e:
            print(f"加载进度失败: {e}")
            return False
    
    def export_report(self, sections: Dict[str, str], output_path: str) -> bool:
        """
        导出完整报告
        
        Args:
            sections: 报告各部分内容（Markdown格式）
            output_path: 输出文件路径
            
        Returns:
            是否导出成功
        """
        try:
            # 使用MarkdownToWordConverter将API返回的Markdown内容转换为Word
            converter = MarkdownToWordConverter()
            
            # 直接使用converter转换并保存
            return converter.convert_sections(sections, output_path)
        
        except Exception as e:
            print(f"导出报告失败: {e}")
            return False


if __name__ == "__main__":
    # 测试代码
    generator = ReportGenerator(llm_provider="openai")
    
    # 模拟加载实验要求和代码分析
    generator.experiment_requirements = "实验要求：实现一个简单的计算器程序，支持加减乘除运算，并进行单元测试。"
    generator.code_analysis_results = {
        'python': [
            {
                'language': 'python',
                'functions': [
                    {'name': 'add', 'arguments': 'a, b', 'body_preview': 'return a + b'},  # 简化的预览
                    {'name': 'subtract', 'arguments': 'a, b', 'body_preview': 'return a - b'},
                    {'name': 'multiply', 'arguments': 'a, b', 'body_preview': 'return a * b'},
                    {'name': 'divide', 'arguments': 'a, b', 'body_preview': 'if b == 0:\n    raise ValueError("除数不能为零")\nreturn a / b'}
                ],
                'classes': [],
                'code_lines': 50,
                'has_main': True
            }
        ]
    }
    
    # 测试生成单个模块
    print("\n=== 测试生成 introduction 模块 ===")
    intro = generator.generate_module('introduction')
    if intro:
        print("\n生成结果:")
        print(intro[:300] + "..." if len(intro) > 300 else intro)