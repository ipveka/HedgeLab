#!/usr/bin/env python3
"""
HedgeLab Test Runner
Runs all tests and generates comprehensive reports
"""

import sys
import os
import time
import subprocess
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.append('../src')

def run_test_file(test_file: str, description: str) -> dict:
    """Run a single test file and return results"""
    print(f"\n🧪 Running {description}...")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Run the test file
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        duration = time.time() - start_time
        
        # Parse output for test results
        output = result.stdout
        error_output = result.stderr
        
        # Look for test summary in output
        test_passed = 0
        test_failed = 0
        
        for line in output.split('\n'):
            if "tests passed" in line:
                # Extract numbers from lines like "📊 Test Results: 17/20 tests passed"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "tests" and i > 0:
                        try:
                            passed_total = parts[i-1].split('/')
                            test_passed = int(passed_total[0])
                            test_failed = int(passed_total[1]) - test_passed
                            break
                        except (ValueError, IndexError):
                            pass
        
        return {
            'file': test_file,
            'description': description,
            'success': result.returncode == 0,
            'duration': duration,
            'test_passed': test_passed,
            'test_failed': test_failed,
            'output': output,
            'error': error_output,
            'return_code': result.returncode
        }
        
    except Exception as e:
        duration = time.time() - start_time
        return {
            'file': test_file,
            'description': description,
            'success': False,
            'duration': duration,
            'test_passed': 0,
            'test_failed': 0,
            'output': '',
            'error': str(e),
            'return_code': -1
        }

def generate_test_report(results: list):
    """Generate a comprehensive test report"""
    print("\n" + "=" * 80)
    print("📊 HEDGELAB COMPREHENSIVE TEST REPORT")
    print("=" * 80)
    
    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_duration = 0
    
    # Summary table
    print(f"\n{'Test File':<25} {'Status':<10} {'Passed':<8} {'Failed':<8} {'Duration':<10}")
    print("-" * 70)
    
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        duration_str = f"{result['duration']:.2f}s"
        
        print(f"{result['description']:<25} {status:<10} {result['test_passed']:<8} {result['test_failed']:<8} {duration_str:<10}")
        
        total_tests += result['test_passed'] + result['test_failed']
        total_passed += result['test_passed']
        total_failed += result['test_failed']
        total_duration += result['duration']
    
    # Overall summary
    print("\n" + "=" * 70)
    print(f"📊 OVERALL SUMMARY")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {total_passed}")
    print(f"   Failed: {total_failed}")
    print(f"   Success Rate: {(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "   Success Rate: 0%")
    print(f"   Total Duration: {total_duration:.2f}s")
    
    # Detailed results
    print(f"\n📋 DETAILED RESULTS")
    for result in results:
        print(f"\n🔍 {result['description']}")
        print(f"   Status: {'✅ PASSED' if result['success'] else '❌ FAILED'}")
        print(f"   Duration: {result['duration']:.2f}s")
        print(f"   Tests: {result['test_passed']} passed, {result['test_failed']} failed")
        
        if result['error']:
            print(f"   Error: {result['error'][:200]}...")
    
    # Recommendations
    print(f"\n🎯 RECOMMENDATIONS")
    if total_failed == 0:
        print("🎉 All tests passed! HedgeLab is fully functional.")
    elif total_passed >= total_tests * 0.8:
        print("✅ Most tests passed. HedgeLab is ready for use with minor limitations.")
    else:
        print("⚠️ Several tests failed. Some features may not work as expected.")
    
    print(f"\n📋 Next Steps:")
    print("1. Check the logs folder for detailed error information")
    print("2. Review API rate limiting issues in api_calls logs")
    print("3. Start the application: python run.py")
    print("4. Access HedgeLab at: http://localhost:8501")

def main():
    """Run all HedgeLab tests"""
    print("🚀 HEDGELAB TEST RUNNER")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Define test files
    test_files = [
        ("test_app.py", "Basic Functionality Tests"),
        ("comprehensive_test.py", "Comprehensive Feature Tests"),
        ("final_demo.py", "Feature Demo Tests")
    ]
    
    results = []
    
    # Run each test file
    for test_file, description in test_files:
        if os.path.exists(test_file):
            result = run_test_file(test_file, description)
            results.append(result)
        else:
            print(f"⚠️ Test file not found: {test_file}")
    
    # Generate report
    generate_test_report(results)
    
    # Save report to file
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write("HEDGELAB TEST REPORT\n")
        f.write("=" * 50 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for result in results:
            f.write(f"{result['description']}\n")
            f.write(f"Status: {'PASSED' if result['success'] else 'FAILED'}\n")
            f.write(f"Tests: {result['test_passed']} passed, {result['test_failed']} failed\n")
            f.write(f"Duration: {result['duration']:.2f}s\n")
            if result['error']:
                f.write(f"Error: {result['error']}\n")
            f.write("\n")
    
    print(f"\n📄 Detailed report saved to: {report_file}")

if __name__ == "__main__":
    main() 