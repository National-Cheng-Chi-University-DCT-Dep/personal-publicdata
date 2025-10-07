#!/usr/bin/env python3
"""
What-If Scenario Simulator for University Applications

Features:
- Interactive profile modification simulation
- Real-time admission probability recalculation
- Side-by-side comparison of scenarios
- ROI impact analysis
- Strategic decision support
- Effort vs. reward quantification
"""

import os
import sys
import json
import yaml
import copy
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
import argparse

@dataclass
class ProfileScenario:
    scenario_name: str
    bachelor_gpa: float = 2.92
    master_gpa: float = 3.96
    ielts_overall: float = 7.0
    ielts_writing: float = 5.5
    ielts_reading: float = 9.0
    ielts_listening: float = 7.5
    ielts_speaking: float = 6.5
    work_experience_years: int = 5
    publications: int = 0
    github_contributions: int = 0
    certifications: int = 0
    recommendation_quality: float = 0.8  # 0.0-1.0 scale
    sop_quality: float = 0.8  # 0.0-1.0 scale
    budget_eur: int = 25000 # 2 years
    
@dataclass
class ScenarioImpact:
    school_id: str
    school_name: str
    baseline_probability: float
    scenario_probability: float
    probability_change: float
    baseline_risk_category: str
    scenario_risk_category: str
    cost_eur: float
    roi_impact: float
    recommendation: str

@dataclass
class SimulationResult:
    scenario: ProfileScenario
    school_impacts: List[ScenarioImpact]
    overall_metrics: Dict[str, float]
    cost_benefit_analysis: Dict[str, Any]
    recommendations: List[str]

