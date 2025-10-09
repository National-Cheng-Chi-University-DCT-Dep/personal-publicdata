#!/usr/bin/env python3
"""
環境設定腳本
自動設定專案所需的環境
"""

import os
import sys
import subprocess
from pathlib import Path


def print_step(step_number, description):
    """列印步驟資訊"""
    print(f"\n{'='*60}")
    print(f"步驟 {step_number}: {description}")
    print('='*60)


def run_command(command, description):
    """執行命令"""
    print(f"\n執行: {description}")
    print(f"命令: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ 成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 失敗: {e}")
        print(f"輸出: {e.output}")
        return False


def check_python_version():
    """檢查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python 版本過低: {version.major}.{version.minor}")
        print("   需要 Python 3.10 或更高版本")
        return False
    
    print(f"✅ Python 版本: {version.major}.{version.minor}.{version.micro}")
    return True


def create_directories():
    """建立必要的目錄"""
    directories = [
        'monitoring/pre_application',
        'monitoring/post_application',
        'integrations',
        'data_schemas',
        'reports/monitoring_reports',
        'reports/financial_reports',
        'reports/status_history',
        'tests/unit',
        'tests/integration',
        'tests/fixtures/mock_html',
        'tests/fixtures/mock_data',
        'scripts',
        'docs',
        'logs',
        'logs/screenshots'
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {directory}")
    
    return True


def create_env_file():
    """建立 .env 檔案"""
    if Path('.env').exists():
        print("⚠️  .env 檔案已存在，跳過建立")
        return True
    
    if Path('.env.example').exists():
        import shutil
        shutil.copy('.env.example', '.env')
        print("✅ 已從 .env.example 建立 .env 檔案")
        print("⚠️  請編輯 .env 檔案，填入您的資訊")
        return True
    
    print("❌ .env.example 不存在")
    return False


def install_dependencies():
    """安裝 Python 依賴套件"""
    if not Path('requirements.txt').exists():
        print("❌ requirements.txt 不存在")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "安裝 Python 套件"
    )


def install_playwright():
    """安裝 Playwright 瀏覽器"""
    return run_command(
        f"{sys.executable} -m playwright install chromium",
        "安裝 Playwright Chromium"
    )


def verify_installation():
    """驗證安裝"""
    print("\n驗證安裝...")
    
    # 檢查必要的套件
    required_packages = [
        'playwright',
        'yaml',
        'requests',
        'jinja2'
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} 未安裝")
            all_installed = False
    
    return all_installed


def create_gitignore_entries():
    """確保 .gitignore 包含必要的項目"""
    gitignore_entries = [
        '.env',
        'credentials.json',
        'token.pickle',
        'token.json',
        '*.log',
        '__pycache__/',
        '*.pyc',
        '.pytest_cache/',
        'logs/',
        'venv/',
        '.venv/'
    ]
    
    gitignore_path = Path('.gitignore')
    
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            existing_content = f.read()
    else:
        existing_content = ''
    
    new_entries = []
    for entry in gitignore_entries:
        if entry not in existing_content:
            new_entries.append(entry)
    
    if new_entries:
        with open(gitignore_path, 'a') as f:
            f.write('\n# 自動新增的項目\n')
            for entry in new_entries:
                f.write(f'{entry}\n')
        print(f"✅ 新增 {len(new_entries)} 個項目到 .gitignore")
    else:
        print("✅ .gitignore 已是最新")
    
    return True


def main():
    """主函式"""
    print("""
╔══════════════════════════════════════════════════════════╗
║   碩士申請管理系統 - 環境設定腳本                      ║
║   Master Application Management Platform - Setup        ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # 步驟 1: 檢查 Python 版本
    print_step(1, "檢查 Python 版本")
    if not check_python_version():
        sys.exit(1)
    
    # 步驟 2: 建立目錄結構
    print_step(2, "建立目錄結構")
    if not create_directories():
        print("❌ 建立目錄失敗")
        sys.exit(1)
    
    # 步驟 3: 建立 .env 檔案
    print_step(3, "建立環境變數檔案")
    create_env_file()
    
    # 步驟 4: 更新 .gitignore
    print_step(4, "更新 .gitignore")
    create_gitignore_entries()
    
    # 步驟 5: 安裝依賴套件
    print_step(5, "安裝 Python 依賴套件")
    if not install_dependencies():
        print("❌ 安裝依賴套件失敗")
        sys.exit(1)
    
    # 步驟 6: 安裝 Playwright
    print_step(6, "安裝 Playwright 瀏覽器")
    if not install_playwright():
        print("⚠️  Playwright 安裝失敗，請手動執行:")
        print("   python -m playwright install chromium")
    
    # 步驟 7: 驗證安裝
    print_step(7, "驗證安裝")
    if not verify_installation():
        print("⚠️  部分套件未正確安裝")
    
    # 完成
    print("\n" + "="*60)
    print("✅ 環境設定完成！")
    print("="*60)
    
    print("\n下一步:")
    print("1. 編輯 .env 檔案，填入您的帳號密碼")
    print("2. 更新 source_data/schools.yml，加入您的目標學校")
    print("3. 執行測試: python monitoring/pre_application/check_opening_status.py")
    print("4. 查看文檔: docs/")
    
    print("\n快速開始:")
    print("  python monitoring/pre_application/check_opening_status.py")
    
    print("\n參考資料:")
    print("  - 實作指南: IMPLEMENTATION_GUIDE.md")
    print("  - API 整合: docs/API_INTEGRATION.md")
    print("  - 故障排除: docs/TROUBLESHOOTING.md")
    
    print("\n")


if __name__ == '__main__':
    main()

