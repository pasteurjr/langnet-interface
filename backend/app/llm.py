"""
LLM Integration Module
Supports OpenAI, DeepSeek, Anthropic, LM Studio
"""
import os
from typing import Dict, List, Optional, Any
from openai import OpenAI
from anthropic import Anthropic
from app.config import settings


class LLMClient:
    """Unified LLM client supporting multiple providers"""

    def __init__(self):
        self.provider = settings.llm_provider.lower()

        if self.provider == "openai":
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model_name
        elif self.provider == "deepseek":
            self.client = OpenAI(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_api_base
            )
            self.model = settings.deepseek_model_name
        elif self.provider == "lmstudio":
            self.client = OpenAI(
                api_key="lm-studio",  # LM Studio doesn't require a real key
                base_url=settings.lmstudio_api_base
            )
            self.model = settings.lmstudio_model_name
        elif self.provider == "anthropic":
            self.client = Anthropic(api_key=settings.anthropic_api_key)
            self.model = settings.anthropic_model_name
        elif self.provider == "claude_code":
            # Claude Code uses OpenAI-compatible API
            self.client = OpenAI(
                api_key="not-needed",  # Claude Code API doesn't need key
                base_url=settings.claude_code_api_base
            )
            self.model = settings.claude_code_model_name
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        """
        Generate completion from LLM

        Args:
            prompt: User prompt
            system: System prompt (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated text
        """
        if self.provider in ["openai", "deepseek", "lmstudio", "claude_code"]:
            return self._complete_openai(prompt, system, temperature, max_tokens, **kwargs)
        elif self.provider == "anthropic":
            return self._complete_anthropic(prompt, system, temperature, max_tokens, **kwargs)

    def _complete_openai(
        self,
        prompt: str,
        system: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """OpenAI completion"""
        messages = []

        if system:
            messages.append({"role": "system", "content": system})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        return response.choices[0].message.content

    def _complete_anthropic(
        self,
        prompt: str,
        system: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Anthropic completion"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system if system else "",
            messages=[
                {"role": "user", "content": prompt}
            ],
            **kwargs
        )

        return response.content[0].text

    def extract_json(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Extract structured JSON from LLM response

        Args:
            prompt: User prompt requesting JSON
            system: System prompt (optional)
            **kwargs: Additional parameters

        Returns:
            Parsed JSON dictionary
        """
        import json

        # Add JSON instruction to system prompt
        json_instruction = "\n\nRespond ONLY with valid JSON. Do not include any markdown formatting or explanations."

        if system:
            system = system + json_instruction
        else:
            system = json_instruction

        response = self.complete(prompt, system, temperature=0.3, **kwargs)

        # Remove markdown code blocks if present
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]

        response = response.strip()

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\n\nResponse: {response}")


# Global LLM client instance
llm_client = LLMClient()


def get_llm_client() -> LLMClient:
    """Get global LLM client instance"""
    return llm_client