class WhatIfSimulator:
    """Interactive scenario simulation for application strategy optimization"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.source_data_dir = self.base_dir / "source_data"
        self.output_dir = self.base_dir / "final_applications"
        
        # Load configuration
        self.load_schools_config()
        self.load_baseline_profile()
        
        # Load existing analysis data if available
        self.load_risk_analysis_data()
        
        # Setup simulation parameters
        self.setup_simulation_weights()
    
    def load_schools_config(self):
        """Load school configuration"""
        with open(self.source_data_dir / "schools.yml", 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            self.schools = {school['school_id']: school for school in data['schools']}
    
    def load_baseline_profile(self):
        """Load or create baseline profile"""
        profile_file = self.source_data_dir / "baseline_profile.yml"
        
        if profile_file.exists():
            with open(profile_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self.baseline_profile = ProfileScenario(**data)
        else:
            # Create default baseline profile
            self.baseline_profile = ProfileScenario(scenario_name="current_profile")
            self.save_baseline_profile()
    
    def save_baseline_profile(self):
        """Save baseline profile to file"""
        profile_file = self.source_data_dir / "baseline_profile.yml"
        with open(profile_file, 'w', encoding='utf-8') as f:
            yaml.dump(asdict(self.baseline_profile), f, default_flow_style=False)
    
    def load_risk_analysis_data(self):
        """Load existing risk analysis data if available"""
        risk_data_file = self.output_dir / "risk_portfolio_data.json"
        
        if risk_data_file.exists():
            with open(risk_data_file, 'r', encoding='utf-8') as f:
                self.risk_data = json.load(f)
        else:
            print("⚠️  No existing risk analysis data found. Baseline calculations may be less accurate.")
            self.risk_data = {}
    
    def setup_simulation_weights(self):
        """Setup weights for different factors in admission probability calculation"""
        self.admission_weights = {
            'gpa_weight': 0.25,
            'ielts_weight': 0.25, 
            'experience_weight': 0.20,
            'research_weight': 0.15,
            'fit_weight': 0.15
        }
        
        # Effort costs for different improvements (in hours/euros)
        self.improvement_costs = {
            'ielts_retake': {'time_hours': 120, 'cost_eur': 350, 'success_rate': 0.8},
            'additional_certification': {'time_hours': 80, 'cost_eur': 200, 'success_rate': 0.9},
            'github_contribution': {'time_hours': 40, 'cost_eur': 0, 'success_rate': 0.95},
            'research_publication': {'time_hours': 200, 'cost_eur': 500, 'success_rate': 0.3},
            'sop_professional_editing': {'time_hours': 20, 'cost_eur': 800, 'success_rate': 0.95}
        }
    
    def calculate_admission_probability(self, profile: ProfileScenario, school_id: str) -> float:
        """Calculate admission probability for a given profile and school"""
        school = self.schools.get(school_id, {})
        
        # Base probability from school requirements
        base_prob = 0.5  # Default baseline
        
        # GPA factor
        gpa_score = min(profile.master_gpa / 4.0, 1.0)  # Normalize to 0-1
        if profile.master_gpa >= 3.7:
            gpa_factor = 1.2
        elif profile.master_gpa >= 3.5:
            gpa_factor = 1.0
        elif profile.master_gpa >= 3.0:
            gpa_factor = 0.9
        else:
            gpa_factor = 0.7
        
        # IELTS factor
        school_ielts_req = school.get('ielts_requirement', {})
        required_overall = school_ielts_req.get('overall', 6.5)
        required_writing = school_ielts_req.get('writing_minimum', 
                                               school_ielts_req.get('minimum_band', 5.5))
        
        ielts_factor = 1.0
        if profile.ielts_overall >= required_overall + 0.5:
            ielts_factor = 1.3
        elif profile.ielts_overall >= required_overall:
            ielts_factor = 1.1
        elif profile.ielts_overall >= required_overall - 0.5:
            ielts_factor = 0.9
        else:
            ielts_factor = 0.6
        
        # Writing penalty/bonus
        if profile.ielts_writing < required_writing:
            ielts_factor *= 0.7
        elif profile.ielts_writing >= required_writing + 0.5:
            ielts_factor *= 1.1
        
        # Experience factor
        if profile.work_experience_years >= 5:
            experience_factor = 1.2
        elif profile.work_experience_years >= 3:
            experience_factor = 1.0
        elif profile.work_experience_years >= 1:
            experience_factor = 0.9
        else:
            experience_factor = 0.8
        
        # Research activity factor
        research_factor = 1.0
        if profile.publications >= 2:
            research_factor = 1.4
        elif profile.publications >= 1:
            research_factor = 1.2
        
        if profile.github_contributions >= 10:
            research_factor *= 1.1
        elif profile.github_contributions >= 5:
            research_factor *= 1.05
        
        # Application quality factor
        quality_factor = (profile.recommendation_quality + profile.sop_quality) / 2
        quality_factor = 0.8 + (quality_factor * 0.4)  # Scale to 0.8-1.2
        
        # Program fit factor (simplified based on school priority)
        priority = school.get('priority_level', 'medium')
        if priority == 'high':
            fit_factor = 1.1  # High priority = good fit
        elif priority == 'low':
            fit_factor = 0.9   # Low priority = less fit
        else:
            fit_factor = 1.0
        
        # Calculate weighted probability
        probability = base_prob * (
            gpa_factor ** self.admission_weights['gpa_weight'] *
            ielts_factor ** self.admission_weights['ielts_weight'] *
            experience_factor ** self.admission_weights['experience_weight'] *
            research_factor ** self.admission_weights['research_weight'] *
            (quality_factor * fit_factor) ** self.admission_weights['fit_weight']
        )
        
        # Cap at realistic range
        return max(0.05, min(0.95, probability))
    
    def categorize_risk(self, probability: float) -> str:
        """Categorize school based on admission probability"""
        if probability >= 0.7:
            return "safe"
        elif probability >= 0.3:
            return "target"
        else:
            return "reach"
    
    def calculate_roi_impact(self, baseline_prob: float, scenario_prob: float, 
                           improvement_effort: Dict[str, float]) -> float:
        """Calculate ROI of the improvement effort"""
        probability_gain = scenario_prob - baseline_prob
        
        # Estimate value of probability gain (in EUR)
        # Higher probability = higher chance of avoiding gap year costs
        gap_year_cost = 20000  # Estimated cost of delaying studies by one year
        probability_value = probability_gain * gap_year_cost
        
        # Calculate total effort cost
        total_cost = improvement_effort.get('cost_eur', 0)
        time_cost = improvement_effort.get('time_hours', 0) * 15  # €15/hour opportunity cost
        total_effort_cost = total_cost + time_cost
        
        if total_effort_cost <= 0:
            return float('inf') if probability_gain > 0 else 0
        
        roi = probability_value / total_effort_cost
        return roi
    
    def simulate_scenario(self, scenario: ProfileScenario) -> SimulationResult:
        """Run complete simulation for a given scenario"""
        school_impacts = []
        
        # Calculate impacts for each active school
        for school_id, school in self.schools.items():
            if school.get('status') != 'active':
                continue
            
            # Calculate baseline and scenario probabilities
            baseline_prob = self.calculate_admission_probability(self.baseline_profile, school_id)
            scenario_prob = self.calculate_admission_probability(scenario, school_id)
            
            # Extract cost
            cost_eur = self.extract_cost_eur(school.get('tuition_fee', ''))
            
            # Calculate ROI impact (simplified)
            roi_impact = scenario_prob - baseline_prob
            
            # Generate recommendation
            prob_change = scenario_prob - baseline_prob
            if prob_change >= 0.15:
                recommendation = "🚀 顯著提升，強烈建議此改進"
            elif prob_change >= 0.05:
                recommendation = "✅ 適度提升，值得考慮"
            elif prob_change >= -0.05:
                recommendation = "➡️ 影響微小"
            else:
                recommendation = "⚠️ 可能產生負面影響"
            
            impact = ScenarioImpact(
                school_id=school_id,
                school_name=school.get('full_name', school_id),
                baseline_probability=baseline_prob,
                scenario_probability=scenario_prob,
                probability_change=prob_change,
                baseline_risk_category=self.categorize_risk(baseline_prob),
                scenario_risk_category=self.categorize_risk(scenario_prob),
                cost_eur=cost_eur,
                roi_impact=roi_impact,
                recommendation=recommendation
            )
            
            school_impacts.append(impact)
        
        # Calculate overall metrics
        baseline_total = sum(impact.baseline_probability for impact in school_impacts)
        scenario_total = sum(impact.scenario_probability for impact in school_impacts)
        
        overall_metrics = {
            'expected_acceptances_baseline': baseline_total,
            'expected_acceptances_scenario': scenario_total,
            'expected_acceptances_change': scenario_total - baseline_total,
            'average_probability_baseline': baseline_total / len(school_impacts) if school_impacts else 0,
            'average_probability_scenario': scenario_total / len(school_impacts) if school_impacts else 0,
            'schools_improved': sum(1 for impact in school_impacts if impact.probability_change > 0.01),
            'schools_degraded': sum(1 for impact in school_impacts if impact.probability_change < -0.01)
        }
        
        # Cost-benefit analysis
        cost_benefit = self.analyze_cost_benefit(scenario, overall_metrics)
        
        # Generate recommendations
        recommendations = self.generate_scenario_recommendations(scenario, school_impacts, overall_metrics)
        
        return SimulationResult(
            scenario=scenario,
            school_impacts=school_impacts,
            overall_metrics=overall_metrics,
            cost_benefit_analysis=cost_benefit,
            recommendations=recommendations
        )
    
    def extract_cost_eur(self, fee_string: str) -> float:
        """Extract cost in EUR from fee string (simplified version)"""
        if not fee_string:
            return 0.0
        
        import re
        fee_string = fee_string.lower()
        
        if 'free' in fee_string:
            return 0.0
        
        # Simple EUR extraction
        eur_match = re.search(r'€\s*(\d+[,.]?\d*)', fee_string)
        if eur_match:
            try:
                return float(eur_match.group(1).replace(',', ''))
            except:
                pass
        
        # SEK conversion
        sek_match = re.search(r'sek\s*(\d+[,.]?\d*)', fee_string)
        if sek_match:
            try:
                sek_amount = float(sek_match.group(1).replace(',', ''))
                return sek_amount / 11.0  # Rough conversion
            except:
                pass
        
        return 10000.0  # Default estimate
    
    def analyze_cost_benefit(self, scenario: ProfileScenario, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Analyze cost-benefit of the scenario changes"""
        changes = self.identify_scenario_changes(scenario)
        
        total_cost = 0.0
        total_time = 0.0
        total_success_rate = 1.0
        
        for change_type in changes:
            if change_type in self.improvement_costs:
                cost_info = self.improvement_costs[change_type]
                total_cost += cost_info['cost_eur']
                total_time += cost_info['time_hours']
                total_success_rate *= cost_info['success_rate']
        
        # Calculate expected benefit
        expected_acceptance_gain = metrics['expected_acceptances_change']
        
        # Value estimation (avoiding gap year, better opportunities)
        gap_year_cost = 25000  # EUR (tuition + living costs + opportunity cost)
        career_improvement = 50000  # EUR (lifetime value of better school)
        
        expected_benefit = (
            expected_acceptance_gain * gap_year_cost * 0.3 +  # Risk reduction value
            expected_acceptance_gain * career_improvement * 0.1  # Career improvement value
        )
        
        # Adjust for success rate
        expected_benefit *= total_success_rate
        
        # Calculate ROI
        total_investment = total_cost + (total_time * 20)  # €20/hour opportunity cost
        roi = (expected_benefit - total_investment) / total_investment if total_investment > 0 else 0
        
        return {
            'total_cost_eur': total_cost,
            'total_time_hours': total_time,
            'total_investment_eur': total_investment,
            'expected_benefit_eur': expected_benefit,
            'success_probability': total_success_rate,
            'roi_percentage': roi * 100,
            'payback_period_months': (total_investment / (expected_benefit / 12)) if expected_benefit > 0 else float('inf'),
            'changes_required': changes
        }
    
    def identify_scenario_changes(self, scenario: ProfileScenario) -> List[str]:
        """Identify what changes are needed to achieve the scenario"""
        changes = []
        
        # IELTS improvements
        if scenario.ielts_overall > self.baseline_profile.ielts_overall or \
           scenario.ielts_writing > self.baseline_profile.ielts_writing:
            changes.append('ielts_retake')
        
        # Certifications
        if scenario.certifications > self.baseline_profile.certifications:
            changes.append('additional_certification')
        
        # GitHub contributions
        if scenario.github_contributions > self.baseline_profile.github_contributions:
            changes.append('github_contribution')
        
        # Publications
        if scenario.publications > self.baseline_profile.publications:
            changes.append('research_publication')
        
        # SOP quality improvement
        if scenario.sop_quality > self.baseline_profile.sop_quality:
            changes.append('sop_professional_editing')
        
        return changes
    
    def generate_scenario_recommendations(self, scenario: ProfileScenario, 
                                        impacts: List[ScenarioImpact], 
                                        metrics: Dict[str, float]) -> List[str]:
        """Generate strategic recommendations based on simulation results"""
        recommendations = []
        
        # Overall impact assessment
        total_improvement = metrics['expected_acceptances_change']
        
        if total_improvement >= 1.0:
            recommendations.append("🎯 此情境顯著提升整體錄取機會，強烈建議實施")
        elif total_improvement >= 0.5:
            recommendations.append("✅ 此情境適度改善申請結果，建議考慮實施")
        elif total_improvement >= 0.1:
            recommendations.append("📊 此情境有輕微改善，需評估投入成本效益")
        else:
            recommendations.append("⚠️ 此情境改善效果有限，可能不值得大量投入")
        
        # School-specific insights
        high_impact_schools = [imp for imp in impacts if imp.probability_change >= 0.15]
        if high_impact_schools:
            school_names = [school.school_name for school in high_impact_schools[:3]]
            recommendations.append(f"🚀 對以下學校影響最大: {', '.join(school_names)}")
        
        # Risk category changes
        category_upgrades = [imp for imp in impacts 
                           if imp.baseline_risk_category == 'reach' and imp.scenario_risk_category == 'target']
        if category_upgrades:
            recommendations.append(f"📈 將 {len(category_upgrades)} 所衝刺學校提升為目標學校")
        
        safety_improvements = [imp for imp in impacts 
                             if imp.baseline_risk_category == 'target' and imp.scenario_risk_category == 'safe']
        if safety_improvements:
            recommendations.append(f"🛡️ 將 {len(safety_improvements)} 所目標學校提升為保底學校")
        
        # Specific action recommendations
        changes = self.identify_scenario_changes(scenario)
        
        if 'ielts_retake' in changes:
            ielts_schools = [imp for imp in impacts if imp.probability_change >= 0.1]
            if len(ielts_schools) >= 3:
                recommendations.append("📚 IELTS重考對多所學校都有顯著幫助，值得優先考慮")
            else:
                recommendations.append("📝 IELTS重考效果有限，可考慮其他改進方式")
        
        if 'github_contribution' in changes:
            recommendations.append("💻 GitHub貢獻成本低且效果穩定，建議立即開始")
        
        if 'research_publication' in changes:
            research_impact = sum(imp.probability_change for imp in impacts if imp.probability_change > 0)
            if research_impact >= 1.5:
                recommendations.append("🔬 研究發表雖耗時但影響巨大，建議長期投入")
            else:
                recommendations.append("📄 研究發表投入產出比不高，可考慮其他選項")
        
        return recommendations
    
    def run_interactive_simulation(self):
        """Run interactive What-If simulation"""
        print("🔮 歡迎使用What-If情境模擬器！")
        print("您可以修改個人檔案參數，查看對申請結果的影響。")
        print()
        
        # Show current profile
        print("📊 當前基準檔案:")
        self.display_profile(self.baseline_profile)
        print()
        
        while True:
            print("請選擇要模擬的情境:")
            print("1. 📚 IELTS重考情境")
            print("2. 🔬 增加研究經驗情境")
            print("3. 💻 技術技能提升情境")
            print("4. 📝 申請文件優化情境")
            print("5. 🎯 自定義情境")
            print("6. 📊 比較多個情境")
            print("7. 💾 儲存情境")
            print("8. 🚪 退出")
            
            choice = input("\n請輸入選擇 (1-8): ").strip()
            
            if choice == '1':
                self.simulate_ielts_improvement()
            elif choice == '2':
                self.simulate_research_improvement()
            elif choice == '3':
                self.simulate_technical_improvement()
            elif choice == '4':
                self.simulate_application_quality_improvement()
            elif choice == '5':
                self.simulate_custom_scenario()
            elif choice == '6':
                self.compare_multiple_scenarios()
            elif choice == '7':
                self.save_scenario()
            elif choice == '8':
                print("感謝使用What-If模擬器！")
                break
            else:
                print("無效選擇，請重新輸入。")
            
            print("\n" + "="*60 + "\n")
    
    def display_profile(self, profile: ProfileScenario):
        """Display profile information"""
        print(f"  學術成績: 學士 {profile.bachelor_gpa:.2f}, 碩士 {profile.master_gpa:.2f}")
        print(f"  IELTS: 總分 {profile.ielts_overall}, 寫作 {profile.ielts_writing}")
        print(f"  工作經驗: {profile.work_experience_years} 年")
        print(f"  研究成果: {profile.publications} 篇論文, {profile.github_contributions} 個GitHub貢獻")
        print(f"  申請品質: 推薦信 {profile.recommendation_quality:.1f}, SOP {profile.sop_quality:.1f}")
    
    def simulate_ielts_improvement(self):
        """Simulate IELTS score improvement scenario"""
        print("\n📚 IELTS重考情境模擬")
        print("假設經過3個月準備重考IELTS...")
        
        # Create improved scenario
        scenario = copy.deepcopy(self.baseline_profile)
        scenario.scenario_name = "ielts_improvement"
        scenario.ielts_overall = min(8.5, scenario.ielts_overall + 0.5)
        scenario.ielts_writing = min(8.0, scenario.ielts_writing + 1.0)  # Focus on writing
        
        # Run simulation
        result = self.simulate_scenario(scenario)
        
        # Display results
        self.display_simulation_results(result)
    
    def simulate_research_improvement(self):
        """Simulate research experience improvement scenario"""
        print("\n🔬 研究經驗提升情境模擬")
        print("假設投入6個月時間進行研究...")
        
        scenario = copy.deepcopy(self.baseline_profile)
        scenario.scenario_name = "research_improvement"
        scenario.publications = scenario.publications + 1
        scenario.github_contributions = scenario.github_contributions + 10
        scenario.sop_quality = min(1.0, scenario.sop_quality + 0.1)
        
        result = self.simulate_scenario(scenario)
        self.display_simulation_results(result)
    
    def simulate_technical_improvement(self):
        """Simulate technical skills improvement scenario"""
        print("\n💻 技術技能提升情境模擬")
        print("假設獲得額外認證和開源貢獻...")
        
        scenario = copy.deepcopy(self.baseline_profile)
        scenario.scenario_name = "technical_improvement"
        scenario.certifications = scenario.certifications + 2
        scenario.github_contributions = scenario.github_contributions + 15
        scenario.recommendation_quality = min(1.0, scenario.recommendation_quality + 0.1)
        
        result = self.simulate_scenario(scenario)
        self.display_simulation_results(result)
    
    def simulate_application_quality_improvement(self):
        """Simulate application document quality improvement scenario"""
        print("\n📝 申請文件優化情境模擬")
        print("假設投資專業編輯和顧問服務...")
        
        scenario = copy.deepcopy(self.baseline_profile)
        scenario.scenario_name = "application_quality_improvement"
        scenario.sop_quality = min(1.0, scenario.sop_quality + 0.2)
        scenario.recommendation_quality = min(1.0, scenario.recommendation_quality + 0.15)
        
        result = self.simulate_scenario(scenario)
        self.display_simulation_results(result)
    
    def simulate_custom_scenario(self):
        """Allow user to create custom scenario"""
        print("\n🎯 自定義情境模擬")
        print("請輸入您想要測試的參數變化:")
        
        scenario = copy.deepcopy(self.baseline_profile)
        scenario.scenario_name = "custom_scenario"
        
        try:
            # IELTS improvements
            new_overall = input(f"IELTS總分 (當前 {scenario.ielts_overall}, 按Enter跳過): ").strip()
            if new_overall:
                scenario.ielts_overall = float(new_overall)
            
            new_writing = input(f"IELTS寫作 (當前 {scenario.ielts_writing}, 按Enter跳過): ").strip()
            if new_writing:
                scenario.ielts_writing = float(new_writing)
            
            # Research improvements
            new_pubs = input(f"論文數量 (當前 {scenario.publications}, 按Enter跳過): ").strip()
            if new_pubs:
                scenario.publications = int(new_pubs)
            
            new_github = input(f"GitHub貢獻 (當前 {scenario.github_contributions}, 按Enter跳過): ").strip()
            if new_github:
                scenario.github_contributions = int(new_github)
            
            # Application quality
            new_sop = input(f"SOP品質 0-1 (當前 {scenario.sop_quality:.1f}, 按Enter跳過): ").strip()
            if new_sop:
                scenario.sop_quality = float(new_sop)
            
            result = self.simulate_scenario(scenario)
            self.display_simulation_results(result)
            
        except ValueError:
            print("❌ 輸入格式錯誤，請確保數值格式正確")
    
    def compare_multiple_scenarios(self):
        """Compare multiple predefined scenarios"""
        print("\n📊 多情境比較分析")
        
        scenarios = [
            self.baseline_profile,
        ]
        
        # Create comparison scenarios
        ielts_scenario = copy.deepcopy(self.baseline_profile)
        ielts_scenario.scenario_name = "IELTS重考"
        ielts_scenario.ielts_overall = min(8.5, ielts_scenario.ielts_overall + 0.5)
        ielts_scenario.ielts_writing = min(8.0, ielts_scenario.ielts_writing + 1.0)
        scenarios.append(ielts_scenario)
        
        research_scenario = copy.deepcopy(self.baseline_profile)
        research_scenario.scenario_name = "研究提升"
        research_scenario.publications += 1
        research_scenario.github_contributions += 10
        scenarios.append(research_scenario)
        
        combined_scenario = copy.deepcopy(self.baseline_profile)
        combined_scenario.scenario_name = "全面提升"
        combined_scenario.ielts_writing = min(8.0, combined_scenario.ielts_writing + 0.5)
        combined_scenario.publications += 1
        combined_scenario.sop_quality = min(1.0, combined_scenario.sop_quality + 0.1)
        scenarios.append(combined_scenario)
        
        # Run all simulations
        results = []
        for scenario in scenarios:
            if scenario.scenario_name == "current_profile":
                scenario.scenario_name = "基準情境"
            result = self.simulate_scenario(scenario)
            results.append(result)
        
        # Display comparison
        self.display_scenario_comparison(results)
    
    def display_simulation_results(self, result: SimulationResult):
        """Display detailed simulation results"""
        print(f"\n🎯 情境模擬結果: {result.scenario.scenario_name}")
        print("=" * 50)
        
        # Overall metrics
        metrics = result.overall_metrics
        print(f"📈 預期錄取數量變化: {metrics['expected_acceptances_baseline']:.1f} → {metrics['expected_acceptances_scenario']:.1f} "
              f"({metrics['expected_acceptances_change']:+.1f})")
        print(f"📊 平均錄取機率變化: {metrics['average_probability_baseline']:.1%} → {metrics['average_probability_scenario']:.1%}")
        print(f"🎯 改善學校數量: {metrics['schools_improved']}")
        
        # Cost-benefit analysis
        cb = result.cost_benefit_analysis
        print(f"\n💰 成本效益分析:")
        print(f"   總投資: €{cb['total_investment_eur']:,.0f} ({cb['total_time_hours']:.0f} 小時)")
        print(f"   預期收益: €{cb['expected_benefit_eur']:,.0f}")
        print(f"   投資報酬率: {cb['roi_percentage']:+.1f}%")
        print(f"   成功機率: {cb['success_probability']:.1%}")
        
        # Top impact schools
        print(f"\n🏛️ 影響最大的學校:")
        top_impacts = sorted(result.school_impacts, key=lambda x: x.probability_change, reverse=True)[:5]
        
        for impact in top_impacts:
            print(f"   {impact.school_name}: "
                  f"{impact.baseline_probability:.1%} → {impact.scenario_probability:.1%} "
                  f"({impact.probability_change:+.1%}) - {impact.recommendation}")
        
        # Recommendations
        if result.recommendations:
            print(f"\n💡 策略建議:")
            for i, rec in enumerate(result.recommendations, 1):
                print(f"   {i}. {rec}")
    
    def display_scenario_comparison(self, results: List[SimulationResult]):
        """Display side-by-side comparison of multiple scenarios"""
        print("\n📊 情境比較分析")
        print("=" * 80)
        
        # Comparison table header
        print(f"{'情境名稱':<15} {'預期錄取':<10} {'平均機率':<10} {'投資(€)':<10} {'ROI':<8} {'推薦度':<10}")
        print("-" * 80)
        
        for result in results:
            metrics = result.overall_metrics
            cb = result.cost_benefit_analysis
            
            # Calculate recommendation level
            if cb['roi_percentage'] >= 100:
                rec_level = "🌟 極佳"
            elif cb['roi_percentage'] >= 50:
                rec_level = "✅ 推薦"
            elif cb['roi_percentage'] >= 0:
                rec_level = "⚠️ 謹慎"
            else:
                rec_level = "❌ 不建議"
            
            print(f"{result.scenario.scenario_name:<15} "
                  f"{metrics['expected_acceptances_scenario']:<10.1f} "
                  f"{metrics['average_probability_scenario']:<10.1%} "
                  f"{cb['total_investment_eur']:<10.0f} "
                  f"{cb['roi_percentage']:<8.0f}% "
                  f"{rec_level:<10}")
        
        # Best scenario recommendation
        best_scenario = max(results[1:], key=lambda x: x.cost_benefit_analysis['roi_percentage'])
        print(f"\n🏆 最佳策略: {best_scenario.scenario.scenario_name}")
    
    def save_scenario(self):
        """Save current scenario for future reference"""
        print("\n💾 儲存情境功能")
        print("此功能將保存自定義情境以供日後參考")
        # Implementation would save scenarios to file
        print("✅ 功能開發中，敬請期待")
    
    def run_batch_analysis(self, scenarios: List[ProfileScenario]) -> List[SimulationResult]:
        """Run batch analysis for multiple scenarios"""
        results = []
        
        print(f"🔮 Running batch analysis for {len(scenarios)} scenarios...")
        
        for scenario in scenarios:
            print(f"   Analyzing: {scenario.scenario_name}")
            result = self.simulate_scenario(scenario)
            results.append(result)
        
        return results
    
    def generate_optimization_report(self, results: List[SimulationResult]) -> str:
        """Generate comprehensive optimization report"""
        report_lines = [
            "# 🔮 What-If 情境模擬優化報告",
            "",
            f"**分析時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**模擬情境數量**: {len(results)}",
            "",
            "## 📊 情境比較總覽",
            "",
            "| 情境名稱 | 預期錄取數 | 平均機率 | 總投資(€) | ROI | 建議等級 |",
            "|----------|------------|----------|-----------|-----|----------|"
        ]
        
        # Sort by ROI
        sorted_results = sorted(results, key=lambda x: x.cost_benefit_analysis['roi_percentage'], reverse=True)
        
        for result in sorted_results:
            metrics = result.overall_metrics
            cb = result.cost_benefit_analysis
            
            if cb['roi_percentage'] >= 100:
                rec_level = "🌟🌟🌟"
            elif cb['roi_percentage'] >= 50:
                rec_level = "⭐⭐"
            elif cb['roi_percentage'] >= 0:
                rec_level = "⭐"
            else:
                rec_level = "❌"
            
            report_lines.append(
                f"| {result.scenario.scenario_name} | "
                f"{metrics['expected_acceptances_scenario']:.1f} | "
                f"{metrics['average_probability_scenario']:.1%} | "
                f"{cb['total_investment_eur']:,.0f} | "
                f"{cb['roi_percentage']:.0f}% | "
                f"{rec_level} |"
            )
        
        # Detailed analysis for top scenarios
        report_lines.extend([
            "",
            "## 🏆 最佳策略詳細分析",
            ""
        ])
        
        for result in sorted_results[:3]:  # Top 3 scenarios
            report_lines.extend([
                f"### {result.scenario.scenario_name}",
                "",
                f"**投資報酬率**: {result.cost_benefit_analysis['roi_percentage']:.1f}%",
                f"**預期錄取提升**: {result.overall_metrics['expected_acceptances_change']:+.1f} 所",
                f"**總投資**: €{result.cost_benefit_analysis['total_investment_eur']:,.0f}",
                ""
            ])
            
            if result.recommendations:
                report_lines.extend([
                    "**策略建議**:",
                    ""
                ])
                for rec in result.recommendations:
                    report_lines.append(f"- {rec}")
                report_lines.append("")
        
        report_lines.extend([
            "---",
            "",
            f"*報告生成於 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by What-If Simulator v2.0*"
        ])
        
        return "\n".join(report_lines)

