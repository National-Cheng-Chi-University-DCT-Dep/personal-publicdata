"""
財務規劃儀表板
Budget Analysis Dashboard

功能：
- 計算總申請成本
- 各校年度總花費比較
- 匯率轉換
- 成本排名
- 獎學金資訊整理
"""

import yaml
import sys
import logging
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class BudgetAnalyzer:
    """財務分析器"""
    
    # 固定匯率（可用 API 更新）
    DEFAULT_EXCHANGE_RATES = {
        'EUR': 33.5,   # 歐元
        'SEK': 2.9,    # 瑞典克朗
        'USD': 31.5,   # 美元
        'GBP': 38.5,   # 英鎊
        'NOK': 2.8,    # 挪威克朗
        'DKK': 4.5,    # 丹麥克朗
        'TWD': 1.0     # 台幣
    }
    
    def __init__(self, use_live_rates: bool = False):
        """
        初始化財務分析器
        
        Args:
            use_live_rates: 是否使用即時匯率
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.schools_file = 'source_data/schools.yml'
        self.dashboard_file = 'final_applications/application_dashboard.md'
        self.use_live_rates = use_live_rates
        self.exchange_rates = self.DEFAULT_EXCHANGE_RATES.copy()
        
        if use_live_rates:
            self.update_exchange_rates()
    
    def load_schools(self) -> List[Dict[str, Any]]:
        """載入學校資料"""
        try:
            with open(self.schools_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                schools = data.get('schools', [])
                self.logger.info(f"載入了 {len(schools)} 所學校")
                return schools
        except Exception as e:
            self.logger.error(f"載入學校資料失敗: {e}")
            return []
    
    def update_exchange_rates(self) -> bool:
        """
        從 API 更新即時匯率
        使用 exchangerate-api.com（免費版）
        """
        try:
            self.logger.info("正在更新即時匯率...")
            
            # 使用 exchangerate-api.com 的免費 API
            url = "https://api.exchangerate-api.com/v4/latest/TWD"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                rates = data.get('rates', {})
                
                # 將 TWD 轉換為其他貨幣的匯率
                # API 回傳的是 TWD -> 其他貨幣，我們需要反過來
                for currency in self.exchange_rates.keys():
                    if currency in rates and rates[currency] > 0:
                        # 反向匯率：其他貨幣 -> TWD
                        self.exchange_rates[currency] = 1 / rates[currency]
                
                self.logger.info("✅ 匯率更新成功")
                return True
            else:
                self.logger.warning(f"無法取得匯率，使用預設值 (HTTP {response.status_code})")
                return False
        
        except Exception as e:
            self.logger.warning(f"更新匯率失敗，使用預設值: {e}")
            return False
    
    def convert_to_twd(self, amount: float, currency: str) -> float:
        """
        轉換為台幣
        
        Args:
            amount: 金額
            currency: 貨幣代碼
            
        Returns:
            台幣金額
        """
        if currency == 'TWD':
            return amount
        
        rate = self.exchange_rates.get(currency, 1.0)
        return amount * rate
    
    def calculate_total_application_cost(self, schools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """計算總申請成本"""
        total_cost_twd = 0
        cost_breakdown = []
        
        for school in schools:
            school_name = school.get('name', 'Unknown')
            
            # 取得申請費用
            app_fee = school.get('application_fee')
            if app_fee and isinstance(app_fee, dict):
                amount = app_fee.get('amount', 0)
                currency = app_fee.get('currency', 'EUR')
                
                twd_amount = self.convert_to_twd(amount, currency)
                total_cost_twd += twd_amount
                
                cost_breakdown.append({
                    'school': school_name,
                    'amount': amount,
                    'currency': currency,
                    'twd_amount': round(twd_amount, 2),
                    'exchange_rate': self.exchange_rates.get(currency, 1.0)
                })
        
        return {
            'total_twd': round(total_cost_twd, 2),
            'breakdown': cost_breakdown,
            'total_schools': len(cost_breakdown)
        }
    
    def calculate_annual_cost(self, school: Dict[str, Any]) -> Dict[str, float]:
        """計算單一學校的年度總花費"""
        # 學費
        tuition = school.get('tuition_fee', {})
        if isinstance(tuition, dict):
            tuition_amount = tuition.get('amount', 0)
            tuition_currency = tuition.get('currency', 'EUR')
        else:
            tuition_amount = 0
            tuition_currency = 'EUR'
        
        # 生活費
        living_cost = school.get('estimated_living_cost', {})
        if isinstance(living_cost, dict):
            living_amount = living_cost.get('amount', 0)
            living_currency = living_cost.get('currency', 'EUR')
            living_period = living_cost.get('period', 'monthly')
            
            # 如果是月費，乘以 12
            if living_period == 'monthly':
                living_amount = living_amount * 12
        else:
            living_amount = 0
            living_currency = 'EUR'
        
        # 轉換為台幣
        tuition_twd = self.convert_to_twd(tuition_amount, tuition_currency)
        living_twd = self.convert_to_twd(living_amount, living_currency)
        total_twd = tuition_twd + living_twd
        
        return {
            'tuition_twd': round(tuition_twd, 2),
            'living_twd': round(living_twd, 2),
            'total_twd': round(total_twd, 2)
        }
    
    def generate_cost_comparison(self, schools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成成本比較表"""
        comparisons = []
        
        for school in schools:
            school_name = school.get('name', 'Unknown')
            country = school.get('country', 'Unknown')
            
            # 計算年度成本
            annual_costs = self.calculate_annual_cost(school)
            
            # 獎學金資訊
            has_scholarship = school.get('scholarship_available', False)
            scholarship_details = school.get('scholarship_details', '')
            
            # 免學費
            tuition_free = school.get('tuition_free', False)
            
            comparison = {
                'school': school_name,
                'country': country,
                'tuition_twd': annual_costs['tuition_twd'],
                'living_twd': annual_costs['living_twd'],
                'total_annual_twd': annual_costs['total_twd'],
                'tuition_free': tuition_free,
                'scholarship_available': has_scholarship,
                'scholarship_details': scholarship_details,
                'priority': school.get('priority', 'medium')
            }
            
            comparisons.append(comparison)
        
        # 按總成本排序
        comparisons.sort(key=lambda x: x['total_annual_twd'])
        
        return comparisons
    
    def group_by_country(self, comparisons: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """按國家分組"""
        grouped = defaultdict(list)
        
        for comp in comparisons:
            country = comp['country']
            grouped[country].append(comp)
        
        return dict(grouped)
    
    def calculate_country_averages(self, grouped: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, float]]:
        """計算各國平均成本"""
        averages = {}
        
        for country, schools in grouped.items():
            total_cost = sum(s['total_annual_twd'] for s in schools)
            avg_cost = total_cost / len(schools) if schools else 0
            
            averages[country] = {
                'count': len(schools),
                'average_twd': round(avg_cost, 2),
                'min_twd': round(min(s['total_annual_twd'] for s in schools), 2) if schools else 0,
                'max_twd': round(max(s['total_annual_twd'] for s in schools), 2) if schools else 0
            }
        
        return averages
    
    def render_markdown_report(self, app_costs: Dict[str, Any], comparisons: List[Dict[str, Any]]) -> str:
        """渲染 Markdown 報告"""
        
        markdown = "## 💰 財務規劃總覽\n\n"
        markdown += f"**更新時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        markdown += f"**匯率來源**: {'即時匯率' if self.use_live_rates else '固定匯率'}\n\n"
        
        # 總申請成本
        markdown += "### 📝 總申請成本\n\n"
        markdown += f"- **總申請學校數**: {app_costs['total_schools']} 所\n"
        markdown += f"- **總申請費用**: NT$ {app_costs['total_twd']:,.0f}\n"
        markdown += f"- **平均每所**: NT$ {app_costs['total_twd'] / app_costs['total_schools']:,.0f}\n\n"
        
        if app_costs['breakdown']:
            markdown += "#### 申請費用明細\n\n"
            markdown += "| 學校 | 原幣金額 | 貨幣 | 台幣金額 |\n"
            markdown += "|------|----------|------|----------|\n"
            
            for item in app_costs['breakdown']:
                markdown += f"| {item['school']} "
                markdown += f"| {item['amount']:,.0f} "
                markdown += f"| {item['currency']} "
                markdown += f"| NT$ {item['twd_amount']:,.0f} |\n"
            
            markdown += "\n"
        
        # 年度總花費比較
        markdown += "### 📊 年度總花費比較（學費 + 生活費）\n\n"
        markdown += "| 排名 | 學校 | 國家 | 學費 | 生活費 | 年度總計 | 獎學金 |\n"
        markdown += "|------|------|------|------|--------|----------|--------|\n"
        
        for idx, comp in enumerate(comparisons, 1):
            tuition_str = "免費 🎓" if comp['tuition_free'] else f"NT$ {comp['tuition_twd']:,.0f}"
            scholarship_str = "✅" if comp['scholarship_available'] else "❌"
            
            markdown += f"| {idx} "
            markdown += f"| {comp['school']} "
            markdown += f"| {comp['country']} "
            markdown += f"| {tuition_str} "
            markdown += f"| NT$ {comp['living_twd']:,.0f} "
            markdown += f"| **NT$ {comp['total_annual_twd']:,.0f}** "
            markdown += f"| {scholarship_str} |\n"
        
        markdown += "\n"
        
        # 按國家分組統計
        grouped = self.group_by_country(comparisons)
        country_averages = self.calculate_country_averages(grouped)
        
        markdown += "### 🌍 各國成本比較\n\n"
        markdown += "| 國家 | 學校數 | 平均年度成本 | 最低 | 最高 |\n"
        markdown += "|------|--------|--------------|------|------|\n"
        
        # 按平均成本排序
        sorted_countries = sorted(country_averages.items(), key=lambda x: x[1]['average_twd'])
        
        for country, stats in sorted_countries:
            markdown += f"| {country} "
            markdown += f"| {stats['count']} "
            markdown += f"| NT$ {stats['average_twd']:,.0f} "
            markdown += f"| NT$ {stats['min_twd']:,.0f} "
            markdown += f"| NT$ {stats['max_twd']:,.0f} |\n"
        
        markdown += "\n"
        
        # 獎學金機會
        scholarship_schools = [c for c in comparisons if c['scholarship_available']]
        if scholarship_schools:
            markdown += "### 🎓 獎學金機會\n\n"
            
            for school in scholarship_schools:
                markdown += f"#### {school['school']} ({school['country']})\n"
                if school['scholarship_details']:
                    markdown += f"- {school['scholarship_details']}\n"
                else:
                    markdown += "- 有獎學金機會，請查詢學校網站\n"
                markdown += "\n"
        
        # 財務建議
        markdown += "### 💡 財務建議\n\n"
        
        if comparisons:
            cheapest = comparisons[0]
            most_expensive = comparisons[-1]
            
            markdown += f"- **最經濟選擇**: {cheapest['school']} ({cheapest['country']}) - NT$ {cheapest['total_annual_twd']:,.0f}/年\n"
            markdown += f"- **最高成本**: {most_expensive['school']} ({most_expensive['country']}) - NT$ {most_expensive['total_annual_twd']:,.0f}/年\n"
            markdown += f"- **成本差異**: NT$ {most_expensive['total_annual_twd'] - cheapest['total_annual_twd']:,.0f}/年\n\n"
        
        # 免學費學校
        tuition_free_schools = [c for c in comparisons if c['tuition_free']]
        if tuition_free_schools:
            markdown += f"- **免學費學校**: {len(tuition_free_schools)} 所\n"
            for school in tuition_free_schools:
                markdown += f"  - {school['school']} ({school['country']})\n"
            markdown += "\n"
        
        # 匯率資訊
        markdown += "### 💱 參考匯率 (對台幣)\n\n"
        for currency, rate in sorted(self.exchange_rates.items()):
            if currency != 'TWD':
                markdown += f"- 1 {currency} = NT$ {rate:.2f}\n"
        
        return markdown
    
    def update_dashboard(self) -> bool:
        """更新 application dashboard"""
        try:
            schools = self.load_schools()
            
            if not schools:
                self.logger.warning("沒有學校資料")
                return False
            
            # 計算申請成本
            app_costs = self.calculate_total_application_cost(schools)
            
            # 生成成本比較
            comparisons = self.generate_cost_comparison(schools)
            
            # 渲染報告
            markdown = self.render_markdown_report(app_costs, comparisons)
            
            # 附加到 dashboard
            if Path(self.dashboard_file).exists():
                with open(self.dashboard_file, 'a', encoding='utf-8') as f:
                    f.write('\n\n---\n\n')
                    f.write(markdown)
            else:
                with open(self.dashboard_file, 'w', encoding='utf-8') as f:
                    f.write('# 申請進度儀表板\n\n')
                    f.write(markdown)
            
            self.logger.info(f"Dashboard 已更新: {self.dashboard_file}")
            
            # 也儲存獨立的財務報告
            self.save_financial_report(app_costs, comparisons)
            
            return True
        
        except Exception as e:
            self.logger.error(f"更新 dashboard 失敗: {e}")
            return False
    
    def save_financial_report(self, app_costs: Dict[str, Any], comparisons: List[Dict[str, Any]]) -> None:
        """儲存財務報告"""
        report_dir = Path('reports/financial_reports')
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f"budget_analysis_{datetime.now().strftime('%Y%m%d')}.md"
        
        markdown = self.render_markdown_report(app_costs, comparisons)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# 財務規劃分析報告\n\n")
            f.write(markdown)
        
        self.logger.info(f"財務報告已儲存: {report_file}")
    
    def generate_summary(self) -> Dict[str, Any]:
        """生成財務摘要"""
        schools = self.load_schools()
        app_costs = self.calculate_total_application_cost(schools)
        comparisons = self.generate_cost_comparison(schools)
        
        if comparisons:
            cheapest = comparisons[0]
            most_expensive = comparisons[-1]
            average = sum(c['total_annual_twd'] for c in comparisons) / len(comparisons)
        else:
            cheapest = most_expensive = None
            average = 0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_schools': len(schools),
            'total_application_cost_twd': app_costs['total_twd'],
            'average_annual_cost_twd': round(average, 2),
            'cheapest_school': cheapest['school'] if cheapest else None,
            'cheapest_cost_twd': cheapest['total_annual_twd'] if cheapest else 0,
            'most_expensive_school': most_expensive['school'] if most_expensive else None,
            'most_expensive_cost_twd': most_expensive['total_annual_twd'] if most_expensive else 0,
            'tuition_free_count': sum(1 for c in comparisons if c['tuition_free']),
            'scholarship_available_count': sum(1 for c in comparisons if c['scholarship_available'])
        }


