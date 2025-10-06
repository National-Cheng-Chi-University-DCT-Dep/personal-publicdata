#!/usr/bin/env python3
"""
Cross-Document Narrative Consistency Checker

Features:
- LLM-powered narrative analysis across CV, SOP, and recommendation materials
- Consistency scoring and conflict detection
- Story coherence validation
- Personalized improvement suggestions
- Multi-document semantic alignment analysis
"""

import os
import sys
import json
import yaml
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
import re

@dataclass
class NarrativeElement:
    document_type: str  # CV, SOP, Recommendation
    content: str
    themes: List[str]
    keywords: List[str]
    tone: str
    emphasis: List[str]

@dataclass
class ConsistencyAnalysis:
    overall_score: float  # 0-100
    conflicts: List[Dict[str, Any]]
    strengths: List[str]
    suggestions: List[str]
    theme_alignment: Dict[str, float]
    narrative_coherence: float

class NarrativeConsistencyChecker:
    """Cross-document narrative consistency analysis system"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.source_data_dir = self.base_dir / "source_data"
        self.output_dir = self.base_dir / "final_applications"
        self.templates_dir = self.base_dir / "templates"
        
        # Load narrative configuration
        self.load_narrative_profile()
        self.setup_llm_integration()
    
    def load_narrative_profile(self):
        """Load user's core narrative themes and keywords"""
        profile_file = self.source_data_dir / "narrative_profile.yml"
        
        # Default narrative profile (will be created if not exists)
        default_profile = {
            'core_themes': [
                '成長曲線',  # Growth trajectory
                '雲端安全架構',  # Cloud security architecture
                '量子計算潛力',  # Quantum computing potential
                '跨領域整合',  # Cross-domain integration
                '實務導向創新'  # Practice-oriented innovation
            ],
            'narrative_strategy': 'technical_leader_with_research_vision',
            'key_experiences': [
                'Taiwan Stock Exchange cybersecurity consulting',
                'Twister5 team leadership',
                'Academic excellence transformation',
                'International perspective development'
            ],
            'target_image': 'experienced_practitioner_seeking_advanced_research',
            'avoid_contradictions': [
                'pure_academic_vs_industry_experience',
                'individual_vs_team_accomplishments',
                'technical_depth_vs_breadth_claims'
            ]
        }
        
        if profile_file.exists():
            with open(profile_file, 'r', encoding='utf-8') as f:
                self.narrative_profile = yaml.safe_load(f)
        else:
            # Create default profile
            self.narrative_profile = default_profile
            with open(profile_file, 'w', encoding='utf-8') as f:
                yaml.dump(default_profile, f, default_flow_style=False, allow_unicode=True)
            
            print(f"📝 Created default narrative profile: {profile_file}")
    
    def setup_llm_integration(self):
        """Setup LLM API integration"""
        # This is a placeholder for LLM integration
        # In production, you would use OpenAI API, Anthropic Claude, or other LLM services
        self.llm_available = False
        self.api_key = os.environ.get('OPENAI_API_KEY')
        
        if self.api_key:
            self.llm_available = True
            print("✅ LLM integration ready")
        else:
            print("⚠️  LLM API key not found. Using rule-based analysis.")
    
    def extract_document_content(self, file_path: Path) -> str:
        """Extract content from document file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove markdown formatting for analysis
            content = re.sub(r'#+\s*', '', content)  # Headers
            content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Bold
            content = re.sub(r'\*(.*?)\*', r'\1', content)  # Italic
            content = re.sub(r'\[.*?\]\(.*?\)', '', content)  # Links
            content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)  # Code blocks
            
            return content.strip()
        except Exception as e:
            print(f"⚠️  Could not read {file_path}: {e}")
            return ""
    
    def analyze_document_themes(self, content: str, doc_type: str) -> NarrativeElement:
        """Analyze themes and emphasis in a document"""
        # Extract key themes based on content analysis
        themes = []
        keywords = []
        emphasis = []
        
        # Theme detection based on keywords
        theme_keywords = {
            '成長曲線': ['growth', 'improvement', 'development', 'progression', 'advancement', 'evolution', 'learning'],
            '雲端安全架構': ['cloud', 'security', 'architecture', 'infrastructure', 'AWS', 'cybersecurity', 'defense'],
            '量子計算潛力': ['quantum', 'computing', 'cryptography', 'post-quantum', 'algorithm', 'qiskit'],
            '跨領域整合': ['interdisciplinary', 'integration', 'collaboration', 'cross-functional', 'diverse'],
            '實務導向創新': ['practical', 'implementation', 'real-world', 'industry', 'application', 'solution']
        }
        
        content_lower = content.lower()
        
        for theme, theme_words in theme_keywords.items():
            if any(word in content_lower for word in theme_words):
                themes.append(theme)
                # Count frequency for emphasis
                frequency = sum(content_lower.count(word) for word in theme_words)
                if frequency >= 3:
                    emphasis.append(theme)
        
        # Extract key technical keywords
        tech_keywords = [
            'python', 'cybersecurity', 'machine learning', 'ai', 'cloud', 'security',
            'quantum', 'cryptography', 'blockchain', 'devops', 'automation',
            'leadership', 'management', 'consulting', 'architecture', 'engineering'
        ]
        
        for keyword in tech_keywords:
            if keyword in content_lower:
                keywords.append(keyword)
        
        # Analyze tone (simplified)
        formal_indicators = ['furthermore', 'therefore', 'consequently', 'moreover', 'research', 'academic']
        personal_indicators = ['i', 'my', 'personally', 'believe', 'passion', 'excited', 'dream']
        
        formal_count = sum(content_lower.count(word) for word in formal_indicators)
        personal_count = sum(content_lower.count(word) for word in personal_indicators)
        
        if formal_count > personal_count:
            tone = "formal_academic"
        elif personal_count > formal_count:
            tone = "personal_narrative"
        else:
            tone = "balanced"
        
        return NarrativeElement(
            document_type=doc_type,
            content=content[:500],  # First 500 chars for analysis
            themes=themes,
            keywords=keywords,
            tone=tone,
            emphasis=emphasis
        )
    
    def call_llm_api(self, prompt: str) -> Optional[str]:
        """Call LLM API for advanced analysis"""
        if not self.llm_available:
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are an expert admissions consultant analyzing university application documents for narrative consistency and coherence.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 1000,
                'temperature': 0.3
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"⚠️  LLM API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠️  LLM API call failed: {e}")
            return None
    
    def analyze_cross_document_consistency(self, documents: List[NarrativeElement]) -> ConsistencyAnalysis:
        """Analyze consistency across multiple documents"""
        conflicts = []
        strengths = []
        suggestions = []
        theme_alignment = {}
        
        # Analyze theme consistency
        all_themes = set()
        for doc in documents:
            all_themes.update(doc.themes)
        
        for theme in all_themes:
            docs_with_theme = [doc for doc in documents if theme in doc.themes]
            emphasis_docs = [doc for doc in documents if theme in doc.emphasis]
            
            alignment_score = len(docs_with_theme) / len(documents)
            theme_alignment[theme] = alignment_score
            
            if alignment_score >= 0.8:
                strengths.append(f"強力主題一致性: '{theme}' 在多數文件中都有體現")
            elif alignment_score <= 0.3:
                conflicts.append({
                    'type': 'theme_inconsistency',
                    'severity': 'medium',
                    'description': f"主題 '{theme}' 只在部分文件中出現，可能造成敘事不一致",
                    'affected_documents': [doc.document_type for doc in docs_with_theme],
                    'suggestion': f"考慮在所有文件中更均勻地體現 '{theme}' 主題"
                })
        
        # Analyze tone consistency
        tones = [doc.tone for doc in documents]
        if len(set(tones)) > 2:
            conflicts.append({
                'type': 'tone_inconsistency',
                'severity': 'high',
                'description': '文件間語調差異過大，可能影響整體形象一致性',
                'affected_documents': [f"{doc.document_type}({doc.tone})" for doc in documents],
                'suggestion': '統一所有文件的語調風格，建議使用平衡的學術-個人敘事風格'
            })
        
        # Analyze keyword overlap
        all_keywords = []
        for doc in documents:
            all_keywords.extend(doc.keywords)
        
        keyword_frequency = {}
        for keyword in all_keywords:
            keyword_frequency[keyword] = all_keywords.count(keyword)
        
        # Check for missing core keywords across documents
        core_keywords = ['cybersecurity', 'security', 'quantum', 'leadership', 'research']
        missing_keywords = []
        
        for keyword in core_keywords:
            if keyword_frequency.get(keyword, 0) < len(documents) * 0.5:
                missing_keywords.append(keyword)
        
        if missing_keywords:
            suggestions.append(f"考慮在更多文件中加入核心關鍵字: {', '.join(missing_keywords)}")
        
        # Analyze emphasis alignment with strategy
        target_strategy = self.narrative_profile.get('narrative_strategy', '')
        if 'technical_leader' in target_strategy:
            leadership_mentions = sum(1 for doc in documents if 'leadership' in doc.keywords)
            if leadership_mentions < len(documents) * 0.6:
                suggestions.append("作為技術領導者的定位需要在更多文件中體現領導經驗")
        
        # Calculate overall consistency score
        consistency_factors = [
            len(conflicts) == 0,  # No conflicts
            sum(theme_alignment.values()) / len(theme_alignment) if theme_alignment else 0.5,  # Theme alignment
            len(set(tones)) <= 2,  # Tone consistency
            len(missing_keywords) <= 1  # Keyword coverage
        ]
        
        narrative_coherence = sum(consistency_factors) / len(consistency_factors) * 100
        
        # Generate LLM-powered analysis if available
        if self.llm_available:
            llm_analysis = self.get_llm_narrative_analysis(documents)
            if llm_analysis:
                suggestions.extend(llm_analysis.get('suggestions', []))
        
        return ConsistencyAnalysis(
            overall_score=narrative_coherence,
            conflicts=conflicts,
            strengths=strengths,
            suggestions=suggestions,
            theme_alignment=theme_alignment,
            narrative_coherence=narrative_coherence
        )
    
    def get_llm_narrative_analysis(self, documents: List[NarrativeElement]) -> Optional[Dict]:
        """Get advanced LLM-powered narrative analysis"""
        if not self.llm_available:
            return None
        
        # Prepare document summaries for LLM
        doc_summaries = []
        for doc in documents:
            doc_summaries.append(f"{doc.document_type}: {doc.content[:200]}...")
        
        prompt = f"""
        Analyze the narrative consistency across these university application documents for a cybersecurity professional applying to graduate programs:

        CORE NARRATIVE THEMES: {', '.join(self.narrative_profile['core_themes'])}
        TARGET IMAGE: {self.narrative_profile.get('target_image', '')}

        DOCUMENTS:
        {chr(10).join(doc_summaries)}

        Please provide analysis in this JSON format:
        {{
            "consistency_score": (0-100),
            "narrative_strengths": ["strength1", "strength2"],
            "potential_conflicts": ["conflict1", "conflict2"],
            "suggestions": ["suggestion1", "suggestion2"],
            "overall_impression": "brief summary"
        }}
        """
        
        llm_response = self.call_llm_api(prompt)
        
        if llm_response:
            try:
                # Try to parse JSON response
                import json
                return json.loads(llm_response)
            except:
                # If JSON parsing fails, extract insights manually
                return {
                    'suggestions': [
                        '建議使用LLM API進行更深度的語意分析',
                        '考慮專業申請顧問的人工審查'
                    ]
                }
        
        return None
    
    def find_application_documents(self) -> List[Tuple[str, Path]]:
        """Find all application documents for analysis"""
        documents = []
        
        # Look for CV files
        cv_files = list(self.output_dir.rglob("CV_*.md"))
        if cv_files:
            documents.append(("CV", cv_files[0]))  # Use first CV file
        
        # Look for SOP files
        sop_files = list(self.output_dir.rglob("SOP_*.md"))
        if sop_files:
            documents.append(("SOP", sop_files[0]))  # Use first SOP file
        
        # Look for recommendation brag sheet (if exists)
        brag_sheet_files = list(self.templates_dir.glob("*brag*sheet*.md"))
        if brag_sheet_files:
            documents.append(("Recommendation", brag_sheet_files[0]))
        
        # Also check templates
        cv_template = self.templates_dir / "cv_template.md"
        if cv_template.exists() and ("CV", cv_template) not in documents:
            documents.append(("CV_Template", cv_template))
        
        sop_template = self.templates_dir / "sop_master_template.md"
        if sop_template.exists():
            documents.append(("SOP_Template", sop_template))
        
        return documents
    
    def run_consistency_analysis(self) -> Dict[str, Any]:
        """Run complete narrative consistency analysis"""
        print("📖 Running cross-document narrative consistency analysis...")
        
        # Find documents to analyze
        document_files = self.find_application_documents()
        
        if not document_files:
            print("⚠️  No application documents found for analysis")
            return {
                'error': 'No documents found',
                'suggestion': 'Run document generation first: .\intelligence.ps1 docs'
            }
        
        # Analyze each document
        analyzed_documents = []
        for doc_type, file_path in document_files:
            print(f"📄 Analyzing {doc_type}: {file_path.name}")
            
            content = self.extract_document_content(file_path)
            if content:
                narrative_element = self.analyze_document_themes(content, doc_type)
                analyzed_documents.append(narrative_element)
        
        if not analyzed_documents:
            print("❌ No valid documents could be analyzed")
            return {'error': 'Document analysis failed'}
        
        # Perform consistency analysis
        consistency_analysis = self.analyze_cross_document_consistency(analyzed_documents)
        
        # Generate report
        report_content = self.generate_consistency_report(consistency_analysis, analyzed_documents)
        
        # Save report
        report_file = self.output_dir / "narrative_consistency_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📋 Narrative consistency report saved to {report_file}")
        
        # Return summary
        return {
            'overall_score': consistency_analysis.overall_score,
            'documents_analyzed': len(analyzed_documents),
            'conflicts_found': len(consistency_analysis.conflicts),
            'suggestions_provided': len(consistency_analysis.suggestions),
            'theme_alignment_avg': sum(consistency_analysis.theme_alignment.values()) / len(consistency_analysis.theme_alignment) if consistency_analysis.theme_alignment else 0,
            'report_file': str(report_file)
        }
    
    def generate_consistency_report(self, analysis: ConsistencyAnalysis, documents: List[NarrativeElement]) -> str:
        """Generate comprehensive narrative consistency report"""
        report_lines = [
            "# 📖 申請敘事一致性分析報告",
            "",
            f"**分析時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**分析文件數**: {len(documents)}",
            f"**整體一致性分數**: {analysis.overall_score:.1f}/100",
            ""
        ]
        
        # Overall assessment
        if analysis.overall_score >= 80:
            assessment = "🌟 優秀 - 您的申請敘事高度一致且連貫"
            color = "success"
        elif analysis.overall_score >= 60:
            assessment = "✅ 良好 - 申請敘事基本一致，有小幅改進空間"
            color = "warning"
        else:
            assessment = "⚠️ 需改進 - 申請敘事存在不一致之處，建議重新審視"
            color = "danger"
        
        report_lines.extend([
            "## 📊 總體評估",
            "",
            f"**{assessment}**",
            ""
        ])
        
        # Documents analyzed
        report_lines.extend([
            "## 📄 分析文件",
            "",
            "| 文件類型 | 主要主題 | 語調風格 | 關鍵字數量 |",
            "|----------|----------|----------|------------|"
        ])
        
        for doc in documents:
            themes_str = ", ".join(doc.themes[:3]) if doc.themes else "無明確主題"
            report_lines.append(
                f"| {doc.document_type} | {themes_str} | {doc.tone} | {len(doc.keywords)} |"
            )
        
        report_lines.append("")
        
        # Theme alignment analysis
        if analysis.theme_alignment:
            report_lines.extend([
                "## 🎯 主題一致性分析",
                "",
                "| 核心主題 | 覆蓋率 | 評估 |",
                "|----------|---------|------|"
            ])
            
            for theme, alignment in analysis.theme_alignment.items():
                if alignment >= 0.8:
                    assessment = "✅ 優秀"
                elif alignment >= 0.5:
                    assessment = "⚠️ 中等"
                else:
                    assessment = "❌ 不足"
                
                report_lines.append(f"| {theme} | {alignment:.1%} | {assessment} |")
            
            report_lines.append("")
        
        # Strengths
        if analysis.strengths:
            report_lines.extend([
                "## ✅ 敘事優勢",
                ""
            ])
            
            for strength in analysis.strengths:
                report_lines.append(f"- {strength}")
            
            report_lines.append("")
        
        # Conflicts and issues
        if analysis.conflicts:
            report_lines.extend([
                "## ⚠️ 發現的問題",
                ""
            ])
            
            for conflict in analysis.conflicts:
                severity_icon = {
                    'high': '🚨',
                    'medium': '⚠️',
                    'low': '💡'
                }
                
                icon = severity_icon.get(conflict.get('severity', 'medium'), '⚠️')
                report_lines.extend([
                    f"### {icon} {conflict.get('type', 'Unknown').replace('_', ' ').title()}",
                    "",
                    f"**問題描述**: {conflict.get('description', 'N/A')}",
                    f"**影響文件**: {', '.join(conflict.get('affected_documents', []))}",
                    f"**建議處理**: {conflict.get('suggestion', 'N/A')}",
                    ""
                ])
        
        # Suggestions for improvement
        if analysis.suggestions:
            report_lines.extend([
                "## 💡 改進建議",
                ""
            ])
            
            for i, suggestion in enumerate(analysis.suggestions, 1):
                report_lines.append(f"{i}. {suggestion}")
            
            report_lines.append("")
        
        # Core narrative profile
        report_lines.extend([
            "## 🎭 核心敘事策略",
            "",
            f"**目標形象**: {self.narrative_profile.get('target_image', 'N/A')}",
            f"**敘事策略**: {self.narrative_profile.get('narrative_strategy', 'N/A')}",
            "",
            "**核心主題**:",
        ])
        
        for theme in self.narrative_profile.get('core_themes', []):
            alignment_score = analysis.theme_alignment.get(theme, 0)
            status_icon = "✅" if alignment_score >= 0.7 else "⚠️" if alignment_score >= 0.4 else "❌"
            report_lines.append(f"- {status_icon} {theme} ({alignment_score:.1%} 覆蓋率)")
        
        # Action items
        report_lines.extend([
            "",
            "## 🎯 行動計畫",
            ""
        ])
        
        if analysis.overall_score >= 80:
            report_lines.extend([
                "您的申請敘事已經相當優秀！建議：",
                "1. 進行最終校對，確保細節完美",
                "2. 請專業顧問或資深申請者進行同儕評議",
                "3. 針對不同學校進行微調優化"
            ])
        else:
            report_lines.extend([
                "建議按以下優先級改進申請敘事：",
                "1. **高優先級**: 解決上述標記的衝突問題",
                "2. **中優先級**: 實施改進建議中的前3項",
                "3. **低優先級**: 增強主題一致性覆蓋率",
                "4. **持續**: 定期重新分析並優化"
            ])
        
        report_lines.extend([
            "",
            "---",
            "",
            "## 📞 進階支援",
            "",
            "如需更深度的敘事分析，建議：",
            "- 🤖 配置LLM API進行語意層面分析",
            "- 👥 尋求專業申請顧問意見",
            "- 📚 參考成功申請案例進行對比",
            "",
            f"*報告生成於 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by Narrative Consistency Checker v2.0*"
        ])
        
        return "\n".join(report_lines)

def main():
    """Main narrative consistency analysis execution"""
    checker = NarrativeConsistencyChecker()
    
    try:
        # Run consistency analysis
        result = checker.run_consistency_analysis()
        
        if 'error' in result:
            print(f"❌ Analysis failed: {result['error']}")
            if 'suggestion' in result:
                print(f"💡 {result['suggestion']}")
            return 1
        
        # Print summary
        print(f"\n📖 Narrative Consistency Analysis Summary:")
        print(f"   Overall Score: {result['overall_score']:.1f}/100")
        print(f"   Documents Analyzed: {result['documents_analyzed']}")
        print(f"   Conflicts Found: {result['conflicts_found']}")
        print(f"   Suggestions Provided: {result['suggestions_provided']}")
        print(f"   Theme Alignment: {result['theme_alignment_avg']:.1%}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Narrative consistency analysis failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
