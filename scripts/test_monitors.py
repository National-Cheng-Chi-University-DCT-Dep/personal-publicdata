#!/usr/bin/env python3
"""
測試所有監控腳本
用於本地測試監控系統是否正常運作
"""

import sys
from pathlib import Path

# 加入專案路徑
sys.path.append(str(Path(__file__).parent.parent))

from monitoring.pre_application.check_opening_status import ApplicationOpeningMonitor
from monitoring.post_application.check_status_sweden import SwedenApplicationMonitor
from monitoring.post_application.check_status_dreamapply import DreamApplyMonitor
from monitoring.post_application.check_status_saarland import SaarlandMonitor


def print_header(title: str) -> None:
    """列印標題"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def test_pre_application_monitor() -> bool:
    """測試 Pre-Application 監控"""
    print_header("測試 Pre-Application Monitor")
    
    try:
        monitor = ApplicationOpeningMonitor()
        success = monitor.run()
        
        if success:
            print("✅ Pre-Application 監控測試成功")
            return True
        else:
            print("❌ Pre-Application 監控測試失敗")
            return False
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return False


def test_sweden_monitor() -> bool:
    """測試瑞典監控"""
    print_header("測試 Sweden Application Monitor")
    
    try:
        monitor = SwedenApplicationMonitor()
        success = monitor.run()
        
        if success:
            print("✅ 瑞典監控測試成功")
            return True
        else:
            print("❌ 瑞典監控測試失敗")
            return False
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return False


def test_dreamapply_monitor() -> bool:
    """測試 DreamApply 監控"""
    print_header("測試 DreamApply Monitor")
    
    try:
        monitor = DreamApplyMonitor()
        success = monitor.run()
        
        if success:
            print("✅ DreamApply 監控測試成功")
            return True
        else:
            print("❌ DreamApply 監控測試失敗")
            return False
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return False


def test_saarland_monitor() -> bool:
    """測試薩爾蘭監控"""
    print_header("測試 Saarland University Monitor")
    
    try:
        monitor = SaarlandMonitor()
        success = monitor.run()
        
        if success:
            print("✅ 薩爾蘭監控測試成功")
            return True
        else:
            print("❌ 薩爾蘭監控測試失敗")
            return False
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return False


def main():
    """主函式"""
    print("""
╔══════════════════════════════════════════════════════════╗
║         監控系統測試工具                                ║
║         Monitor System Testing Tool                     ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    print("選擇要測試的監控器：")
    print("1. Pre-Application Monitor（申請開放監控）")
    print("2. Sweden Application Monitor（瑞典申請進度）")
    print("3. DreamApply Monitor（DreamApply 申請進度）")
    print("4. Saarland Monitor（薩爾蘭大學申請進度）")
    print("5. 測試全部")
    print("0. 退出")
    
    choice = input("\n請輸入選項（0-5）: ").strip()
    
    results = {}
    
    if choice == '1':
        results['Pre-Application'] = test_pre_application_monitor()
    elif choice == '2':
        results['Sweden'] = test_sweden_monitor()
    elif choice == '3':
        results['DreamApply'] = test_dreamapply_monitor()
    elif choice == '4':
        results['Saarland'] = test_saarland_monitor()
    elif choice == '5':
        print("\n🚀 開始測試所有監控器...\n")
        results['Pre-Application'] = test_pre_application_monitor()
        results['Sweden'] = test_sweden_monitor()
        results['DreamApply'] = test_dreamapply_monitor()
        results['Saarland'] = test_saarland_monitor()
    elif choice == '0':
        print("退出測試")
        return
    else:
        print("❌ 無效的選項")
        return
    
    # 顯示測試結果總覽
    print_header("測試結果總覽")
    
    total = len(results)
    passed = sum(1 for success in results.values() if success)
    
    for name, success in results.items():
        status = "✅ 通過" if success else "❌ 失敗"
        print(f"{name:20} {status}")
    
    print(f"\n總計: {passed}/{total} 測試通過")
    
    if passed == total:
        print("\n🎉 所有測試都通過了！")
    else:
        print(f"\n⚠️ 有 {total - passed} 個測試失敗")
        print("請檢查日誌檔案: logs/monitor.log")
        print("請檢查截圖: logs/screenshots/")


if __name__ == '__main__':
    main()

