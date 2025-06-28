#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@file: deepseek
@author: kody
@create: 2025-06-28 10:27:29
@desc:
"""

import os
import logging
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class DeepSeekClient:
    """DeepSeek API客户端"""

    def __init__(
        self, api_key: Optional[str] = None, base_url: str = "https://api.deepseek.com"
    ):
        """
        初始化DeepSeek客户端

        Args:
            api_key: API密钥，如果为None则从环境变量DEEPSEEK_API_KEY获取
            base_url: API基础URL
        """

        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API密钥未提供，请设置DEEPSEEK_API_KEY环境变量或传入api_key参数"
            )

        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

    def chat_completion(
        self,
        messages: list,
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        调用DeepSeek聊天完成API

        Args:
            messages: 消息列表，格式为[{"role": "user", "content": "..."}]
            model: 模型名称
            temperature: 温度参数，控制输出的随机性
            max_tokens: 最大输出token数
            **kwargs: 其他参数

        Returns:
            API响应字典
        """
        url = f"{self.base_url}/v1/chat/completions"

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            **kwargs,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            logger.info(f"调用DeepSeek API，模型: {model}")
            response = self.session.post(url, json=payload)
            response.raise_for_status()

            result = response.json()
            logger.info("DeepSeek API调用成功")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"DeepSeek API调用失败: {e}")
            raise

    def generate_text(
        self,
        prompt: str,
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        生成文本的便捷方法

        Args:
            prompt: 输入提示文本
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大输出token数
            system_prompt: 系统提示词

        Returns:
            生成的文本内容
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response = self.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # 提取生成的文本
            if response.get("choices") and len(response["choices"]) > 0:
                content = response["choices"][0].get("message", {}).get("content", "")
                return content.strip()
            else:
                raise ValueError("API响应中没有找到生成的文本")

        except Exception as e:
            logger.error(f"文本生成失败: {e}")
            raise

    def batch_generate(
        self,
        prompts: list,
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
    ) -> list:
        """
        批量生成文本

        Args:
            prompts: 提示文本列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大输出token数
            system_prompt: 系统提示词

        Returns:
            生成的文本列表
        """
        results = []

        for i, prompt in enumerate(prompts):
            try:
                logger.info(f"处理第 {i+1}/{len(prompts)} 个提示")
                result = self.generate_text(
                    prompt=prompt,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    system_prompt=system_prompt,
                )
                results.append(result)

            except Exception as e:
                logger.error(f"处理第 {i+1} 个提示时失败: {e}")
                results.append(None)

        return results


# 便捷函数
def generate_text(
    prompt: str,
    api_key: Optional[str] = None,
    model: str = "deepseek-chat",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    system_prompt: Optional[str] = None,
) -> str:
    """
    便捷的文本生成函数

    Args:
        prompt: 输入提示文本
        api_key: API密钥
        model: 模型名称
        temperature: 温度参数
        max_tokens: 最大输出token数
        system_prompt: 系统提示词

    Returns:
        生成的文本内容
    """
    client = DeepSeekClient(api_key=api_key)
    return client.generate_text(
        prompt=prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        system_prompt=system_prompt,
    )


def batch_generate_text(
    prompts: list,
    api_key: Optional[str] = None,
    model: str = "deepseek-chat",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    system_prompt: Optional[str] = None,
) -> list:
    """
    便捷的批量文本生成函数

    Args:
        prompts: 提示文本列表
        api_key: API密钥
        model: 模型名称
        temperature: 温度参数
        max_tokens: 最大输出token数
        system_prompt: 系统提示词

    Returns:
        生成的文本列表
    """
    client = DeepSeekClient(api_key=api_key)
    return client.batch_generate(
        prompts=prompts,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        system_prompt=system_prompt,
    )
