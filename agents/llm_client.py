"""
LLM Client wrapper for google-generativeai (Gemini) and openai APIs.
Provides unified execution interfaces and fallback logic.
"""

import logging
from typing import Dict, Any, Optional

from config.settings import settings

logger = logging.getLogger("llm_client")

# Initialize SDK configurations lazily
_gemini_configured = False


def _configure_gemini():
    global _gemini_configured
    if _gemini_configured:
        return True
    key = settings.gemini_api_key
    if not key:
        return False
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        _gemini_configured = True
        return True
    except Exception as e:
        logger.error(f"Failed to configure google-generativeai: {e}")
        return False


class LLMClient:
    """
    Client for managing inference requests to Gemini (primary) and OpenAI (secondary) models.
    """

    def __init__(self, model_name: Optional[str] = None):
        # Default fallback models
        self.model_name = model_name or settings.get("models.primary.name", "gemini-1.5-flash")
        self.primary_provider = settings.get("models.primary.provider", "google")

    def execute_prompt(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Executes a prompt query, choosing the appropriate LLM provider based on settings and keys.
        """
        # Determine provider by model name prefix or config
        model_lower = self.model_name.lower()
        
        is_google = "gemini" in model_lower or self.primary_provider == "google"
        is_openai = "gpt" in model_lower or self.primary_provider == "openai"

        # Check credentials
        gemini_key = settings.gemini_api_key
        openai_key = settings.openai_api_key

        # If google model chosen, try Google first
        if is_google and gemini_key:
            try:
                if _configure_gemini():
                    import google.generativeai as genai
                    logger.info(f"Invoking Gemini model: '{self.model_name}'...")
                    
                    config = {}
                    temp = settings.get("models.primary.temperature")
                    if temp is not None:
                        config["temperature"] = temp
                    max_tokens = settings.get("models.primary.max_tokens")
                    if max_tokens is not None:
                        config["max_output_tokens"] = max_tokens

                    model = genai.GenerativeModel(
                        model_name=self.model_name,
                        system_instruction=system_instruction,
                        generation_config=config if config else None
                    )
                    response = model.generate_content(prompt)
                    return response.text.strip()
            except Exception as e:
                logger.warning(f"Gemini execution failed: {e}. Attempting OpenAI fallback...")

        # If openai chosen, or fallback from google triggered
        if (is_openai or (is_google and not gemini_key)) and openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)
                
                # Default fallback model name for OpenAI
                openai_model = self.model_name if is_openai else "gpt-4o-mini"
                logger.info(f"Invoking OpenAI model: '{openai_model}'...")

                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})

                response = client.chat.completions.create(
                    model=openai_model,
                    messages=messages,
                    temperature=settings.get("models.primary.temperature", 0.3)
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"OpenAI execution failed: {e}")

        # If no keys are configured, return a mock response for workflow demonstration
        logger.warning(
            f"No API credentials found for run (GEMINI_API_KEY={bool(gemini_key)}, OPENAI_API_KEY={bool(openai_key)}). "
            "Falling back to mock execution."
        )
        return self._generate_mock_response(prompt, system_instruction)

    def _generate_mock_response(self, prompt: str, system_instruction: Optional[str]) -> str:
        """Generates a structured mock response when no API keys are present."""
        prompt_preview = prompt[:100] + "..." if len(prompt) > 100 else prompt
        
        # Simple heuristics to generate slightly customized mock outputs based on query content
        prompt_lower = prompt.lower()
        if "synthesize" in prompt_lower or "report" in prompt_lower:
            return f"""# Simulated Workforce Intelligence Report: Cloud Engineering
Query/Goal: {prompt_preview}
## 1. Executive Summary
This is a simulated mock analysis report covering Cloud Engineering and workforce trends.
## 2. Key Insights
- High demand for cloud engineering roles.
- Remote work options increase resource satisfaction.
"""
        elif "research" in prompt_lower or "search" in prompt_lower:
            return f"""# Simulated Search Results
Query: {prompt_preview}
- **Insight 1**: Market data indicates a 15% increase in skill requirements for cloud computing.
- **Insight 2**: Workforce turnover is stabilized at 8.4% globally.
- **Insight 3**: Remote roles have reduced by 5% compared to 2024 benchmarks.

Sources:
- https://www.bls.gov/news.release/pdf/empsit.pdf
- https://www.linkedin.com/economic-graph
"""
        
        return f"""# Workforce Intelligence Analytics Response
System Instruction: {system_instruction or 'None'}
Prompt: {prompt_preview}

This is a simulated mock analytics report generated because no live API keys (GEMINI_API_KEY or OPENAI_API_KEY) are configured in the environment variables.
"""
