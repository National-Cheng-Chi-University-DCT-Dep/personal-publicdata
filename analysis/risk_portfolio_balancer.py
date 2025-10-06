#!/usr/bin/env python3
"""
Dynamic Risk Portfolio Balancer for University Applications

Features:
- Financial portfolio theory applied to school selection
- Risk categorization (Reach, Target, Safe)
- Portfolio risk assessment and optimization
- ROI analysis and strategic recommendations
- Dynamic rebalancing suggestions
"""

import os
import sys
import json
import yaml
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
import math

@dataclass
class SchoolRiskProfile:
    school_id: str
    school_name: str
    risk_category: str  # "reach", "target", "safe"
    admission_probability: float  # 0.0 - 1.0
    cost_eur: float
    roi_score: float
    prestige_score: float
    fit_score: float
    overall_score: float
    confidence_level: float

@dataclass
class PortfolioAnalysis:
    total_risk_score: float  # 0-10 scale
    risk_distribution: Dict[str, float]  # Percentage in each category
    expected_acceptances: float
    cost_efficiency: float
    diversification_score: float
    recommendations: List[str]
    optimal_changes: List[Dict[str, Any]]

class RiskPortfolioBalancer:
    """Advanced portfolio risk management for university applications"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.source_data_dir = self.base_dir / "source_data"
        self.output_dir = self.base_dir / "final_applications"
        
        # Load configuration and validation data
        self.load_schools_config()
        self.load_validation_data()
        self.setup_risk_parameters()
    
    def load_schools_config(self):
        """Load school configuration"""
        with open(self.source_data_dir / "schools.yml", 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            self.schools = {school['school_id']: school for school in data['schools']}
    
    def load_validation_data(self):
        """Load validation results for risk calculation"""
        validation_file = self.output_dir / "validation_results.json"
        
        if validation_file.exists():
            with open(validation_file, 'r', encoding='utf-8') as f:
                self.validation_data = json.load(f)
        else:
            print("⚠️  No validation results found. Using default risk assessments.")
            self.validation_data = {}
    
    def setup_risk_parameters(self):
        """Setup risk assessment parameters"""
        # Personal profile for risk calculation
        self.personal_profile = {
            'bachelor_gpa': 2.92,
            'master_gpa': 3.96,
            'ielts_overall': 7.0,
            'ielts_writing': 5.5,
            'work_experience_years': 5,
            'target_budget_eur': 15000,
            'risk_tolerance': 'medium'  # low, medium, high
        }
        
        # Risk category thresholds
        self.risk_thresholds = {
            'reach': (0.0, 0.3),      # 0-30% admission probability
            'target': (0.3, 0.7),     # 30-70% admission probability  
            'safe': (0.7, 1.0)        # 70-100% admission probability
        }
        
        # Portfolio optimization parameters
        self.optimal_portfolio = {
            'reach': 0.25,    # 25% reach schools
            'target': 0.50,   # 50% target schools
            'safe': 0.25      # 25% safe schools
        }
        
        # Weight factors for scoring
        self.score_weights = {
            'admission_probability': 0.3,
            'cost_efficiency': 0.2,
            'prestige': 0.2,
            'program_fit': 0.2,
            'career_prospects': 0.1
        }
    
    def calculate_admission_probability(self, school_id: str) -> float:
        """Calculate admission probability based on eligibility and fit"""
        school = self.schools.get(school_id, {})
        validation_result = self.validation_data.get('results', {}).get(school_id, {})
        
        # Base probability from validation status
        status = validation_result.get('overall_status', 'NEEDS_REVIEW')
        base_probability = {
            'ELIGIBLE': 0.7,
            'WARNING': 0.4,
            'NEEDS_REVIEW': 0.3,
            'INELIGIBLE': 0.1
        }.get(status, 0.3)
        
        # Adjust based on confidence score
        confidence = validation_result.get('confidence_score', 0.5)
        probability = base_probability * (0.5 + confidence * 0.5)
        
        # Adjust based on IELTS fit
        ielts_details = validation_result.get('validation_details', {})
        ielts_status = ielts_details.get('ielts_status', 'WARNING')
        
        if ielts_status == 'ELIGIBLE':
            probability *= 1.2
        elif ielts_status == 'WARNING':
            probability *= 0.9
        elif ielts_status == 'INELIGIBLE':
            probability *= 0.6
        
        # Adjust based on budget fit
        budget_status = ielts_details.get('budget_status', 'WARNING')
        
        if budget_status == 'ELIGIBLE':
            probability *= 1.1
        elif budget_status == 'WARNING':
            probability *= 0.95
        
        # Adjust based on priority level (higher priority = more competitive)
        priority = school.get('priority_level', 'medium')
        if priority == 'high':
            probability *= 0.8  # High priority schools are more competitive
        elif priority == 'low':
            probability *= 1.2  # Low priority schools may be less competitive
        
        # Cap at 1.0
        return min(probability, 1.0)
    
    def extract_cost_eur(self, fee_string: str) -> float:
        """Extract cost in EUR from fee string"""
        if not fee_string:
            return 0.0
        
        fee_string = fee_string.lower()
        
        if 'free' in fee_string or '€0' in fee_string:
            return 0.0
        
        # Extract numeric values
        import re
        
        # Look for EUR amounts
        eur_patterns = [
            r'€\s*(\d+[,.]?\d*)',
            r'(\d+[,.]?\d*)\s*€',
            r'(\d+[,.]?\d*)\s*eur'
        ]
        
        for pattern in eur_patterns:
            match = re.search(pattern, fee_string)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = float(amount_str)
                    
                    # Convert to annual if needed
                    if 'semester' in fee_string and amount < 10000:
                        amount *= 2
                    
                    return amount
                except ValueError:
                    continue
        
        # Handle SEK conversion
        sek_patterns = [r'sek\s*(\d+[,.]?\d*)', r'(\d+[,.]?\d*)\s*sek']
        
        for pattern in sek_patterns:
            match = re.search(pattern, fee_string)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    sek_amount = float(amount_str)
                    eur_amount = sek_amount / 11.0  # Rough conversion
                    
                    if 'semester' in fee_string and eur_amount < 10000:
                        eur_amount *= 2
                    
                    return eur_amount
                except ValueError:
                    continue
        
        # Default high cost for unknown
        return 15000.0
    
    def calculate_roi_score(self, school_id: str, cost: float) -> float:
        """Calculate Return on Investment score"""
        school = self.schools.get(school_id, {})
        
        # Base ROI factors
        country = school.get('country', '')
        program = school.get('program', '')
        
        # Country-specific ROI factors (work visa length, salary prospects, etc.)
        country_factors = {
            'Estonia': 0.75,    # EU access, lower salaries
            'Finland': 0.85,    # Good tech sector, high taxes
            'Sweden': 0.80,     # Strong tech, high cost of living
            'Germany': 0.90,    # Strong economy, good opportunities
            'Netherlands': 0.95, # Tech hub, good salaries
            'Denmark': 0.85     # High salaries, very high costs
        }
        
        country_factor = country_factors.get(country, 0.7)
        
        # Program-specific factors
        program_factors = {
            'cybersecurity': 1.2,  # High demand field
            'computer science': 1.0,
            'engineering': 0.9
        }
        
        program_lower = program.lower()
        program_factor = 1.0
        
        for key, factor in program_factors.items():
            if key in program_lower:
                program_factor = factor
                break
        
        # Cost efficiency (inverse relationship)
        if cost <= 0:
            cost_factor = 2.0  # Free education is excellent ROI
        elif cost <= 5000:
            cost_factor = 1.5
        elif cost <= 10000:
            cost_factor = 1.2
        elif cost <= 15000:
            cost_factor = 1.0
        elif cost <= 25000:
            cost_factor = 0.8
        else:
            cost_factor = 0.6
        
        # Priority factor (assumes priority correlates with opportunity)
        priority = school.get('priority_level', 'medium')
        priority_factors = {'high': 1.2, 'medium': 1.0, 'low': 0.8}
        priority_factor = priority_factors.get(priority, 1.0)
        
        roi_score = country_factor * program_factor * cost_factor * priority_factor
        
        return min(roi_score, 2.0)  # Cap at 2.0
    
    def calculate_prestige_score(self, school_id: str) -> float:
        """Calculate prestige/ranking score"""
        school = self.schools.get(school_id, {})
        
        # Simplified prestige scoring based on known factors
        school_name = school.get('full_name', '').lower()
        
        # High prestige indicators
        prestige_keywords = {
            'aalto': 1.0,           # Top Nordic tech university
            'tallinn': 0.85,        # Strong in tech, NATO center
            'linköping': 0.75,      # Good engineering school
            'darmstadt': 0.70,      # Applied sciences focus
        }
        
        prestige_score = 0.6  # Default score
        
        for keyword, score in prestige_keywords.items():
            if keyword in school_name:
                prestige_score = score
                break
        
        # Adjust based on program specificity
        program = school.get('program', '').lower()
        if 'cybersecurity' in program:
            prestige_score *= 1.1  # Bonus for specialized program
        
        return prestige_score
    
    def calculate_program_fit_score(self, school_id: str) -> float:
        """Calculate program fit based on research interests and career goals"""
        school = self.schools.get(school_id, {})
        
        # Research interest alignment
        program = school.get('program', '').lower()
        
        # Your research interests alignment
        research_alignments = {
            'cybersecurity': 1.0,
            'quantum': 0.9,
            'security': 1.0,
            'ai': 0.8,
            'machine learning': 0.8,
            'computer science': 0.7
        }
        
        fit_score = 0.6  # Default
        
        for interest, score in research_alignments.items():
            if interest in program:
                fit_score = max(fit_score, score)
        
        # Adjust based on validation confidence
        validation_result = self.validation_data.get('results', {}).get(school_id, {})
        confidence = validation_result.get('confidence_score', 0.5)
        fit_score *= (0.7 + confidence * 0.3)  # Confidence affects fit
        
        return fit_score
    
    def create_school_risk_profile(self, school_id: str) -> SchoolRiskProfile:
        """Create comprehensive risk profile for a school"""
        school = self.schools.get(school_id, {})
        
        # Calculate core metrics
        admission_prob = self.calculate_admission_probability(school_id)
        cost = self.extract_cost_eur(school.get('tuition_fee', ''))
        roi_score = self.calculate_roi_score(school_id, cost)
        prestige_score = self.calculate_prestige_score(school_id)
        fit_score = self.calculate_program_fit_score(school_id)
        
        # Determine risk category
        if admission_prob <= self.risk_thresholds['reach'][1]:
            risk_category = 'reach'
        elif admission_prob <= self.risk_thresholds['target'][1]:
            risk_category = 'target'
        else:
            risk_category = 'safe'
        
        # Calculate overall score
        overall_score = (
            self.score_weights['admission_probability'] * admission_prob +
            self.score_weights['cost_efficiency'] * (roi_score / 2.0) +
            self.score_weights['prestige'] * prestige_score +
            self.score_weights['program_fit'] * fit_score +
            self.score_weights['career_prospects'] * roi_score / 2.0
        )
        
        # Confidence level
        validation_result = self.validation_data.get('results', {}).get(school_id, {})
        confidence = validation_result.get('confidence_score', 0.5)
        
        return SchoolRiskProfile(
            school_id=school_id,
            school_name=school.get('full_name', school_id),
            risk_category=risk_category,
            admission_probability=admission_prob,
            cost_eur=cost,
            roi_score=roi_score,
            prestige_score=prestige_score,
            fit_score=fit_score,
            overall_score=overall_score,
            confidence_level=confidence
        )
    
    def analyze_portfolio_risk(self, school_profiles: List[SchoolRiskProfile]) -> PortfolioAnalysis:
        """Analyze overall portfolio risk and balance"""
        if not school_profiles:
            return PortfolioAnalysis(
                total_risk_score=10.0,
                risk_distribution={},
                expected_acceptances=0.0,
                cost_efficiency=0.0,
                diversification_score=0.0,
                recommendations=['No schools in portfolio'],
                optimal_changes=[]
            )
        
        # Calculate risk distribution
        total_schools = len(school_profiles)
        risk_counts = {'reach': 0, 'target': 0, 'safe': 0}
        
        for profile in school_profiles:
            risk_counts[profile.risk_category] += 1
        
        risk_distribution = {
            category: count / total_schools 
            for category, count in risk_counts.items()
        }
        
        # Calculate total risk score (0-10 scale)
        # Higher percentage of reach schools = higher risk
        risk_score = (
            risk_distribution.get('reach', 0) * 8 +
            risk_distribution.get('target', 0) * 5 +
            risk_distribution.get('safe', 0) * 2
        )
        
        # Expected acceptances (probabilistic)
        expected_acceptances = sum(p.admission_probability for p in school_profiles)
        
        # Cost efficiency
        if school_profiles:
            avg_cost = sum(p.cost_eur for p in school_profiles) / len(school_profiles)
            avg_roi = sum(p.roi_score for p in school_profiles) / len(school_profiles)
            cost_efficiency = avg_roi / (avg_cost / 10000) if avg_cost > 0 else avg_roi
        else:
            cost_efficiency = 0.0
        
        # Diversification score
        # Based on how close the distribution is to optimal
        diversification_penalties = []
        for category, optimal_pct in self.optimal_portfolio.items():
            actual_pct = risk_distribution.get(category, 0)
            penalty = abs(actual_pct - optimal_pct)
            diversification_penalties.append(penalty)
        
        diversification_score = 1.0 - (sum(diversification_penalties) / 2.0)
        diversification_score = max(0.0, diversification_score)
        
        # Generate recommendations
        recommendations = self.generate_portfolio_recommendations(
            risk_distribution, school_profiles, risk_score
        )
        
        # Generate optimal changes
        optimal_changes = self.suggest_optimal_changes(risk_distribution, school_profiles)
        
        return PortfolioAnalysis(
            total_risk_score=risk_score,
            risk_distribution=risk_distribution,
            expected_acceptances=expected_acceptances,
            cost_efficiency=cost_efficiency,
            diversification_score=diversification_score,
            recommendations=recommendations,
            optimal_changes=optimal_changes
        )
    
    def generate_portfolio_recommendations(self, 
                                         risk_distribution: Dict[str, float], 
                                         profiles: List[SchoolRiskProfile],
                                         risk_score: float) -> List[str]:
        """Generate strategic portfolio recommendations"""
        recommendations = []
        
        # Risk level assessment
        if risk_score >= 8:
            recommendations.append("🚨 投資組合風險過高！建議增加更多 'Safe' 或 'Target' 學校")
        elif risk_score >= 6:
            recommendations.append("⚠️ 投資組合風險偏高，考慮平衡風險分佈")
        elif risk_score <= 3:
            recommendations.append("💡 投資組合過於保守，可考慮申請1-2所衝刺學校")
        else:
            recommendations.append("✅ 投資組合風險適中，分佈相對均衡")
        
        # Distribution-specific recommendations
        reach_pct = risk_distribution.get('reach', 0)
        target_pct = risk_distribution.get('target', 0)
        safe_pct = risk_distribution.get('safe', 0)
        
        if reach_pct > 0.4:
            recommendations.append("📉 'Reach' 學校比例過高，建議調整為25%以下")
        elif reach_pct < 0.1:
            recommendations.append("📈 考慮申請1-2所衝刺學校，增加成功天花板")
        
        if target_pct < 0.3:
            recommendations.append("🎯 'Target' 學校不足，建議增加到40-60%範圍")
        
        if safe_pct < 0.2:
            recommendations.append("🛡️ 'Safe' 學校不足，建議至少保留20%作為保底選項")
        
        # Cost optimization
        high_cost_schools = [p for p in profiles if p.cost_eur > 20000]
        if len(high_cost_schools) > len(profiles) * 0.6:
            recommendations.append("💰 高學費學校過多，考慮增加免學費或低學費選項")
        
        # ROI optimization
        low_roi_schools = [p for p in profiles if p.roi_score < 0.8]
        if len(low_roi_schools) > len(profiles) * 0.5:
            recommendations.append("📊 投資回報率偏低，重新評估學校選擇的職涯價值")
        
        # Expected acceptances
        expected = sum(p.admission_probability for p in profiles)
        if expected < 1.0:
            recommendations.append("⚡ 預期錄取數量偏低，建議增加學校數量或調整選校策略")
        elif expected > 3.0:
            recommendations.append("🎯 預期錄取數量充足，可專注於提升申請品質")
        
        return recommendations
    
    def suggest_optimal_changes(self, 
                               current_distribution: Dict[str, float],
                               profiles: List[SchoolRiskProfile]) -> List[Dict[str, Any]]:
        """Suggest specific changes to optimize portfolio"""
        changes = []
        
        total_schools = len(profiles)
        if total_schools == 0:
            return changes
        
        # Calculate optimal counts
        optimal_counts = {
            category: round(total_schools * pct)
            for category, pct in self.optimal_portfolio.items()
        }
        
        # Calculate current counts
        current_counts = {
            'reach': len([p for p in profiles if p.risk_category == 'reach']),
            'target': len([p for p in profiles if p.risk_category == 'target']),
            'safe': len([p for p in profiles if p.risk_category == 'safe'])
        }
        
        # Suggest additions
        for category, optimal_count in optimal_counts.items():
            current_count = current_counts.get(category, 0)
            
            if current_count < optimal_count:
                deficit = optimal_count - current_count
                changes.append({
                    'type': 'add',
                    'category': category,
                    'count': deficit,
                    'description': f"建議增加 {deficit} 所 '{category}' 類別學校",
                    'examples': self.get_school_examples(category)
                })
        
        # Suggest removals or reclassifications
        for category, optimal_count in optimal_counts.items():
            current_count = current_counts.get(category, 0)
            
            if current_count > optimal_count:
                excess = current_count - optimal_count
                # Find lowest scoring schools in this category
                category_schools = [p for p in profiles if p.risk_category == category]
                category_schools.sort(key=lambda x: x.overall_score)
                
                for i in range(min(excess, len(category_schools))):
                    school = category_schools[i]
                    changes.append({
                        'type': 'consider_removing',
                        'school_id': school.school_id,
                        'school_name': school.school_name,
                        'category': category,
                        'reason': f"該校在 '{category}' 類別中得分較低",
                        'score': school.overall_score
                    })
        
        return changes
    
    def get_school_examples(self, category: str) -> List[str]:
        """Get example schools for each risk category"""
        examples = {
            'reach': [
                "ETH Zurich (瑞士)",
                "TU Delft (荷蘭)", 
                "KTH Royal Institute (瑞典)",
                "University of Edinburgh (英國)"
            ],
            'target': [
                "University of Twente (荷蘭)",
                "Université libre de Bruxelles (比利時)",
                "University of Oslo (挪威)",
                "Chalmers University (瑞典)"
            ],
            'safe': [
                "University of Limerick (愛爾蘭)",
                "Tampere University (芬蘭)",
                "University of Tartu (愛沙尼亞)",
                "Masaryk University (捷克)"
            ]
        }
        
        return examples.get(category, [])
    
    def run_portfolio_analysis(self) -> Dict[str, Any]:
        """Run complete portfolio risk analysis"""
        print("📊 Running portfolio risk analysis...")
        
        # Get active schools
        active_schools = [
            school_id for school_id, school in self.schools.items() 
            if school.get('status') == 'active'
        ]
        
        if not active_schools:
            print("⚠️  No active schools found for analysis")
            return {
                'error': 'No active schools',
                'suggestion': 'Add schools to source_data/schools.yml with status: active'
            }
        
        # Create risk profiles for all schools
        school_profiles = []
        for school_id in active_schools:
            print(f"📈 Analyzing risk profile: {school_id}")
            profile = self.create_school_risk_profile(school_id)
            school_profiles.append(profile)
        
        # Analyze portfolio
        portfolio_analysis = self.analyze_portfolio_risk(school_profiles)
        
        # Generate report
        report_content = self.generate_portfolio_report(portfolio_analysis, school_profiles)
        
        # Save report
        report_file = self.output_dir / "risk_portfolio_analysis.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📋 Risk portfolio analysis saved to {report_file}")
        
        # Save structured data
        portfolio_data = {
            'analysis_date': datetime.now().isoformat(),
            'portfolio_metrics': {
                'total_risk_score': portfolio_analysis.total_risk_score,
                'expected_acceptances': portfolio_analysis.expected_acceptances,
                'cost_efficiency': portfolio_analysis.cost_efficiency,
                'diversification_score': portfolio_analysis.diversification_score
            },
            'risk_distribution': portfolio_analysis.risk_distribution,
            'school_profiles': [
                {
                    'school_id': p.school_id,
                    'school_name': p.school_name,
                    'risk_category': p.risk_category,
                    'admission_probability': p.admission_probability,
                    'cost_eur': p.cost_eur,
                    'roi_score': p.roi_score,
                    'overall_score': p.overall_score
                }
                for p in school_profiles
            ]
        }
        
        data_file = self.output_dir / "risk_portfolio_data.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(portfolio_data, f, indent=2)
        
        # Return summary
        return {
            'total_schools': len(school_profiles),
            'risk_score': portfolio_analysis.total_risk_score,
            'expected_acceptances': portfolio_analysis.expected_acceptances,
            'diversification_score': portfolio_analysis.diversification_score,
            'recommendations_count': len(portfolio_analysis.recommendations),
            'suggested_changes': len(portfolio_analysis.optimal_changes),
            'report_file': str(report_file)
        }
    
    def generate_portfolio_report(self, analysis: PortfolioAnalysis, 
                                 profiles: List[SchoolRiskProfile]) -> str:
        """Generate comprehensive portfolio analysis report"""
        report_lines = [
            "# 📊 大學申請風險投資組合分析報告",
            "",
            f"**分析時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**投資組合規模**: {len(profiles)} 所大學",
            f"**總體風險分數**: {analysis.total_risk_score:.1f}/10",
            ""
        ]
        
        # Risk assessment overview
        if analysis.total_risk_score >= 8:
            risk_assessment = "🚨 高風險 - 需要立即調整策略"
            risk_color = "danger"
        elif analysis.total_risk_score >= 6:
            risk_assessment = "⚠️ 中高風險 - 建議優化平衡"
            risk_color = "warning"
        elif analysis.total_risk_score >= 4:
            risk_assessment = "✅ 適中風險 - 策略相對均衡"
            risk_color = "success"
        else:
            risk_assessment = "💤 低風險 - 可能過於保守"
            risk_color = "info"
        
        report_lines.extend([
            "## 📊 風險評估總覽",
            "",
            f"**風險等級**: {risk_assessment}",
            f"**預期錄取數量**: {analysis.expected_acceptances:.1f} 所",
            f"**投資組合多樣化**: {analysis.diversification_score:.1%}",
            f"**成本效率**: {analysis.cost_efficiency:.2f}",
            ""
        ])
        
        # Risk distribution visualization
        report_lines.extend([
            "## 🎯 風險分佈分析",
            "",
            "| 風險類別 | 目前比例 | 理想比例 | 差距 | 評估 |",
            "|----------|----------|----------|------|------|"
        ])
        
        for category in ['safe', 'target', 'reach']:
            current_pct = analysis.risk_distribution.get(category, 0)
            optimal_pct = self.optimal_portfolio[category]
            gap = current_pct - optimal_pct
            
            if abs(gap) <= 0.1:
                assessment = "✅ 理想"
            elif abs(gap) <= 0.2:
                assessment = "⚠️ 可接受"
            else:
                assessment = "❌ 需調整"
            
            category_names = {'safe': '保底', 'target': '目標', 'reach': '衝刺'}
            
            report_lines.append(
                f"| {category_names[category]} | {current_pct:.1%} | "
                f"{optimal_pct:.1%} | {gap:+.1%} | {assessment} |"
            )
        
        report_lines.append("")
        
        # Individual school analysis
        report_lines.extend([
            "## 🏛️ 個別學校風險分析",
            "",
            "| 學校 | 風險類別 | 錄取機率 | 年學費 | ROI | 總分 | 推薦度 |",
            "|------|----------|----------|--------|-----|------|--------|"
        ])
        
        # Sort by overall score
        profiles_sorted = sorted(profiles, key=lambda x: x.overall_score, reverse=True)
        
        for profile in profiles_sorted:
            category_icons = {'safe': '🛡️', 'target': '🎯', 'reach': '🚀'}
            
            # Recommendation based on score and category balance
            if profile.overall_score >= 0.8:
                recommendation = "⭐ 強推"
            elif profile.overall_score >= 0.6:
                recommendation = "✅ 推薦"
            elif profile.overall_score >= 0.4:
                recommendation = "⚠️ 考慮"
            else:
                recommendation = "❌ 重評"
            
            report_lines.append(
                f"| {profile.school_name} | "
                f"{category_icons.get(profile.risk_category, '❓')} {profile.risk_category} | "
                f"{profile.admission_probability:.1%} | "
                f"€{profile.cost_eur:,.0f} | "
                f"{profile.roi_score:.2f} | "
                f"{profile.overall_score:.2f} | "
                f"{recommendation} |"
            )
        
        report_lines.append("")
        
        # Strategic recommendations
        if analysis.recommendations:
            report_lines.extend([
                "## 💡 策略建議",
                ""
            ])
            
            for i, rec in enumerate(analysis.recommendations, 1):
                report_lines.append(f"{i}. {rec}")
            
            report_lines.append("")
        
        # Portfolio optimization suggestions
        if analysis.optimal_changes:
            report_lines.extend([
                "## 🔄 投資組合優化建議",
                ""
            ])
            
            additions = [c for c in analysis.optimal_changes if c['type'] == 'add']
            removals = [c for c in analysis.optimal_changes if c['type'] == 'consider_removing']
            
            if additions:
                report_lines.extend([
                    "### 📈 建議增加",
                    ""
                ])
                
                for change in additions:
                    report_lines.extend([
                        f"**{change['description']}**",
                        "",
                        "推薦學校選項:",
                    ])
                    
                    for example in change.get('examples', []):
                        report_lines.append(f"- {example}")
                    
                    report_lines.append("")
            
            if removals:
                report_lines.extend([
                    "### 📉 考慮調整",
                    ""
                ])
                
                for change in removals:
                    report_lines.append(
                        f"- **{change['school_name']}**: {change['reason']} "
                        f"(得分: {change['score']:.2f})"
                    )
                
                report_lines.append("")
        
        # Financial analysis
        total_cost = sum(p.cost_eur for p in profiles)
        avg_cost = total_cost / len(profiles) if profiles else 0
        
        report_lines.extend([
            "## 💰 財務分析",
            "",
            f"**總申請成本預估**: €{total_cost:,.0f}",
            f"**平均每校成本**: €{avg_cost:,.0f}",
            f"**預算符合度**: {len([p for p in profiles if p.cost_eur <= self.personal_profile['target_budget_eur']]) / len(profiles):.1%}",
            ""
        ])
        
        # Risk scenarios
        report_lines.extend([
            "## 🎲 情境分析",
            "",
            "### 樂觀情境 (90%置信區間上限)",
            f"- 預期錄取: {min(len(profiles), analysis.expected_acceptances + 1.5):.0f} 所",
            f"- 最佳情況: 獲得所有Target和Safe學校錄取",
            "",
            "### 現實情境 (50%機率)",
            f"- 預期錄取: {analysis.expected_acceptances:.1f} 所",
            f"- 典型情況: 按機率模型的預期結果",
            "",
            "### 悲觀情境 (10%置信區間下限)",
            f"- 預期錄取: {max(0, analysis.expected_acceptances - 1.0):.0f} 所",
            f"- 最差情況: 僅獲得部分Safe學校錄取",
            ""
        ])
        
        # Action plan
        report_lines.extend([
            "## 🎯 行動計劃",
            "",
            "### 短期行動 (1-2週內)",
        ])
        
        high_priority_actions = []
        if analysis.total_risk_score >= 7:
            high_priority_actions.append("🚨 立即調整投資組合，增加Safe學校")
        
        if analysis.expected_acceptances < 1.0:
            high_priority_actions.append("📈 緊急增加申請學校數量")
        
        if not high_priority_actions:
            high_priority_actions.append("✅ 當前策略良好，專注提升申請品質")
        
        for action in high_priority_actions:
            report_lines.append(f"- {action}")
        
        report_lines.extend([
            "",
            "### 中期優化 (1個月內)",
            "- 根據上述建議調整學校清單",
            "- 重新運行風險分析驗證改進效果", 
            "- 針對高ROI學校進行深度研究",
            "",
            "### 長期監控",
            "- 每月重新評估投資組合平衡",
            "- 根據申請進度調整風險偏好",
            "- 收集更多學校數據完善模型",
            "",
            "---",
            "",
            "## 📞 專業建議",
            "",
            "此分析基於量化模型和公開數據。建議：",
            "- 🤖 定期重新運行分析以反映最新情況",
            "- 👥 與專業申請顧問討論個人化策略",
            "- 📚 參考實際錄取數據驗證模型準確性",
            "",
            f"*報告生成於 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by Risk Portfolio Balancer v2.0*"
        ])
        
        return "\n".join(report_lines)

def main():
    """Main risk portfolio analysis execution"""
    balancer = RiskPortfolioBalancer()
    
    try:
        # Run portfolio analysis
        result = balancer.run_portfolio_analysis()
        
        if 'error' in result:
            print(f"❌ Analysis failed: {result['error']}")
            if 'suggestion' in result:
                print(f"💡 {result['suggestion']}")
            return 1
        
        # Print summary
        print(f"\n📊 Risk Portfolio Analysis Summary:")
        print(f"   Total Schools: {result['total_schools']}")
        print(f"   Risk Score: {result['risk_score']:.1f}/10")
        print(f"   Expected Acceptances: {result['expected_acceptances']:.1f}")
        print(f"   Diversification: {result['diversification_score']:.1%}")
        print(f"   Recommendations: {result['recommendations_count']}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Risk portfolio analysis failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
