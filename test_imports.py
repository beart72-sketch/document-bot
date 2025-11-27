#!/usr/bin/env python3
"""Тест импортов"""
import sys
import os

# Добавляем корневую папку в путь
sys.path.insert(0, os.path.dirname(__file__))

try:
    from domain.entities.user import User
    print("✅ User imported")
    
    from domain.entities.document import Document
    print("✅ Document imported")
    
    from domain.entities.document_template import DocumentTemplate
    print("✅ DocumentTemplate imported")
    
    from domain.repositories.user_repository import UserRepository
    print("✅ UserRepository imported")
    
    print("🎉 All imports successful!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
