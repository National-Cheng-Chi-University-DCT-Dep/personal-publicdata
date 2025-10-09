"""
快速測試更新後的 Scrapers
Test Updated Scrapers
"""

import asyncio
from scrape_mastersportal import MastersPortalScraper
from scrape_studyeu import StudyEuScraper

async def test_mastersportal():
    """測試 Mastersportal Scraper"""
    print("=" * 60)
    print("🧪 測試 Mastersportal Scraper")
    print("=" * 60)
    
    scraper = MastersPortalScraper(['Cybersecurity'], ['Sweden'])
    courses = await scraper.run_async()
    
    print(f"\n✅ 找到 {len(courses)} 個課程")
    
    if courses:
        print(f"\n📚 前 3 個課程:")
        for i, course in enumerate(courses[:3], 1):
            print(f"\n{i}. {course.get('program_name', 'Unknown')}")
            print(f"   大學: {course.get('university_name', 'Unknown')}")
            print(f"   國家: {course.get('country', 'Unknown')}")
            print(f"   連結: {course.get('program_url', 'N/A')[:80]}...")
    else:
        print("\n⚠️  沒有找到課程")
        print("可能需要進一步檢查 selectors 或網站結構")
    
    return len(courses)

async def test_studyeu():
    """測試 Study.eu Scraper"""
    print("\n" + "=" * 60)
    print("🧪 測試 Study.eu Scraper")
    print("=" * 60)
    
    scraper = StudyEuScraper(['Cybersecurity'])
    courses = await scraper.run_async()
    
    print(f"\n✅ 找到 {len(courses)} 個課程")
    
    if courses:
        print(f"\n📚 前 3 個課程:")
        for i, course in enumerate(courses[:3], 1):
            print(f"\n{i}. {course.get('program_name', 'Unknown')}")
            print(f"   大學: {course.get('university_name', 'Unknown')}")
            print(f"   國家: {course.get('country', 'Unknown')}")
            print(f"   連結: {course.get('program_url', 'N/A')[:80]}...")
    else:
        print("\n⚠️  沒有找到課程")
        print("可能需要進一步調整 selectors")
    
    return len(courses)

async def main():
    """主測試函式"""
    print("\n🚀 開始測試更新後的 Scrapers\n")
    
    # 測試 Mastersportal
    mp_count = await test_mastersportal()
    
    # 測試 Study.eu
    se_count = await test_studyeu()
    
    # 總結
    print("\n" + "=" * 60)
    print("📊 測試總結")
    print("=" * 60)
    print(f"Mastersportal: {mp_count} 個課程")
    print(f"Study.eu: {se_count} 個課程")
    print(f"總計: {mp_count + se_count} 個課程")
    
    if mp_count + se_count > 0:
        print("\n✅ 測試成功！Scrapers 正常工作")
        print("\n下一步:")
        print("  1. 查看 discovery/raw_data/ 中的原始資料")
        print("  2. Commit 並 push 到 GitHub")
        print("  3. 在 Harness 重新執行 Course Discovery Pipeline")
    else:
        print("\n❌ 測試失敗：沒有找到任何課程")
        print("\n建議:")
        print("  1. 檢查 logs/screenshots/ 中的診斷截圖")
        print("  2. 手動訪問網站查看實際 HTML 結構")
        print("  3. 考慮使用替代方案（API 或手動資料）")

if __name__ == '__main__':
    asyncio.run(main())

