import os
import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, List
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class LLMClient(ABC):
    """
    大语言模型客户端抽象基类
    """
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> Optional[str]:
        """
        生成文本回复
        
        Args:
            prompt: 提示文本
            **kwargs: 其他参数
            
        Returns:
            生成的文本，失败返回None
        """
        pass
    
    def generate_batch(self, prompts: List[str], **kwargs) -> List[Optional[str]]:
        """
        批量生成文本回复
        
        Args:
            prompts: 提示文本列表
            **kwargs: 其他参数
            
        Returns:
            生成的文本列表
        """
        results = []
        for prompt in prompts:
            results.append(self.generate(prompt, **kwargs))
            # 添加延迟避免API限流
            time.sleep(0.5)
        return results


class OpenAIClient(LLMClient):
    """
    OpenAI API客户端
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        初始化OpenAI客户端
        
        Args:
            api_key: OpenAI API密钥，如果为None则从环境变量读取
            model: 使用的模型名称
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API密钥未提供")
        self.model = model
        self.base_url = "https://api.openai.com/v1"
    
    def generate(self, prompt: str, **kwargs) -> Optional[str]:
        """
        使用OpenAI API生成文本
        
        Args:
            prompt: 提示文本
            **kwargs: 其他参数，如temperature, max_tokens等
            
        Returns:
            生成的文本
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": kwargs.get("model", self.model),
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 1500)
            }
            
            # 添加额外参数
            for key in ["top_p", "frequency_penalty", "presence_penalty"]:
                if key in kwargs:
                    data[key] = kwargs[key]
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                print(f"OpenAI API错误: {response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            print(f"OpenAI API调用失败: {e}")
            return None


class AnthropicClient(LLMClient):
    """
    Anthropic (Claude) API客户端
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"):
        """
        初始化Anthropic客户端
        
        Args:
            api_key: Anthropic API密钥，如果为None则从环境变量读取
            model: 使用的模型名称
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API密钥未提供")
        self.model = model
        self.base_url = "https://api.anthropic.com/v1"
    
    def generate(self, prompt: str, **kwargs) -> Optional[str]:
        """
        使用Anthropic API生成文本
        
        Args:
            prompt: 提示文本
            **kwargs: 其他参数，如temperature, max_tokens等
            
        Returns:
            生成的文本
        """
        try:
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": kwargs.get("model", self.model),
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 1500)
            }
            
            response = requests.post(
                f"{self.base_url}/messages",
                headers=headers,
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["content"][0]["text"]
            else:
                print(f"Anthropic API错误: {response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            print(f"Anthropic API调用失败: {e}")
            return None


class DeepSeekClient(LLMClient):
    """
    DeepSeek API客户端（使用与OpenAI兼容的格式）
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-chat"):
        """
        初始化DeepSeek客户端
        
        Args:
            api_key: DeepSeek API密钥，如果为None则从环境变量读取
            model: 使用的模型名称
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未提供")
        self.model = model
        # 使用与OpenAI兼容的base_url
        self.base_url = "https://api.deepseek.com"  # 推荐使用不带v1的格式
    
    def generate(self, prompt: str, **kwargs) -> Optional[str]:
        """
        使用DeepSeek API生成文本（采用OpenAI兼容格式）
        
        Args:
            prompt: 提示文本
            **kwargs: 其他参数，如temperature, max_tokens等
            
        Returns:
            生成的文本
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 创建与OpenAI兼容的请求数据结构
            data = {
                "model": kwargs.get("model", self.model),
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 1500),
                "stream": kwargs.get("stream", False)
            }
            
            # 添加额外参数
            for key in ["top_p", "frequency_penalty", "presence_penalty"]:
                if key in kwargs:
                    data[key] = kwargs[key]
            
            # 确保使用正确的API端点
            endpoint = f"{self.base_url}/chat/completions" if "/v1" not in self.base_url else f"{self.base_url}/chat/completions"
            
            response = requests.post(
                endpoint,
                headers=headers,
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                print(f"DeepSeek API错误: {response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            print(f"DeepSeek API调用失败: {e}")
            return None


class APIClientFactory:
    """
    LLM客户端工厂类，用于创建不同的模型客户端
    """
    
    @staticmethod
    def create_client(provider: str, **kwargs) -> Optional[LLMClient]:
        """
        创建LLM客户端
        
        Args:
            provider: 服务提供商，如'openai', 'anthropic', 'deepseek'
            **kwargs: 客户端初始化参数
            
        Returns:
            LLM客户端实例
        """
        try:
            if provider.lower() == "openai":
                return OpenAIClient(**kwargs)
            elif provider.lower() == "anthropic":
                return AnthropicClient(**kwargs)
            elif provider.lower() == "deepseek":
                return DeepSeekClient(**kwargs)
            else:
                print(f"不支持的服务提供商: {provider}")
                return None
        except Exception as e:
            print(f"创建客户端失败: {e}")
            return None


# 默认客户端实现（无需API密钥的本地回退）
class MockLLMClient(LLMClient):
    """
    模拟LLM客户端，用于测试和演示
    """
    
    def generate(self, prompt: str, **kwargs) -> Optional[str]:
        """
        返回模拟的生成结果
        """
        return f"[模拟LLM响应] 您的提示包含{len(prompt)}个字符。这是一个模拟响应，实际使用时需要配置真实的API密钥。"


if __name__ == "__main__":
    # 测试代码
    try:
        # 尝试创建DeepSeek客户端（使用OpenAI兼容格式）
        print("尝试创建DeepSeek客户端（使用OpenAI兼容格式）...")
        client = APIClientFactory.create_client("deepseek")
        if not client:
            print("DeepSeek客户端创建失败，尝试使用OpenAI客户端")
            client = APIClientFactory.create_client("openai")
            if not client:
                client = MockLLMClient()
                print("使用模拟LLM客户端进行测试")
        
        test_prompt = "请简要介绍Python的主要特点"
        print(f"发送测试请求到{'DeepSeek' if isinstance(client, DeepSeekClient) else '其他'}客户端...")
        response = client.generate(test_prompt, max_tokens=500)
        if response:
            print("\n=== LLM响应 ===\n")
            print(response)
    except Exception as e:
        print(f"测试失败: {e}")