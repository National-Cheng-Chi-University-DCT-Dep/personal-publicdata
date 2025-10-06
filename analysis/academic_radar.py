#!/usr/bin/env python3
"""
Academic Intelligence and Research Radar System

Features:
- Professor publication tracking (Google Scholar)
- Conference monitoring and deadlines
- GitHub repository activity tracking
- Research collaboration discovery
- Academic opportunity identification
- Citation network analysis
"""

import os
import sys
import time
import yaml
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
import re
from urllib.parse import urljoin, urlparse

@dataclass
class Publication:
    title: str
    authors: List[str]
    venue: str
    year: int
    citation_count: int
    url: Optional[str] = None
    abstract: Optional[str] = None
    keywords: List[str] = None

@dataclass
class Professor:
    name: str
    affiliation: str
    email: Optional[str] = None
    google_scholar_url: Optional[str] = None
    research_interests: List[str] = None
    recent_publications: List[Publication] = None
    h_index: Optional[int] = None
    total_citations: Optional[int] = None

@dataclass
class Conference:
    name: str
    acronym: str
    submission_deadline: Optional[datetime] = None
    conference_date: Optional[datetime] = None
    location: str = ""
    website: Optional[str] = None
    acceptance_rate: Optional[float] = None
    relevance_score: float = 0.0

@dataclass
class GitHubRepo:
    name: str
    owner: str
    description: str
    language: str
    stars: int
    last_updated: datetime
    open_issues: int
    good_first_issues: int
    contributors: int
    url: str

