#!/usr/bin/env python3
"""
Comprehensive Test Runner
Executes all tests and evaluations in the system
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    
    try:
        # For evaluation scripts, run without capturing output to avoid encoding issues
        if "evaluacion_automatica" in cmd or "demo_modular_integration" in cmd:
            result = subprocess.run(cmd, shell=True)
        else:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            
        if result.returncode == 0:
            print(f"PASSED: {description}")
            return True
        else:
            print(f"FAILED: {description} (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"ERROR: {description} - {e}")
        return False

def main():
    """Main test runner"""
    print("Starting Comprehensive Test Suite")
    print(f"Working directory: {os.getcwd()}")
    
    # Test categories and commands
    test_suite = [
        # Unit Tests
        ("python -m pytest tests/unit/ -v --tb=short", "Unit Tests"),
        
        # Integration Tests
        ("python -m pytest tests/integration/ -v --tb=short", "Integration Tests (pytest)"),
        ("python -m pytest tests/integration/test_groq_simple.py -v", "Groq API Test"),
        ("python -m pytest tests/integration/test_deepsearch_integration.py -v", "DeepSearch Integration"),
        ("python -m pytest tests/integration/test_model_manager.py -v", "Model Manager Test"),
        ("python -m pytest tests/integration/test_competition.py -v", "Competition Test"),
        
        # System Evaluations (direct execution)
        ("python tests/evaluacion_automatica.py", "Automatic Evaluation"),
        ("python scripts/demo_modular_integration.py", "Modular Integration Demo"),
        ("python -m pytest tests/integration/test_competition.py -v --tb=short", "Competition Test Enhanced"),
        
        # All tests combined
        ("python -m pytest tests/ -v --tb=short", "All pytest Tests Combined"),
    ]
    
    results = []
    start_time = time.time()
    
    for cmd, description in test_suite:
        success = run_command(cmd, description)
        results.append((description, success))
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "="*80)
    print(" TEST SUITE SUMMARY ")
    print("="*80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for description, success in results:
        status = "PASSED" if success else "ERROR"
        print(f" {description:<40} {status} ")
    
    print("\n" + "="*80)
    
    if passed == total:
        print("All tests passed! System is ready.")
        return 0
    else:
        print(f"WARNING: {total - passed} tests failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())