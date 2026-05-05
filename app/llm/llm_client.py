"""
LLM Client for Groq API integration.
Provides core reasoning engine for all agents.
"""

import json
import logging
from typing import Dict, Optional, List
from groq import Groq

logger = logging.getLogger(__name__)


class LLMClient:
    """
    LLM Client wrapper for Groq API.
    Handles all LLM-based reasoning for the financial AI system.
    """
    
    def __init__(self, api_key: str, model: str = "mixtral-8x7b-32768"):
        """
        Initialize LLM client.
        
        Args:
            api_key: Groq API key
            model: Model to use (default: mixtral-8x7b-32768)
        """
        self.client = Groq(api_key=api_key)
        self.model = model
        logger.info(f"Initialized LLM client with model: {model}")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, 
                 temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """
        Generate text completion from LLM.
        
        Args:
            prompt: User/context prompt
            system_prompt: System message
            temperature: Creativity level (0.0-1.0)
            max_tokens: Max response tokens
            
        Returns:
            Generated text
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            raise
    
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None,
                     temperature: float = 0.3, max_tokens: int = 2048) -> Dict:
        """
        Generate JSON-formatted response from LLM.
        
        Args:
            prompt: User/context prompt
            system_prompt: System message
            temperature: Creativity level (lower for consistency)
            max_tokens: Max response tokens
            
        Returns:
            Parsed JSON dict
        """
        try:
            # Add JSON instruction to prompt
            json_instruction = "\nRespond ONLY with valid JSON, no markdown or extra text."
            full_prompt = prompt + json_instruction
            
            response_text = self.generate(
                full_prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Clean response (remove markdown code blocks if present)
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            # Parse JSON
            parsed = json.loads(response_text)
            return parsed
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}\nResponse: {response_text}")
            raise ValueError(f"LLM did not return valid JSON: {response_text}")
        except Exception as e:
            logger.error(f"LLM JSON generation error: {e}")
            raise
    
    def analyze(self, context: str, query: str, system_prompt: Optional[str] = None) -> str:
        """
        Analyze context and answer query.
        
        Args:
            context: Context/background information
            query: Question to answer
            system_prompt: System message
            
        Returns:
            Analysis result
        """
        prompt = f"""
Context:
{context}

Question:
{query}

Provide a thorough analysis based on the context.
"""
        return self.generate(prompt, system_prompt=system_prompt)
    
    def synthesize(self, results: Dict, query: str, system_prompt: Optional[str] = None) -> Dict:
        """
        Synthesize multiple analysis results into a decision.
        
        Args:
            results: Dict with analysis results from different agents
            query: Original query
            system_prompt: System message
            
        Returns:
            Synthesized decision
        """
        prompt = f"""
Original Query: {query}

Analysis Results:
{json.dumps(results, indent=2)}

Synthesize these results into a coherent decision.
Return JSON with:
- final_decision: Clear action recommendation
- confidence: 0.0-1.0
- key_factors: List of critical factors
- risks: Identified risks
- recommendations: Actionable next steps
"""
        return self.generate_json(prompt, system_prompt=system_prompt, temperature=0.3)
