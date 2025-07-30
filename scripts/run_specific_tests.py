#!/usr/bin/env python3
"""
Specific Test Runner for Telegram AI Bot

This script allows running specific test categories or individual tests.
"""
import sys
import subprocess
import argparse
from pathlib import Path

def run_test_category(category, verbose=False):
    """Run a specific test category"""
    test_commands = {
        'unit': 'python -m pytest tests/unit/ -v',
        'integration': 'python -m pytest tests/integration/ -v',
        'e2e': 'python tests/test_bot_e2e.py',
        'performance': 'python tests/test_performance.py',
        'all': 'python run_tests.py',
        'coverage': 'python -m pytest tests/ --cov=telegram_ai_bot --cov-report=html',
        'quick': 'python -m pytest tests/unit/ -x',  # Stop on first failure
    }
    
    if category not in test_commands:
        print(f"❌ Unknown test category: {category}")
        print(f"Available categories: {', '.join(test_commands.keys())}")
        return False
    
    command = test_commands[category]
    if verbose and 'pytest' in command:
        command += ' -v'
    
    print(f"🔍 Running {category} tests...")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        return False

def run_specific_test(test_path, verbose=False):
    """Run a specific test file"""
    test_file = Path(test_path)
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_path}")
        return False
    
    command = f"python -m pytest {test_path}"
    if verbose:
        command += " -v"
    
    print(f"🔍 Running specific test: {test_path}")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Run specific tests for Telegram AI Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_specific_tests.py unit              # Run unit tests
  python scripts/run_specific_tests.py integration      # Run integration tests
  python scripts/run_specific_tests.py e2e              # Run end-to-end tests
  python scripts/run_specific_tests.py performance      # Run performance tests
  python scripts/run_specific_tests.py coverage         # Run with coverage
  python scripts/run_specific_tests.py all              # Run all tests
  python scripts/run_specific_tests.py --file tests/unit/test_user_manager.py
        """
    )
    
    parser.add_argument(
        'category',
        nargs='?',
        help='Test category to run (unit, integration, e2e, performance, coverage, all, quick)'
    )
    
    parser.add_argument(
        '--file', '-f',
        help='Run specific test file'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List available test categories'
    )
    
    args = parser.parse_args()
    
    if args.list:
        print("📋 Available test categories:")
        print("  unit         - Unit tests for individual components")
        print("  integration  - Integration tests for component interaction")
        print("  e2e          - End-to-end tests for full workflows")
        print("  performance  - Performance and load tests")
        print("  coverage     - All tests with coverage report")
        print("  all          - Complete test suite")
        print("  quick        - Unit tests only, stop on first failure")
        print("\n📁 Example test files:")
        for test_file in Path('tests').rglob('test_*.py'):
            print(f"  {test_file}")
        return 0
    
    # Set up environment
    sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
    
    success = False
    
    if args.file:
        success = run_specific_test(args.file, args.verbose)
    elif args.category:
        success = run_test_category(args.category, args.verbose)
    else:
        parser.print_help()
        return 1
    
    return 0 if success else 1

if __name__ == "__main__":
    # Handle Python 3.13 compatibility
    if sys.version_info >= (3, 13):
        import warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    exit_code = main()
    sys.exit(exit_code)