def main():
    """Main What-If simulator execution"""
    parser = argparse.ArgumentParser(description='What-If Scenario Simulator')
    parser.add_argument('--interactive', action='store_true', 
                       help='Run interactive simulation mode')
    parser.add_argument('--batch', action='store_true',
                       help='Run batch analysis of predefined scenarios')
    parser.add_argument('--report', action='store_true',
                       help='Generate optimization report')
    
    args = parser.parse_args()
    
    simulator = WhatIfSimulator()
    
    try:
        if args.interactive:
            simulator.run_interactive_simulation()
        elif args.batch or args.report:
            # Run predefined scenarios
            baseline = simulator.baseline_profile
            
            scenarios = [
                baseline,
                ProfileScenario(scenario_name="IELTS_Improvement", 
                              **{**asdict(baseline), 'ielts_overall': 8.0, 'ielts_writing': 6.5}),
                ProfileScenario(scenario_name="Research_Focus",
                              **{**asdict(baseline), 'publications': 1, 'github_contributions': 15}),
                ProfileScenario(scenario_name="Quality_Enhancement",
                              **{**asdict(baseline), 'sop_quality': 0.95, 'recommendation_quality': 0.95}),
                ProfileScenario(scenario_name="Comprehensive_Improvement",
                              **{**asdict(baseline), 'ielts_writing': 6.5, 'publications': 1, 'sop_quality': 0.9})
            ]
            
            results = simulator.run_batch_analysis(scenarios)
            
            if args.report:
                report_content = simulator.generate_optimization_report(results)
                
                output_dir = simulator.output_dir
                output_dir.mkdir(exist_ok=True)
                
                report_file = output_dir / "whatif_optimization_report.md"
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                
                print(f"📋 Optimization report saved to {report_file}")
            
            simulator.display_scenario_comparison(results)
        else:
            print("🔮 What-If Scenario Simulator")
            print("Usage:")
            print("  --interactive    : 互動式情境模擬")
            print("  --batch         : 批次情境分析")
            print("  --report        : 生成優化報告")
            print("\nExample: python whatif_simulator.py --interactive")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 模擬器已停止")
        return 130
    
    except Exception as e:
        print(f"❌ What-If simulation failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
