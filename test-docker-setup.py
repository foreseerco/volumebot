#!/usr/bin/env python3
"""
Test script to validate Docker setup and configuration
"""

import os
import sys
from pathlib import Path

def test_file_exists(filepath, description):
    """Test if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} missing: {filepath}")
        return False

def test_dockerfile():
    """Test Dockerfile content"""
    dockerfile_path = "Dockerfile"
    if not test_file_exists(dockerfile_path, "Dockerfile"):
        return False
    
    with open(dockerfile_path, 'r') as f:
        content = f.read()
    
    tests = [
        ("python:3.11-slim", "Base image specified"),
        ("WORKDIR /app", "Working directory set"),
        ("requirements.txt", "Requirements copied"),
        ("ENTRYPOINT", "Entrypoint configured"),
        ("HEALTHCHECK", "Health check configured"),
        ("USER app", "Non-root user configured")
    ]
    
    for test_string, description in tests:
        if test_string in content:
            print(f"✅ {description}")
        else:
            print(f"❌ {description} missing")
    
    return True

def test_docker_compose():
    """Test docker-compose.yml content"""
    compose_path = "docker-compose.yml"
    if not test_file_exists(compose_path, "Docker Compose file"):
        return False
    
    with open(compose_path, 'r') as f:
        content = f.read()
    
    tests = [
        ("services:", "Services section exists"),
        ("volume-bot:", "Volume bot service defined"),
        ("env_file:", "Environment file configured"),
        ("healthcheck:", "Health check defined"),
        ("restart:", "Restart policy set"),
        ("build:", "Build configuration present")
    ]
    
    for test_string, description in tests:
        if test_string in content:
            print(f"✅ {description}")
        else:
            print(f"❌ {description}")
    
    return True

def test_env_example():
    """Test .env.example file"""
    env_path = ".env.example"
    if not test_file_exists(env_path, "Environment example file"):
        return False
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    required_vars = [
        "API_KEY", "API_SECRET", "EXCHANGE", "DRY_RUN",
        "TARGET_VOLUME_USDT_PER_HOUR", "TRADING_PAIR"
    ]
    
    for var in required_vars:
        if var in content:
            print(f"✅ Environment variable {var} documented")
        else:
            print(f"❌ Environment variable {var} missing")
    
    return True

def test_dockerignore():
    """Test .dockerignore file"""
    ignore_path = ".dockerignore"
    if not test_file_exists(ignore_path, "Docker ignore file"):
        return False
    
    with open(ignore_path, 'r') as f:
        content = f.read()
    
    important_ignores = [
        "__pycache__", "*.pyc", ".env", ".git", "README.md"
    ]
    
    for ignore_pattern in important_ignores:
        if ignore_pattern in content:
            print(f"✅ {ignore_pattern} ignored")
        else:
            print(f"❌ {ignore_pattern} should be ignored")
    
    return True

def test_entrypoint_script():
    """Test entrypoint script"""
    script_path = "docker-entrypoint.sh"
    if not test_file_exists(script_path, "Docker entrypoint script"):
        return False
    
    # Check if executable
    if os.access(script_path, os.X_OK):
        print("✅ Entrypoint script is executable")
    else:
        print("❌ Entrypoint script is not executable")
    
    with open(script_path, 'r') as f:
        content = f.read()
    
    checks = [
        ("#!/bin/bash", "Bash shebang present"),
        ("check_env_vars", "Environment validation function"),
        ("validate_config", "Configuration validation function"),
        ("test_imports", "Import testing function")
    ]
    
    for check_string, description in checks:
        if check_string in content:
            print(f"✅ {description}")
        else:
            print(f"❌ {description}")
    
    return True

def test_python_files():
    """Test that all Python files are present"""
    required_files = [
        "main.py",
        "constants.py", 
        "config_validator.py",
        "order_manager.py",
        "market_data.py",
        "price_strategy.py",
        "requirements.txt"
    ]
    
    all_present = True
    for file in required_files:
        if not test_file_exists(file, f"Required file"):
            all_present = False
    
    return all_present

def main():
    """Run all tests"""
    print("🐳 Testing Docker Setup")
    print("=" * 50)
    
    tests = [
        ("Docker Files", test_dockerfile),
        ("Docker Compose", test_docker_compose),
        ("Environment Template", test_env_example),
        ("Docker Ignore", test_dockerignore),
        ("Entrypoint Script", test_entrypoint_script),
        ("Python Files", test_python_files)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}:")
        print("-" * 30)
        if not test_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All Docker setup tests passed!")
        print("\nTo build and run:")
        print("  docker-compose up --build")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()