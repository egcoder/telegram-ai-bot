#!/usr/bin/env python3
"""
Comprehensive Test Runner for Telegram AI Bot

This script runs all tests in the correct order and provides a unified test report.
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"🔍 {description}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(result.stdout)
            print(f"✅ {description} completed successfully in {duration:.2f}s")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            print(result.stdout)
            print(f"Duration: {duration:.2f}s")
            return False
            
    except Exception as e:
        duration = time.time() - start_time
        print(f"❌ {description} failed with exception: {e}")
        print(f"Duration: {duration:.2f}s")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        ('pytest', 'pytest'),
        ('python-telegram-bot', 'telegram'),
        ('openai', 'openai'),
        ('aiohttp', 'aiohttp'),
        ('python-dotenv', 'dotenv')
    ]
    
    missing = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"  ✅ {package_name}")
        except ImportError:
            print(f"  ❌ {package_name} (missing)")
            missing.append(package_name)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False
    
    print("✅ All dependencies available")
    return True

def setup_test_environment():
    """Set up test environment"""
    print("🔧 Setting up test environment...")
    
    # Ensure test directories exist
    test_dirs = ['tests/unit', 'tests/integration', 'data', 'logs']
    for dir_path in test_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Set test environment variables
    os.environ.update({
        'TELEGRAM_BOT_TOKEN': '123456789:test_token_for_testing_only',
        'OPENAI_API_KEY': 'sk-test-key-for-testing-only',
        'ADMIN_USER_ID': '123456789',
        'LOG_LEVEL': 'WARNING'  # Reduce log noise during tests
    })
    
    print("✅ Test environment ready")
    return True

def main():
    """Main test execution"""
    print("🚀 Telegram AI Bot - Comprehensive Test Suite")
    print("=" * 60)
    
    # Track test results
    results = []
    start_time = time.time()
    
    # 1. Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed")
        return 1
    
    # 2. Set up environment
    if not setup_test_environment():
        print("❌ Environment setup failed")
        return 1
    
    # 3. Run environment validation
    success = run_command(
        "python scripts/test_setup.py",
        "Environment Validation"
    )
    results.append(("Environment Validation", success))
    
    # 4. Run unit tests
    success = run_command(
        "python -m pytest tests/unit/ -v --tb=short",
        "Unit Tests"
    )
    results.append(("Unit Tests", success))
    
    # 5. Run integration tests
    success = run_command(
        "python -m pytest tests/integration/ -v --tb=short",
        "Integration Tests"
    )
    results.append(("Integration Tests", success))
    
    # 6. Run end-to-end tests
    success = run_command(
        "python tests/test_bot_e2e.py",
        "End-to-End Tests"
    )
    results.append(("End-to-End Tests", success))
    
    # 7. Run performance tests
    success = run_command(
        "python tests/test_performance.py",
        "Performance Tests"
    )
    results.append(("Performance Tests", success))
    
    # 8. Generate coverage report (if pytest-cov is available)
    try:
        import pytest_cov
        success = run_command(
            "python -m pytest tests/ --cov=telegram_ai_bot --cov-report=term-missing --cov-report=html",
            "Coverage Report"
        )
        results.append(("Coverage Report", success))
    except ImportError:
        print("ℹ️  pytest-cov not available, skipping coverage report")
    
    # Print final results
    total_time = time.time() - start_time
    print_final_report(results, total_time)
    
    # Return appropriate exit code
    failed_tests = [name for name, success in results if not success]
    return 0 if not failed_tests else 1

def print_final_report(results, total_time):
    """Print comprehensive test report"""
    print("\n" + "="*70)
    print("📊 COMPREHENSIVE TEST REPORT")
    print("="*70)
    
    passed = 0
    failed = 0
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:<12} {test_name}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print("="*70)
    print(f"📈 SUMMARY:")
    print(f"  Total Tests: {len(results)}")
    print(f"  Passed:      {passed}")
    print(f"  Failed:      {failed}")
    print(f"  Duration:    {total_time:.2f}s")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Your Telegram AI Bot is ready for deployment!")
        print("\n📋 Next Steps:")
        print("  1. Install FFmpeg: brew install ffmpeg")
        print("  2. Set up real API keys in .env")
        print("  3. Run: python main.py")
        print("  4. Test with real Telegram messages")
    else:
        failed_test_names = [name for name, success in results if not success]
        print(f"\n⚠️  {failed} test(s) failed:")
        for name in failed_test_names:
            print(f"  - {name}")
        print("\nPlease fix the failing tests before deployment.")
    
    print("="*70)
    
    # Additional information
    print("\n📁 Test Artifacts:")
    if Path("htmlcov").exists():
        print("  📊 Coverage report: open htmlcov/index.html")
    if Path("logs").exists():
        print("  📋 Log files: logs/")
    
    print("\n🔧 Useful Commands:")
    print("  Run specific test:     python -m pytest tests/unit/test_user_manager.py")
    print("  Run with coverage:     python -m pytest --cov=telegram_ai_bot")
    print("  Run performance only:  python tests/test_performance.py")
    print("  Run e2e only:         python tests/test_bot_e2e.py")

if __name__ == "__main__":
    # Handle Python 3.13 compatibility
    if sys.version_info >= (3, 13):
        import warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    # Add src to Python path
    sys.path.insert(0, str(Path(__file__).parent / 'src'))
    
    exit_code = main()
    sys.exit(exit_code)