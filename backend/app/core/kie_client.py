import asyncio
import uuid
from typing import Dict, Any, List

async def generate_roadmap_mock(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mock function to simulate calling the KIE Planning Engine to generate a roadmap.
    In reality, this would make an HTTP request to the KIE service.
    """
    await asyncio.sleep(1)  # Simulate network delay
    
    degree = user_profile.get("degree_program", "Computer Science")
    
    # Return a mocked structured roadmap
    return {
        "title": f"Semester Plan: {degree}",
        "type": "semester",
        "goals": [
            {
                "title": "Master Core Algorithms",
                "type": "monthly",
                "description": "Understand sorting and graph algorithms deeply.",
                "missions": [
                    {
                        "title": "Implement QuickSort",
                        "type": "practical",
                        "content": "Write a Python implementation of QuickSort and test it.",
                        "xp_reward": 50
                    },
                    {
                        "title": "Algorithm Theory Quiz",
                        "type": "revision",
                        "content": "Review Big O notation for all basic sorting algorithms.",
                        "xp_reward": 20
                    }
                ]
            },
            {
                "title": "Complete First Project",
                "type": "weekly",
                "description": "Build a basic API using FastAPI.",
                "missions": [
                    {
                        "title": "Setup FastAPI Server",
                        "type": "assignment",
                        "content": "Initialize app and create a /health endpoint.",
                        "xp_reward": 30
                    }
                ]
            }
        ]
    }


async def process_memory_context_mock(conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Mock function to simulate calling the KIE Memory Engine to extract context and update history.
    """
    await asyncio.sleep(1)  # Simulate network delay
    
    # Analyze conversation (dummy logic)
    topics_mentioned = [msg["content"] for msg in conversation_history if "python" in msg["content"].lower()]
    
    updates = []
    if topics_mentioned:
        updates.append({
            "type": "learning_history",
            "data": {
                "topic": "Python Basics",
                "mastery_level": 1
            }
        })
        
    return {
        "status": "success",
        "extracted_updates": updates
    }
