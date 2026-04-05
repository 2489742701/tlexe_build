"""测试运行脚本。

运行所有自动化测试并生成报告。

使用方式:
    python -m tests.run_tests
"""

import sys
import os
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tests import TestLogger
from tests.test_flow import TestFlow
from tests.test_project import TestProject
from tests.test_state_machine import TestStateMachineView


def run_all_tests():
    """运行所有测试。"""
    logger = TestLogger()
    
    print("\n" + "=" * 60)
    print("自动化测试框架")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestProject))
    suite.addTests(loader.loadTestsFromTestCase(TestStateMachineView))
    suite.addTests(loader.loadTestsFromTestCase(TestFlow))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print(f"运行: {result.testsRun} 个测试")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)} 个")
    print(f"失败: {len(result.failures)} 个")
    print(f"错误: {len(result.errors)} 个")
    print("=" * 60 + "\n")
    
    if result.failures:
        print("失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}")
        print()
    
    if result.errors:
        print("出错的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}")
        print()
    
    report = logger.generate_report()
    print(report)
    
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
