"""
診斷工具：檢查 Scrapers 並找出正確的 CSS Selectors
Diagnostic Tool: Check scrapers and find correct CSS selectors
"""

import asyncio
from playwright.async_api import async_playwright

async def diagnose_mastersportal():
    """診斷 Mastersportal.com"""
    print("=" * 60)
    print("🔍 診斷 Mastersportal.com")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 設為 False 可以看到瀏覽器
        page = await browser.new_page()
        
        test_url = "https://www.mastersportal.com/search/master/?q=Cybersecurity"
        
        print(f"\n📍 訪問: {test_url}")
        await page.goto(test_url, timeout=30000, wait_until='networkidle')
        await page.wait_for_timeout(5000)  # 等待頁面完全載入
        
        # 測試各種可能的 selectors
        selectors_to_test = [
            '.StudyCard',
            '.study-card',
            '[class*="CourseCard"]',
            '[class*="ProgramCard"]',
            '[class*="card"]',
            'article',
            '[data-testid*="card"]',
            '[data-testid*="program"]',
            '[data-testid*="course"]',
            '.search-result',
            '.result-item',
            '[class*="Result"]',
            'a[href*="/programmes/"]',
            'a[href*="/programs/"]',
        ]
        
        print("\n🔍 測試 CSS Selectors:")
        found_selectors = []
        
        for selector in selectors_to_test:
            try:
                elements = await page.query_selector_all(selector)
                if elements and len(elements) > 0:
                    print(f"  ✅ '{selector}' - 找到 {len(elements)} 個元素")
                    found_selectors.append((selector, len(elements)))
                else:
                    print(f"  ❌ '{selector}' - 沒有找到")
            except Exception as e:
                print(f"  ⚠️  '{selector}' - 錯誤: {e}")
        
        if found_selectors:
            print(f"\n✅ 建議使用的 selector: '{found_selectors[0][0]}'")
            
            # 分析第一個元素的結構
            print(f"\n📊 分析第一個元素的 HTML 結構:")
            try:
                first_element = await page.query_selector(found_selectors[0][0])
                if first_element:
                    # 取得 outer HTML
                    outer_html = await first_element.evaluate('el => el.outerHTML')
                    print(outer_html[:500])  # 只顯示前 500 字元
                    
                    # 列出所有子元素的 class names
                    print(f"\n📋 元素內的 classes:")
                    all_classes = await first_element.evaluate('''el => {
                        const classes = new Set();
                        el.querySelectorAll('*').forEach(child => {
                            if (child.className) {
                                child.className.split(' ').forEach(c => classes.add(c));
                            }
                        });
                        return Array.from(classes);
                    }''')
                    for cls in all_classes[:20]:  # 只顯示前 20 個
                        print(f"  - .{cls}")
            except Exception as e:
                print(f"  錯誤: {e}")
        else:
            print("\n❌ 沒有找到任何符合的元素！")
            print("\n💡 建議:")
            print("  1. 手動訪問網站並使用瀏覽器開發工具檢查")
            print("  2. 網站可能有 anti-bot 保護")
            print("  3. 考慮使用官方 API")
        
        # 保存截圖
        screenshot_path = "logs/screenshots/mastersportal_diagnosis.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"\n📸 截圖已儲存: {screenshot_path}")
        
        print("\n⏸️  按 Enter 繼續...")
        input()
        
        await browser.close()


async def diagnose_studyeu():
    """診斷 Study.eu"""
    print("\n" + "=" * 60)
    print("🔍 診斷 Study.eu")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        test_url = "https://www.study.eu/search?q=Cybersecurity&level=master"
        
        print(f"\n📍 訪問: {test_url}")
        await page.goto(test_url, timeout=30000, wait_until='networkidle')
        await page.wait_for_timeout(5000)
        
        selectors_to_test = [
            '[class*="course"]',
            '[class*="program"]',
            '[class*="result"]',
            '[class*="card"]',
            'article',
            '[data-testid*="course"]',
            '[data-testid*="program"]',
            '.search-result',
            'a[href*="/course/"]',
            'a[href*="/programme/"]',
        ]
        
        print("\n🔍 測試 CSS Selectors:")
        found_selectors = []
        
        for selector in selectors_to_test:
            try:
                elements = await page.query_selector_all(selector)
                if elements and len(elements) > 0:
                    print(f"  ✅ '{selector}' - 找到 {len(elements)} 個元素")
                    found_selectors.append((selector, len(elements)))
                else:
                    print(f"  ❌ '{selector}' - 沒有找到")
            except Exception as e:
                print(f"  ⚠️  '{selector}' - 錯誤: {e}")
        
        if found_selectors:
            print(f"\n✅ 建議使用的 selector: '{found_selectors[0][0]}'")
            
            # 分析第一個元素
            print(f"\n📊 分析第一個元素的 HTML 結構:")
            try:
                first_element = await page.query_selector(found_selectors[0][0])
                if first_element:
                    outer_html = await first_element.evaluate('el => el.outerHTML')
                    print(outer_html[:500])
                    
                    print(f"\n📋 元素內的 classes:")
                    all_classes = await first_element.evaluate('''el => {
                        const classes = new Set();
                        el.querySelectorAll('*').forEach(child => {
                            if (child.className) {
                                child.className.split(' ').forEach(c => classes.add(c));
                            }
                        });
                        return Array.from(classes);
                    }''')
                    for cls in all_classes[:20]:
                        print(f"  - .{cls}")
            except Exception as e:
                print(f"  錯誤: {e}")
        else:
            print("\n❌ 沒有找到任何符合的元素！")
        
        screenshot_path = "logs/screenshots/studyeu_diagnosis.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"\n📸 截圖已儲存: {screenshot_path}")
        
        print("\n⏸️  按 Enter 繼續...")
        input()
        
        await browser.close()


async def main():
    """主函式"""
    print("\n🔧 Scraper 診斷工具")
    print("這個工具會幫你找出正確的 CSS selectors\n")
    
    choice = input("選擇要診斷的網站 (1: Mastersportal, 2: Study.eu, 3: 兩者都診斷): ")
    
    if choice == '1' or choice == '3':
        await diagnose_mastersportal()
    
    if choice == '2' or choice == '3':
        await diagnose_studyeu()
    
    print("\n✅ 診斷完成！")
    print("\n💡 下一步:")
    print("  1. 查看儲存的截圖")
    print("  2. 根據找到的 selectors 更新 scraper")
    print("  3. 重新測試")


if __name__ == '__main__':
    asyncio.run(main())

