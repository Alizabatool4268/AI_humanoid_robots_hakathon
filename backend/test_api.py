#!/usr/bin/env python3
"""
Test script to query the running FastAPI server
"""

import requests
import json

def test_query():
    """Test the multi-agent system with a query via the API"""
    url = "http://127.0.0.1:8000/api/agent/query"

    # Create a query payload
    payload = {
        "query": "what is the book about",
        "selected_text": None,
        "user_context": None
    }

    print("Sending query to the API: 'what is the book about'")

    try:
        response = requests.post(url, json=payload)

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

        return response.json()
    except Exception as e:
        print(f"Error making request: {e}")
        return None

def test_health():
    """Test the health endpoint"""
    url = "http://127.0.0.1:8000/api/agent/health"

    print("\nTesting health endpoint...")

    try:
        response = requests.get(url)

        print(f"Health Status Code: {response.status_code}")
        print(f"Health Response: {response.json()}")

        return response.json()
    except Exception as e:
        print(f"Error making health request: {e}")
        return None

if __name__ == "__main__":
    print("Testing the Book RAG Chatbot API...")

    # Test health first
    test_health()

    # Test the main query endpoint
    test_query()