def main():
    """主函式"""
    import argparse
    
    parser = argparse.ArgumentParser(description='財務規劃分析工具')
    parser.add_argument('--live-rates', action='store_true', help='使用即時匯率')
    args = parser.parse_args()
    
    print("""
╔══════════════════════════════════════════════════════════╗
║         財務規劃儀表板                                  ║
║         Budget Analysis Dashboard                       ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    analyzer = BudgetAnalyzer(use_live_rates=args.live_rates)
    
    print("\n📊 生成財務分析報告...\n")
    
    # 更新 dashboard
    if analyzer.update_dashboard():
        print("✅ Dashboard 已更新")
    
    # 顯示摘要
    summary = analyzer.generate_summary()
    
    print("\n" + "="*60)
    print("💰 財務摘要")
    print("="*60)
    print(f"申請學校數: {summary['total_schools']}")
    print(f"總申請費用: NT$ {summary['total_application_cost_twd']:,.0f}")
    print(f"\n平均年度成本: NT$ {summary['average_annual_cost_twd']:,.0f}")
    print(f"最低成本: {summary['cheapest_school']} - NT$ {summary['cheapest_cost_twd']:,.0f}/年")
    print(f"最高成本: {summary['most_expensive_school']} - NT$ {summary['most_expensive_cost_twd']:,.0f}/年")
    print(f"\n免學費學校: {summary['tuition_free_count']} 所")
    print(f"有獎學金機會: {summary['scholarship_available_count']} 所")
    print(f"\n報告已儲存至: reports/financial_reports/")
    print("\n✅ 完成！")


if __name__ == '__main__':
    main()

