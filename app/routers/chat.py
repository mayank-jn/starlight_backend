"""
Chat Router for Astrological Consultations
Provides endpoints for interactive chat with AI astrologer
"""

from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from typing import Optional, List
import logging
from datetime import datetime

from app.models import (
    ChatRequest, ChatResponse, ConversationHistoryResponse, SuggestedQuestionsResponse,
    BirthChartRequest, ErrorResponse, HouseSystem, AyanamsaSystem, ChatMessage
)
from app.services.chat_service import chat_service
from app.services.birth_chart import birth_chart_service

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/chat", response_model=ChatResponse)
async def chat_with_astrologer(request: ChatRequest):
    """
    Chat with an AI astrologer using your birth chart as context.
    
    This endpoint provides personalized astrological guidance by:
    - Using your birth chart data as context for responses
    - Maintaining conversation history for coherent discussions
    - Providing expert Vedic astrology insights
    - Offering practical guidance and recommendations
    
    The AI astrologer is trained in Vedic astrology principles and will reference
    your specific planetary positions, houses, and aspects in its responses.
    """
    try:
        logger.info(f"Processing chat message: '{request.message}' for birth chart {request.birth_date}")
        
        # Check if chat service is available
        if not chat_service.is_available():
            raise HTTPException(
                status_code=503, 
                detail="Chat service is currently unavailable. Please check OpenAI API configuration."
            )
        
        # Generate birth chart for context
        birth_chart_request = BirthChartRequest(
            name=request.user_name,
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone=request.timezone,
            house_system=request.house_system,
            ayanamsa=request.ayanamsa
        )
        
        birth_chart = birth_chart_service.generate_birth_chart(birth_chart_request)
        
        # Process chat message
        chat_response = chat_service.chat(
            user_message=request.message,
            birth_chart=birth_chart,
            conversation_id=request.conversation_id,
            user_name=request.user_name
        )
        
        if not chat_response['success']:
            raise HTTPException(status_code=500, detail=chat_response.get('error', 'Chat processing failed'))
        
        # Convert to response model
        response = ChatResponse(
            success=chat_response['success'],
            response=chat_response['response'],
            conversation_id=chat_response['conversation_id'],
            user_message=chat_response['user_message'],
            timestamp=datetime.fromisoformat(chat_response['timestamp']),
            usage=chat_response.get('usage'),
            metadata=chat_response.get('metadata')
        )
        
        logger.info(f"Chat response generated successfully for conversation {response.conversation_id}")
        return response
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during chat processing")

@router.get("/conversations/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(conversation_id: str):
    """
    Get the conversation history for a specific conversation.
    
    Returns all messages in the conversation along with metadata
    about the associated birth chart and user information.
    """
    try:
        conversation = chat_service.get_conversation_history(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail=f"Conversation '{conversation_id}' not found")
        
        # Convert messages to ChatMessage format
        messages = []
        for msg in conversation['messages']:
            messages.append(ChatMessage(
                role=msg['role'],
                content=msg['content'],
                timestamp=datetime.now()  # Simplified for now
            ))
        
        # Create birth chart summary
        birth_chart = conversation['birth_chart']
        birth_chart_summary = {
            'birth_datetime': birth_chart.birth_datetime,
            'location': birth_chart.location,
            'sun_sign': birth_chart.chart_summary.get('sun_sign') if birth_chart.chart_summary else None,
            'moon_sign': birth_chart.chart_summary.get('moon_sign') if birth_chart.chart_summary else None,
            'ascendant_sign': birth_chart.chart_summary.get('ascendant_sign') if birth_chart.chart_summary else None
        }
        
        response = ConversationHistoryResponse(
            conversation_id=conversation_id,
            messages=messages,
            birth_chart_summary=birth_chart_summary,
            user_name=conversation.get('user_name'),
            created_at=datetime.fromisoformat(conversation['created_at']),
            message_count=len(messages)
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """
    Clear a specific conversation and its history.
    
    This permanently removes all messages and data associated
    with the conversation ID.
    """
    try:
        success = chat_service.clear_conversation(conversation_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Conversation '{conversation_id}' not found")
        
        return {"message": f"Conversation '{conversation_id}' cleared successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/conversations")
async def list_active_conversations():
    """
    Get a list of all active conversation IDs.
    
    Useful for debugging and understanding current chat sessions.
    """
    try:
        conversations = chat_service.get_active_conversations()
        return {
            "active_conversations": conversations,
            "count": len(conversations)
        }
    
    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/suggested-questions", response_model=SuggestedQuestionsResponse)
async def get_suggested_questions(request: BirthChartRequest):
    """
    Get personalized question suggestions based on birth chart.
    
    Analyzes the birth chart and provides relevant questions that
    the user might want to ask about their astrological influences.
    """
    try:
        logger.info(f"Generating suggested questions for birth chart {request.birth_date}")
        
        # Generate birth chart
        birth_chart = birth_chart_service.generate_birth_chart(request)
        
        # Get suggested questions
        suggestions = chat_service.get_suggested_questions(birth_chart)
        
        # Create birth chart summary for response
        birth_chart_summary = {
            'birth_datetime': birth_chart.birth_datetime,
            'location': birth_chart.location,
            'sun_sign': birth_chart.chart_summary.get('sun_sign') if birth_chart.chart_summary else None,
            'moon_sign': birth_chart.chart_summary.get('moon_sign') if birth_chart.chart_summary else None,
            'ascendant_sign': birth_chart.chart_summary.get('ascendant_sign') if birth_chart.chart_summary else None,
            'dominant_sign': birth_chart.chart_summary.get('dominant_sign') if birth_chart.chart_summary else None
        }
        
        response = SuggestedQuestionsResponse(
            questions=suggestions,
            birth_chart_summary=birth_chart_summary
        )
        
        logger.info(f"Generated {len(suggestions)} suggested questions")
        return response
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error generating suggested questions: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def chat_health_check():
    """
    Check the health status of the chat service.
    
    Returns information about OpenAI API availability and service status.
    """
    try:
        is_available = chat_service.is_available()
        
        return {
            "status": "healthy" if is_available else "limited",
            "service": "Astrological Chat Service",
            "openai_available": is_available,
            "features": [
                "Personalized Astrological Chat",
                "Birth Chart Context Integration", 
                "Conversation History",
                "Suggested Questions",
                "Vedic Astrology Expertise"
            ] if is_available else [
                "Limited functionality - OpenAI API not configured"
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")

@router.get("/status")
async def chat_service_status():
    """
    Get detailed status information about the chat service.
    
    Includes statistics about active conversations and service configuration.
    """
    try:
        active_conversations = chat_service.get_active_conversations()
        
        return {
            "service_name": "Astrological Chat Service",
            "version": "1.0.0",
            "openai_configured": chat_service.is_available(),
            "active_conversations": len(active_conversations),
            "conversation_ids": active_conversations[:5],  # Show first 5
            "features": {
                "birth_chart_context": True,
                "conversation_memory": True,
                "vedic_astrology": True,
                "personalized_responses": True,
                "suggested_questions": True
            },
            "limits": {
                "max_tokens_per_response": 1000,
                "conversation_history_limit": 20,
                "model": "gpt-4"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(status_code=500, detail="Status check failed") 