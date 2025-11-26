import os
import re
from typing import Dict, List, Optional, Any


class CodeParser:
    """
    代码文件解析模块，支持多种编程语言的代码分析
    """
    
    # 支持的编程语言及其文件扩展名
    SUPPORTED_LANGUAGES = {
        'python': ['.py'],
        'java': ['.java'],
        'javascript': ['.js', '.jsx'],
        'typescript': ['.ts', '.tsx'],
        'c': ['.c'],
        'cpp': ['.cpp', '.cc', '.cxx', '.c++'],
        'csharp': ['.cs'],
        'go': ['.go'],
        'rust': ['.rs'],
        'php': ['.php']
    }
    
    @staticmethod
    def get_language(file_path: str) -> Optional[str]:
        """
        根据文件扩展名确定编程语言
        
        Args:
            file_path: 文件路径
            
        Returns:
            语言名称，未知返回None
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        for lang, exts in CodeParser.SUPPORTED_LANGUAGES.items():
            if file_ext in exts:
                return lang
        return None
    
    @staticmethod
    def read_code_file(file_path: str) -> Optional[str]:
        """
        读取代码文件内容
        
        Args:
            file_path: 代码文件路径
            
        Returns:
            文件内容，失败返回None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as file:
                    return file.read()
            except Exception as e:
                print(f"读取代码文件失败 (编码错误): {e}")
                return None
        except Exception as e:
            print(f"读取代码文件失败: {e}")
            return None
    
    @staticmethod
    def parse_python_code(code: str) -> Dict[str, Any]:
        """
        解析Python代码，提取函数、类、导入等信息
        
        Args:
            code: Python代码内容
            
        Returns:
            包含代码结构信息的字典
        """
        # 提取导入语句
        imports = re.findall(r'^(?:from\s+([\w.]+)\s+)?import\s+([\w.,\s*]+)', code, re.MULTILINE)
        
        # 提取函数
        functions = []
        function_pattern = r'def\s+([\w_]+)\s*\(([^)]*)\)\s*:'
        for match in re.finditer(function_pattern, code):
            func_name = match.group(1)
            args = match.group(2)
            # 尝试提取函数注释和实现
            start_pos = match.end()
            # 简单的缩进分析来获取函数体范围
            lines = code[start_pos:].split('\n')
            func_body = []
            indent_level = 0
            first_line = True
            
            for line in lines:
                stripped = line.lstrip()
                if not stripped or stripped.startswith('#'):
                    func_body.append(line)
                    continue
                
                if first_line:
                    # 计算第一行的缩进
                    indent_level = len(line) - len(stripped)
                    first_line = False
                
                current_indent = len(line) - len(stripped)
                if current_indent < indent_level and stripped:
                    break
                
                func_body.append(line)
            
            functions.append({
                'name': func_name,
                'arguments': args.strip(),
                'body_preview': '\n'.join(func_body[:3]) + ('...' if len(func_body) > 3 else '')
            })
        
        # 提取类
        classes = []
        class_pattern = r'class\s+([\w_]+)\s*(?:\(([^)]*)\))?\s*:'
        for match in re.finditer(class_pattern, code):
            class_name = match.group(1)
            inheritance = match.group(2) or ''
            classes.append({
                'name': class_name,
                'inheritance': inheritance.strip()
            })
        
        return {
            'language': 'python',
            'imports': imports,
            'functions': functions,
            'classes': classes,
            'code_lines': len(code.split('\n')),
            'has_main': 'if __name__ == "__main__":' in code
        }
    
    @staticmethod
    def parse_code(file_path: str) -> Optional[Dict[str, Any]]:
        """
        主解析函数，根据语言选择合适的解析方法
        
        Args:
            file_path: 代码文件路径
            
        Returns:
            解析结果，失败返回None
        """
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return None
        
        language = CodeParser.get_language(file_path)
        if not language:
            print(f"不支持的编程语言: {file_path}")
            return None
        
        code = CodeParser.read_code_file(file_path)
        if not code:
            return None
        
        # 根据语言选择解析方法
        if language == 'python':
            return CodeParser.parse_python_code(code)
        else:
            # 对于其他语言，返回基本信息，包含完整代码
            return {
                'language': language,
                'code_lines': len(code.split('\n')),
                'file_path': file_path,
                'raw_code': code  # 返回完整代码内容
            }
    
    @staticmethod
    def parse_code_directory(directory: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        解析整个目录中的代码文件
        
        Args:
            directory: 目录路径
            
        Returns:
            按语言分类的代码解析结果
        """
        results = {}
        
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                result = CodeParser.parse_code(file_path)
                if result:
                    language = result['language']
                    if language not in results:
                        results[language] = []
                    results[language].append(result)
        
        return results


if __name__ == "__main__":
    # 测试代码
    test_file = "example.py"  # 替换为实际的测试文件
    if os.path.exists(test_file):
        result = CodeParser.parse_code(test_file)
        if result:
            print(f"语言: {result['language']}")
            print(f"代码行数: {result['code_lines']}")
            if 'functions' in result:
                print(f"函数数量: {len(result['functions'])}")
                for func in result['functions'][:3]:  # 只显示前3个函数
                    print(f"  - {func['name']}({func['arguments']})")