"""
Chat Service for Astrological Consultations
Integrates with OpenAI ChatGPT API using birth chart context
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import openai
from openai import OpenAI

from app.models import BirthChartResponse
from app.services.birth_chart import BirthChartService


class AstrologyChatService:
    """Chat service for astrological consultations using OpenAI ChatGPT."""
    
    def __init__(self):
        """Initialize the chat service with OpenAI client."""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            print("⚠️  Warning: OPENAI_API_KEY not found. Chat functionality will be limited.")
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=self.openai_api_key)
                print("✅ OpenAI Chat client initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize OpenAI client: {e}")
                self.client = None
        
        self.birth_chart_service = BirthChartService()
        
        # Conversation memory (in production, use Redis or database)
        self.conversations = {}
    
    def is_available(self) -> bool:
        """Check if the chat service is available."""
        return self.client is not None
    
    def create_astrological_context(self, birth_chart: BirthChartResponse) -> str:
        """Create detailed astrological context from birth chart data."""
        
        context_parts = []
        
        # Basic birth information
        context_parts.append(f"Birth Chart Analysis:")
        context_parts.append(f"- Birth Date/Time: {birth_chart.birth_datetime}")
        context_parts.append(f"- Location: {birth_chart.location}")
        context_parts.append(f"- House System: {birth_chart.house_system}")
        context_parts.append(f"- Ayanamsa: {birth_chart.ayanamsa}")
        
        # Key chart elements
        if birth_chart.chart_summary:
            summary = birth_chart.chart_summary
            context_parts.append(f"\nChart Summary:")
            context_parts.append(f"- Sun Sign: {summary.get('sun_sign', 'Unknown')}")
            context_parts.append(f"- Moon Sign: {summary.get('moon_sign', 'Unknown')}")
            context_parts.append(f"- Ascendant: {summary.get('ascendant_sign', 'Unknown')}")
            context_parts.append(f"- Dominant Sign: {summary.get('dominant_sign', 'Unknown')}")
            context_parts.append(f"- Dominant House: {summary.get('dominant_house', 'Unknown')}")
            context_parts.append(f"- Retrograde Planets: {summary.get('retrograde_planets', 0)}")
        
        # Planetary positions
        context_parts.append(f"\nPlanetary Positions:")
        for planet in birth_chart.planets:
            retro_status = " (Retrograde)" if planet.retrograde else ""
            context_parts.append(
                f"- {planet.planet}: {planet.degree:.1f}° {planet.sign} in House {planet.house}{retro_status}"
            )
        
        # House cusps
        context_parts.append(f"\nHouse Cusps:")
        for house in birth_chart.houses[:4]:  # First 4 houses for context
            context_parts.append(f"- House {house.number}: {house.cusp:.1f}° {house.sign}")
        
        # Key aspects (limit to major ones)
        if birth_chart.aspects:
            major_aspects = [asp for asp in birth_chart.aspects if asp.orb <= 3.0][:5]
            if major_aspects:
                context_parts.append(f"\nMajor Aspects:")
                for aspect in major_aspects:
                    context_parts.append(
                        f"- {aspect.planet1} {aspect.aspect_type} {aspect.planet2} (orb: {aspect.orb:.1f}°)"
                    )
        
        return "\n".join(context_parts)
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the astrological chat assistant."""
        
        return """You are an expert Vedic astrologer and spiritual guide with deep knowledge of:
- Vedic (Sidereal) astrology principles and techniques
- Planetary influences and their meanings
- House systems and their significance
- Aspects and their interpretations
- Ayanamsa systems and their applications
- Traditional Vedic wisdom and modern psychological insights

Your role is to provide personalized astrological guidance based on the user's birth chart data. 

Guidelines:
1. **Be Personalized**: Use the specific birth chart data provided as context for all responses
2. **Be Educational**: Explain astrological concepts clearly and help users understand their chart
3. **Be Supportive**: Offer constructive guidance and insights, focusing on growth and self-understanding
4. **Be Accurate**: Base responses on actual Vedic astrological principles
5. **Be Respectful**: Honor the sacred nature of astrological consultation
6. **Be Practical**: Provide actionable insights and recommendations when appropriate

Response Style:
- Start responses by acknowledging specific placements from their chart when relevant
- Use clear, accessible language while maintaining astrological accuracy
- Provide both the "what" and the "why" behind astrological influences
- Offer balanced perspectives on challenging aspects
- Include practical suggestions for working with planetary energies

Remember: You are providing guidance based on Vedic astrology. Always refer to the provided birth chart context to make your responses personal and relevant."""

    def chat(self, 
             user_message: str, 
             birth_chart: BirthChartResponse,
             conversation_id: Optional[str] = None,
             user_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a chat message with astrological context.
        
        Args:
            user_message: The user's question or message
            birth_chart: The user's birth chart data for context
            conversation_id: Optional conversation ID for maintaining context
            user_name: Optional user name for personalization
            
        Returns:
            Dict containing the response and conversation metadata
        """
        
        if not self.is_available():
            return {
                'success': False,
                'error': 'Chat service is not available. Please check OpenAI API configuration.',
                'response': 'I apologize, but the chat service is currently unavailable. Please try again later.',
                'conversation_id': conversation_id
            }
        
        try:
            # Generate conversation ID if not provided
            if not conversation_id:
                conversation_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Get or create conversation history
            if conversation_id not in self.conversations:
                self.conversations[conversation_id] = {
                    'messages': [],
                    'birth_chart': birth_chart,
                    'user_name': user_name,
                    'created_at': datetime.now().isoformat()
                }
            
            conversation = self.conversations[conversation_id]
            
            # Create astrological context
            chart_context = self.create_astrological_context(birth_chart)
            
            # Build messages for OpenAI
            messages = [
                {
                    "role": "system",
                    "content": self.get_system_prompt()
                },
                {
                    "role": "system", 
                    "content": f"Birth Chart Context:\n{chart_context}"
                }
            ]
            
            # Add conversation history
            messages.extend(conversation['messages'])
            
            # Add current user message
            user_name_prefix = f"{user_name}: " if user_name else ""
            messages.append({
                "role": "user",
                "content": f"{user_name_prefix}{user_message}"
            })
            
            # Call OpenAI ChatGPT
            response = self.client.chat.completions.create(
                model="gpt-4",  # Use GPT-4 for better astrological reasoning
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            # Extract response
            assistant_response = response.choices[0].message.content
            
            # Update conversation history
            conversation['messages'].append({
                "role": "user",
                "content": f"{user_name_prefix}{user_message}"
            })
            conversation['messages'].append({
                "role": "assistant", 
                "content": assistant_response
            })
            
            # Limit conversation history (keep last 20 messages)
            if len(conversation['messages']) > 20:
                conversation['messages'] = conversation['messages'][-20:]
            
            # Calculate token usage
            total_tokens = response.usage.total_tokens
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            
            return {
                'success': True,
                'response': assistant_response,
                'conversation_id': conversation_id,
                'user_message': user_message,
                'timestamp': datetime.now().isoformat(),
                'usage': {
                    'total_tokens': total_tokens,
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens
                },
                'metadata': {
                    'model': 'gpt-4',
                    'user_name': user_name,
                    'message_count': len(conversation['messages'])
                }
            }
            
        except Exception as e:
            error_message = f"Chat processing error: {str(e)}"
            print(f"❌ {error_message}")
            
            return {
                'success': False,
                'error': error_message,
                'response': 'I apologize, but I encountered an error while processing your question. Please try again.',
                'conversation_id': conversation_id,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_conversation_history(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation history for a given conversation ID."""
        return self.conversations.get(conversation_id)
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """Clear a specific conversation."""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            return True
        return False
    
    def get_active_conversations(self) -> List[str]:
        """Get list of active conversation IDs."""
        return list(self.conversations.keys())
    
    def get_suggested_questions(self, birth_chart: BirthChartResponse) -> List[str]:
        """Generate suggested questions based on birth chart."""
        
        suggestions = []
        
        # General suggestions
        suggestions.extend([
            "What does my birth chart reveal about my personality?",
            "What are my key strengths and challenges?",
            "How can I best use my planetary energies?",
        ])
        
        # Chart-specific suggestions
        if birth_chart.chart_summary:
            summary = birth_chart.chart_summary
            
            # Sun sign specific
            sun_sign = summary.get('sun_sign')
            if sun_sign:
                suggestions.append(f"How does my {sun_sign} Sun influence my life purpose?")
            
            # Moon sign specific  
            moon_sign = summary.get('moon_sign')
            if moon_sign:
                suggestions.append(f"What does my {moon_sign} Moon say about my emotional nature?")
            
            # Dominant elements
            dominant_sign = summary.get('dominant_sign')
            if dominant_sign:
                suggestions.append(f"How can I balance my strong {dominant_sign} energy?")
        
        # Retrograde planets
        retrograde_planets = [p for p in birth_chart.planets if p.retrograde]
        if retrograde_planets:
            planet_names = [p.planet for p in retrograde_planets[:2]]
            suggestions.append(f"How do my retrograde planets ({', '.join(planet_names)}) affect me?")
        
        # Career and relationships
        suggestions.extend([
            "What career paths suit my astrological makeup?",
            "How can I improve my relationships based on my chart?",
            "What spiritual practices would benefit me most?",
            "When might be good timing for major life decisions?"
        ])
        
        return suggestions[:8]  # Return top 8 suggestions


# Global chat service instance
chat_service = AstrologyChatService() 