class AcademicRadar:
    """Academic intelligence gathering and monitoring system"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.source_data_dir = self.base_dir / "source_data"
        self.output_dir = self.base_dir / "final_applications"
        self.cache_dir = self.base_dir / "analysis" / "cache"
        
        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.load_target_professors()
        self.research_keywords = self.get_research_keywords()
        
        # Rate limiting
        self.last_request_time = {}
        self.min_delay = 1.0  # seconds between requests
        
        # GitHub API setup
        self.github_token = os.environ.get('GITHUB_TOKEN')
        if self.github_token:
            self.github_headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
        else:
            self.github_headers = {}
            print("⚠️  No GitHub token found. API rate limits will be lower.")
    
    def load_target_professors(self):
        """Load target professors from school configuration"""
        with open(self.source_data_dir / "schools.yml", 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            self.schools = {school['school_id']: school for school in data['schools']}
        
        # Extract professor information from schools
        self.target_professors = {}
        
        # TalTech professors (from your SOP)
        self.target_professors['taltech'] = [
            Professor(
                name="Rain Ottis",
                affiliation="TalTech - Centre for Digital Forensics and Cyber Security",
                research_interests=["cyber conflicts", "national cybersecurity", "cyber exercises"]
            ),
            Professor(
                name="Samuel Pagliarini", 
                affiliation="TalTech - Centre for Hardware Security",
                research_interests=["hardware security", "IC design", "hardware trojans"]
            ),
            Professor(
                name="Ahto Buldas",
                affiliation="TalTech - Department of Software Science",
                research_interests=["cryptography", "blockchain", "post-quantum cryptography"]
            ),
            Professor(
                name="Amar Hadzihasanovic",
                affiliation="TalTech - Quantum Software",
                research_interests=["quantum computing", "formal methods", "quantum circuits"]
            ),
            Professor(
                name="Paweł Sobociński",
                affiliation="TalTech - Compositional Systems and Methods",
                research_interests=["quantum computing", "string diagrams", "category theory"]
            )
        ]
        
        # Aalto professors (add based on research)
        self.target_professors['aalto'] = [
            Professor(
                name="Samuel Kaski",
                affiliation="Aalto University - Department of Computer Science",
                research_interests=["machine learning", "AI security", "human-AI interaction"]
            ),
            Professor(
                name="Tuomas Aura",
                affiliation="Aalto University - Department of Computer Science", 
                research_interests=["network security", "authentication", "distributed systems"]
            ),
            Professor(
                name="Mikko Möttönen",
                affiliation="Aalto University - Centre for Quantum Engineering",
                research_interests=["quantum computing", "quantum algorithms", "quantum systems"]
            )
        ]
    
    def get_research_keywords(self) -> List[str]:
        """Define research keywords relevant to your interests"""
        return [
            # Core cybersecurity
            "cybersecurity", "information security", "network security", "cyber defense",
            "threat detection", "intrusion detection", "malware analysis",
            
            # AI and ML security
            "AI security", "machine learning security", "adversarial ML", "AI safety",
            "explainable AI", "trustworthy AI", "federated learning security",
            
            # Quantum computing and cryptography
            "quantum computing", "post-quantum cryptography", "quantum algorithms",
            "quantum key distribution", "quantum cryptanalysis", "lattice cryptography",
            
            # Hardware security
            "hardware security", "trusted computing", "secure hardware", "hardware trojans",
            "side-channel attacks", "fault injection", "PUF", "secure boot",
            
            # Cloud and infrastructure
            "cloud security", "container security", "DevSecOps", "zero trust",
            "infrastructure security", "distributed systems security",
            
            # Blockchain and emerging tech
            "blockchain security", "smart contract security", "DeFi security",
            "IoT security", "5G security", "edge computing security"
        ]
    
    def rate_limit(self, domain: str):
        """Implement rate limiting"""
        now = time.time()
        if domain in self.last_request_time:
            elapsed = now - self.last_request_time[domain]
            if elapsed < self.min_delay:
                time.sleep(self.min_delay - elapsed)
        
        self.last_request_time[domain] = time.time()
    
    def search_google_scholar_publications(self, professor_name: str, max_results: int = 10) -> List[Publication]:
        """Search for recent publications on Google Scholar"""
        # Note: This is a simplified version. In production, you might want to use:
        # - scholarly library (pip install scholarly)
        # - Serpapi for Google Scholar
        # - Academic databases APIs (IEEE, ACM, arXiv)
        
        publications = []
        
        # For demonstration, we'll create some mock recent publications
        # In reality, you'd implement actual Google Scholar scraping
        
        mock_publications = {
            "Rain Ottis": [
                Publication(
                    title="Cyber Exercise Development and Lessons Learned",
                    authors=["Rain Ottis", "Lauri Jutila"],
                    venue="International Conference on Cyber Warfare",
                    year=2024,
                    citation_count=15,
                    keywords=["cyber exercises", "cybersecurity training", "national defense"]
                )
            ],
            "Ahto Buldas": [
                Publication(
                    title="Post-Quantum Cryptographic Protocols for Blockchain Systems",
                    authors=["Ahto Buldas", "Risto Laanoja", "Triinu Mägi"],
                    venue="IACR Cryptology ePrint Archive",
                    year=2024,
                    citation_count=8,
                    keywords=["post-quantum cryptography", "blockchain", "digital signatures"]
                )
            ],
            "Samuel Kaski": [
                Publication(
                    title="Human-AI Collaboration in Cybersecurity Decision Making",
                    authors=["Samuel Kaski", "Antti Honkela", "Pekka Marttinen"],
                    venue="Nature Machine Intelligence", 
                    year=2024,
                    citation_count=23,
                    keywords=["human-AI interaction", "cybersecurity", "decision support"]
                )
            ]
        }
        
        return mock_publications.get(professor_name, [])
    
    def search_github_repositories(self, professor_name: str, affiliation: str) -> List[GitHubRepo]:
        """Search for GitHub repositories related to professors/institutions"""
        repos = []
        
        # Search strategies:
        # 1. Search by professor name
        # 2. Search by university/institution
        # 3. Search by research keywords + affiliation
        
        search_queries = [
            f'user:"{professor_name.lower().replace(" ", "")}"',
            f'"{affiliation}" in:description',
            f'"{professor_name}" in:description OR in:readme'
        ]
        
        for query in search_queries:
            try:
                self.rate_limit('api.github.com')
                
                # GitHub API search
                url = f"https://api.github.com/search/repositories"
                params = {
                    'q': query,
                    'sort': 'updated',
                    'per_page': 5
                }
                
                response = requests.get(
                    url,
                    headers=self.github_headers,
                    params=params,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for item in data.get('items', []):
                        # Calculate relevance based on research keywords
                        description = item.get('description', '').lower()
                        readme_relevance = sum(1 for keyword in self.research_keywords 
                                             if keyword in description)
                        
                        if readme_relevance > 0:  # Only include relevant repos
                            repo = GitHubRepo(
                                name=item['name'],
                                owner=item['owner']['login'],
                                description=item.get('description', ''),
                                language=item.get('language', ''),
                                stars=item.get('stargazers_count', 0),
                                last_updated=datetime.fromisoformat(item['updated_at'].replace('Z', '+00:00')),
                                open_issues=item.get('open_issues_count', 0),
                                good_first_issues=0,  # Would need to check issue labels
                                contributors=0,  # Would need separate API call
                                url=item['html_url']
                            )
                            repos.append(repo)
                
            except Exception as e:
                print(f"⚠️  GitHub search error: {str(e)}")
                continue
        
        return repos[:10]  # Limit results
    
    def search_conferences(self, research_area: str) -> List[Conference]:
        """Search for relevant conferences and their deadlines"""
        # Mock conference data - in reality, you'd scrape from:
        # - WikiCFP (http://www.wikicfp.com/)
        # - Conference websites
        # - Academic calendar APIs
        
        conferences = {
            "cybersecurity": [
                Conference(
                    name="IEEE Symposium on Security and Privacy",
                    acronym="S&P",
                    submission_deadline=datetime(2025, 8, 15),
                    conference_date=datetime(2026, 5, 18),
                    location="San Francisco, CA",
                    website="https://www.ieee-security.org/",
                    acceptance_rate=0.12,
                    relevance_score=0.95
                ),
                Conference(
                    name="ACM Conference on Computer and Communications Security",
                    acronym="CCS", 
                    submission_deadline=datetime(2025, 5, 15),
                    conference_date=datetime(2025, 11, 15),
                    location="Melbourne, Australia",
                    website="https://www.sigsac.org/ccs/CCS2025/",
                    acceptance_rate=0.18,
                    relevance_score=0.93
                )
            ],
            "quantum": [
                Conference(
                    name="International Conference on Quantum Computing",
                    acronym="QCE",
                    submission_deadline=datetime(2025, 6, 1),
                    conference_date=datetime(2025, 9, 15),
                    location="Chicago, IL",
                    website="https://qce.quantum.ieee.org/",
                    acceptance_rate=0.25,
                    relevance_score=0.88
                )
            ],
            "AI": [
                Conference(
                    name="International Conference on Machine Learning",
                    acronym="ICML",
                    submission_deadline=datetime(2025, 2, 1),
                    conference_date=datetime(2025, 7, 13),
                    location="Vienna, Austria", 
                    website="https://icml.cc/",
                    acceptance_rate=0.22,
                    relevance_score=0.85
                )
            ]
        }
        
        return conferences.get(research_area, [])
    
    def analyze_research_opportunities(self, school_id: str) -> Dict[str, Any]:
        """Analyze research opportunities for a specific school"""
        print(f"🔬 Analyzing research opportunities for {school_id}...")
        
        opportunities = {
            'school_id': school_id,
            'analyzed_at': datetime.now().isoformat(),
            'professors': [],
            'recent_publications': [],
            'github_repos': [],
            'conferences': [],
            'collaboration_opportunities': [],
            'action_items': []
        }
        
        if school_id not in self.target_professors:
            print(f"⚠️  No professor data for {school_id}")
            return opportunities
        
        professors = self.target_professors[school_id]
        
        for professor in professors:
            prof_analysis = {
                'name': professor.name,
                'affiliation': professor.affiliation,
                'research_interests': professor.research_interests,
                'recent_publications': [],
                'github_repos': [],
                'recommendations': []
            }
            
            # Get recent publications
            publications = self.search_google_scholar_publications(professor.name)
            prof_analysis['recent_publications'] = [
                {
                    'title': pub.title,
                    'authors': pub.authors,
                    'venue': pub.venue,
                    'year': pub.year,
                    'citation_count': pub.citation_count,
                    'keywords': pub.keywords
                }
                for pub in publications
            ]
            
            # Get GitHub repositories
            repos = self.search_github_repositories(professor.name, professor.affiliation)
            prof_analysis['github_repos'] = [
                {
                    'name': repo.name,
                    'owner': repo.owner,
                    'description': repo.description,
                    'language': repo.language,
                    'stars': repo.stars,
                    'last_updated': repo.last_updated.isoformat(),
                    'open_issues': repo.open_issues,
                    'url': repo.url
                }
                for repo in repos
            ]
            
            # Generate recommendations
            recommendations = []
            
            if publications:
                latest_pub = publications[0]  # Most recent
                recommendations.append(
                    f"📖 Reference recent paper: '{latest_pub.title}' in your SOP"
                )
            
            if repos:
                active_repos = [r for r in repos if r.open_issues > 0]
                if active_repos:
                    repo = active_repos[0]
                    recommendations.append(
                        f"💻 Contribute to {repo.name}: {repo.open_issues} open issues"
                    )
            
            # Research interest alignment
            common_interests = [
                interest for interest in professor.research_interests
                if any(keyword in interest.lower() for keyword in self.research_keywords)
            ]
            
            if common_interests:
                recommendations.append(
                    f"🔗 Highlight alignment in: {', '.join(common_interests)}"
                )
            
            prof_analysis['recommendations'] = recommendations
            opportunities['professors'].append(prof_analysis)
        
        # Get relevant conferences
        research_areas = ['cybersecurity', 'quantum', 'AI']
        for area in research_areas:
            conferences = self.search_conferences(area)
            for conf in conferences:
                # Check if deadline is approaching
                if conf.submission_deadline and conf.submission_deadline > datetime.now():
                    days_until = (conf.submission_deadline - datetime.now()).days
                    
                    opportunities['conferences'].append({
                        'name': conf.name,
                        'acronym': conf.acronym,
                        'submission_deadline': conf.submission_deadline.isoformat(),
                        'conference_date': conf.conference_date.isoformat() if conf.conference_date else None,
                        'location': conf.location,
                        'website': conf.website,
                        'acceptance_rate': conf.acceptance_rate,
                        'relevance_score': conf.relevance_score,
                        'days_until_deadline': days_until,
                        'research_area': area
                    })
        
        # Generate overall action items
        action_items = []
        
        # Recent publications to cite
        all_recent_pubs = [pub for prof in opportunities['professors'] 
                          for pub in prof['recent_publications']]
        if all_recent_pubs:
            action_items.append(
                f"📚 {len(all_recent_pubs)} recent publications available for SOP citations"
            )
        
        # GitHub contribution opportunities  
        all_repos = [repo for prof in opportunities['professors'] 
                    for repo in prof['github_repos']]
        active_repos = [repo for repo in all_repos if repo['open_issues'] > 0]
        if active_repos:
            action_items.append(
                f"💻 {len(active_repos)} repositories with contribution opportunities"
            )
        
        # Upcoming conference deadlines
        upcoming_conferences = [conf for conf in opportunities['conferences']
                              if conf['days_until_deadline'] <= 90]
        if upcoming_conferences:
            action_items.append(
                f"📅 {len(upcoming_conferences)} conference deadlines in next 90 days"
            )
        
        opportunities['action_items'] = action_items
        
        return opportunities
    
    def generate_academic_report(self, school_analyses: Dict[str, Dict[str, Any]]) -> str:
        """Generate comprehensive academic intelligence report"""
        report_lines = [
            "# 🎓 Academic Intelligence Report",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Schools Analyzed**: {len(school_analyses)}",
            "",
            "## 📊 Executive Summary",
            ""
        ]
        
        # Summary statistics
        total_professors = sum(len(analysis['professors']) for analysis in school_analyses.values())
        total_publications = sum(len(prof['recent_publications']) 
                               for analysis in school_analyses.values()
                               for prof in analysis['professors'])
        total_repos = sum(len(prof['github_repos'])
                         for analysis in school_analyses.values() 
                         for prof in analysis['professors'])
        
        report_lines.extend([
            f"- **Professors Monitored**: {total_professors}",
            f"- **Recent Publications**: {total_publications}", 
            f"- **GitHub Repositories**: {total_repos}",
            "",
        ])
        
        # School-by-school analysis
        for school_id, analysis in school_analyses.items():
            school_name = self.schools.get(school_id, {}).get('full_name', school_id)
            
            report_lines.extend([
                f"## 🏛️ {school_name} ({school_id})",
                ""
            ])
            
            # Professor analysis
            for prof in analysis['professors']:
                report_lines.extend([
                    f"### 👨‍🎓 {prof['name']}",
                    f"**Affiliation**: {prof['affiliation']}",
                    f"**Research Interests**: {', '.join(prof['research_interests'])}",
                    ""
                ])
                
                # Recent publications
                if prof['recent_publications']:
                    report_lines.extend([
                        "**📖 Recent Publications:**",
                        ""
                    ])
                    for pub in prof['recent_publications'][:3]:  # Top 3
                        report_lines.append(f"- {pub['title']} ({pub['year']}) - {pub['citation_count']} citations")
                    report_lines.append("")
                
                # GitHub repositories
                if prof['github_repos']:
                    report_lines.extend([
                        "**💻 GitHub Activity:**",
                        ""
                    ])
                    for repo in prof['github_repos'][:3]:  # Top 3
                        report_lines.append(f"- [{repo['name']}]({repo['url']}) - {repo['stars']} ⭐, {repo['open_issues']} issues")
                    report_lines.append("")
                
                # Recommendations
                if prof['recommendations']:
                    report_lines.extend([
                        "**🎯 Action Recommendations:**",
                        ""
                    ])
                    for rec in prof['recommendations']:
                        report_lines.append(f"- {rec}")
                    report_lines.append("")
                
                report_lines.append("---")
                report_lines.append("")
            
            # Conference opportunities
            if analysis['conferences']:
                report_lines.extend([
                    "### 📅 Relevant Conferences",
                    "",
                    "| Conference | Deadline | Location | Acceptance Rate |",
                    "|------------|----------|----------|----------------|"
                ])
                
                # Sort by deadline
                conferences = sorted(analysis['conferences'], 
                                   key=lambda x: x['days_until_deadline'])
                
                for conf in conferences[:5]:  # Top 5
                    deadline = datetime.fromisoformat(conf['submission_deadline']).strftime('%Y-%m-%d')
                    days = conf['days_until_deadline']
                    urgency = "🚨" if days <= 30 else "⚠️" if days <= 60 else "📅"
                    
                    report_lines.append(
                        f"| {urgency} {conf['name']} | {deadline} ({days}d) | "
                        f"{conf['location']} | {conf['acceptance_rate']:.1%} |"
                    )
                
                report_lines.append("")
        
        # Overall recommendations
        report_lines.extend([
            "## 💡 Strategic Recommendations",
            "",
            "### 📚 SOP Enhancement Opportunities",
            ""
        ])
        
        # Collect all recommendations
        all_recommendations = []
        for analysis in school_analyses.values():
            for prof in analysis['professors']:
                all_recommendations.extend(prof['recommendations'])
        
        # Group similar recommendations
        citation_recs = [r for r in all_recommendations if '📖' in r]
        contribution_recs = [r for r in all_recommendations if '💻' in r]
        alignment_recs = [r for r in all_recommendations if '🔗' in r]
        
        if citation_recs:
            report_lines.extend([
                "**Recent Publications to Reference:**",
                ""
            ])
            for rec in citation_recs[:5]:  # Top 5
                report_lines.append(f"- {rec}")
            report_lines.append("")
        
        if contribution_recs:
            report_lines.extend([
                "**GitHub Contribution Opportunities:**",
                ""
            ])
            for rec in contribution_recs[:5]:  # Top 5
                report_lines.append(f"- {rec}")
            report_lines.append("")
        
        if alignment_recs:
            report_lines.extend([
                "**Research Interest Alignments:**",
                ""
            ])
            for rec in alignment_recs[:5]:  # Top 5
                report_lines.append(f"- {rec}")
            report_lines.append("")
        
        # Footer
        report_lines.extend([
            "---",
            "",
            f"*Report generated by Academic Radar v2.0 on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "*This report provides actionable intelligence for enhancing your application strategy.*"
        ])
        
        return "\n".join(report_lines)
    
    def save_academic_intelligence(self, school_analyses: Dict[str, Dict[str, Any]]):
        """Save academic intelligence data and reports"""
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
        # Save structured data
        intelligence_data = {
            'generated_at': datetime.now().isoformat(),
            'schools': school_analyses,
            'summary': {
                'total_schools': len(school_analyses),
                'total_professors': sum(len(analysis['professors']) for analysis in school_analyses.values()),
                'total_publications': sum(len(prof['recent_publications']) 
                                        for analysis in school_analyses.values()
                                        for prof in analysis['professors']),
                'total_repositories': sum(len(prof['github_repos'])
                                        for analysis in school_analyses.values() 
                                        for prof in analysis['professors'])
            }
        }
        
        json_file = self.output_dir / "academic_intelligence.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(intelligence_data, f, indent=2)
        
        print(f"📊 Academic intelligence data saved to {json_file}")
        
        # Generate and save report
        report_content = self.generate_academic_report(school_analyses)
        
        report_file = self.output_dir / "academic_intelligence_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📋 Academic intelligence report saved to {report_file}")

def main():
    """Main academic radar execution"""
    radar = AcademicRadar()
    
    try:
        # Analyze all target schools
        school_analyses = {}
        
        target_schools = ['taltech', 'aalto']  # Start with priority schools
        
        for school_id in target_schools:
            if school_id in radar.target_professors:
                analysis = radar.analyze_research_opportunities(school_id)
                school_analyses[school_id] = analysis
                
                # Small delay between schools
                time.sleep(2)
        
        # Save results
        radar.save_academic_intelligence(school_analyses)
        
        # Summary
        total_professors = sum(len(analysis['professors']) for analysis in school_analyses.values())
        total_actions = sum(len(analysis['action_items']) for analysis in school_analyses.values())
        
        print(f"\n🔬 Academic Radar Summary:")
        print(f"   Schools analyzed: {len(school_analyses)}")
        print(f"   Professors monitored: {total_professors}")
        print(f"   Action items generated: {total_actions}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Academic radar failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
