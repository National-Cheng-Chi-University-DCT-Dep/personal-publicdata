#!/usr/bin/env python3
"""
Gamified Motivation Engine for University Application System

Features:
- Achievement and badge system
- Progress bar visualization
- Streak bonus tracking
- Motivational milestones
- Psychological reinforcement mechanics
"""

import os
import sys
import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
import subprocess

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    icon: str
    category: str
    unlock_condition: str
    points: int
    unlocked: bool = False
    unlock_date: Optional[datetime] = None

@dataclass
class UserProgress:
    total_points: int = 0
    level: int = 1
    current_streak: int = 0
    longest_streak: int = 0
    achievements_unlocked: List[str] = None
    last_activity_date: Optional[datetime] = None
    
    def __post_init__(self):
        if self.achievements_unlocked is None:
            self.achievements_unlocked = []

class GamificationEngine:
    """Gamification system for university application process"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.source_data_dir = self.base_dir / "source_data"
        self.output_dir = self.base_dir / "final_applications"
        self.gamification_dir = self.base_dir / "analysis" / "gamification_data"
        
        # Create gamification data directory
        self.gamification_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration and progress
        self.load_schools_config()
        self.setup_achievements()
        self.load_user_progress()
    
    def load_schools_config(self):
        """Load school configuration"""
        with open(self.source_data_dir / "schools.yml", 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            self.schools = {school['school_id']: school for school in data['schools']}
    
    def setup_achievements(self) -> List[Achievement]:
        """Define all possible achievements in the system"""
        achievements = [
            # Document Creation Achievements
            Achievement(
                id="first_cv",
                name="CV Architect",
                description="完成第一版CV文件",
                icon="📝",
                category="Documents",
                unlock_condition="cv_generated",
                points=50
            ),
            Achievement(
                id="first_sop",
                name="SOP Draft v1.0",
                description="完成第一版SOP草稿",
                icon="📖",
                category="Documents",
                unlock_condition="sop_generated",
                points=100
            ),
            Achievement(
                id="polyglot",
                name="The Polyglot",
                description="IELTS總分達到7.0",
                icon="🌟",
                category="Language",
                unlock_condition="ielts_overall_7",
                points=150
            ),
            Achievement(
                id="writing_master",
                name="Writing Master",
                description="IELTS寫作達到6.5分",
                icon="✍️",
                category="Language",
                unlock_condition="ielts_writing_6_5",
                points=200
            ),
            
            # Application Milestones
            Achievement(
                id="first_blood",
                name="First Blood",
                description="提交第一份學校申請",
                icon="🚀",
                category="Applications",
                unlock_condition="first_application_submitted",
                points=300
            ),
            Achievement(
                id="application_spree",
                name="Application Spree",
                description="成功提交3份申請",
                icon="📬",
                category="Applications",
                unlock_condition="three_applications_submitted",
                points=500
            ),
            Achievement(
                id="deadline_warrior",
                name="Deadline Warrior",
                description="所有申請均在截止日期前完成",
                icon="⏰",
                category="Applications",
                unlock_condition="all_before_deadline",
                points=400
            ),
            
            # Research & Networking
            Achievement(
                id="networker",
                name="Networker",
                description="成功聯繫第一位教授或校友",
                icon="🤝",
                category="Networking",
                unlock_condition="first_contact_made",
                points=250
            ),
            Achievement(
                id="researcher",
                name="Academic Researcher",
                description="發現並引用10篇相關學術論文",
                icon="🔬",
                category="Research",
                unlock_condition="ten_papers_cited",
                points=350
            ),
            Achievement(
                id="github_contributor",
                name="Open Source Contributor",
                description="對目標教授的GitHub專案做出貢獻",
                icon="💻",
                category="Technical",
                unlock_condition="github_contribution",
                points=400
            ),
            
            # System Mastery
            Achievement(
                id="intelligence_master",
                name="Intelligence Master",
                description="成功運行完整的Intelligence Pipeline",
                icon="🤖",
                category="System",
                unlock_condition="full_pipeline_success",
                points=200
            ),
            Achievement(
                id="automation_guru",
                name="Automation Guru",
                description="連續7天自動化執行pipeline",
                icon="⚙️",
                category="System",
                unlock_condition="seven_day_automation",
                points=300
            ),
            
            # Streak Achievements
            Achievement(
                id="consistent_worker",
                name="Consistent Worker",
                description="連續3天推進申請進度",
                icon="🔥",
                category="Consistency",
                unlock_condition="three_day_streak",
                points=100
            ),
            Achievement(
                id="dedication",
                name="Dedication",
                description="連續7天推進申請進度",
                icon="💪",
                category="Consistency",
                unlock_condition="seven_day_streak",
                points=300
            ),
            Achievement(
                id="unstoppable",
                name="Unstoppable Force",
                description="連續14天推進申請進度",
                icon="🌟",
                category="Consistency",
                unlock_condition="fourteen_day_streak",
                points=500
            ),
            
            # Success Achievements
            Achievement(
                id="first_acceptance",
                name="Acceptance Letter",
                description="收到第一封錄取通知書",
                icon="🎉",
                category="Success",
                unlock_condition="first_acceptance_received",
                points=1000
            ),
            Achievement(
                id="scholarship_winner",
                name="Scholarship Winner",
                description="獲得獎學金或助學金",
                icon="💰",
                category="Success",
                unlock_condition="scholarship_received",
                points=1500
            ),
            Achievement(
                id="dream_school",
                name="Dream School Achiever",
                description="被第一志願學校錄取",
                icon="🏆",
                category="Success",
                unlock_condition="top_choice_acceptance",
                points=2000
            )
        ]
        
        self.achievements = {ach.id: ach for ach in achievements}
        return achievements
    
    def load_user_progress(self):
        """Load user progress from file"""
        progress_file = self.gamification_dir / "user_progress.json"
        
        if progress_file.exists():
            with open(progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Convert ISO datetime strings back to datetime objects
                if data.get('last_activity_date'):
                    data['last_activity_date'] = datetime.fromisoformat(data['last_activity_date'])
                
                self.user_progress = UserProgress(**data)
        else:
            self.user_progress = UserProgress()
        
        # Update achievement unlock status
        for ach_id in self.user_progress.achievements_unlocked:
            if ach_id in self.achievements:
                self.achievements[ach_id].unlocked = True
    
    def save_user_progress(self):
        """Save user progress to file"""
        progress_file = self.gamification_dir / "user_progress.json"
        
        # Convert datetime to ISO string for JSON serialization
        data = {
            'total_points': self.user_progress.total_points,
            'level': self.user_progress.level,
            'current_streak': self.user_progress.current_streak,
            'longest_streak': self.user_progress.longest_streak,
            'achievements_unlocked': self.user_progress.achievements_unlocked,
            'last_activity_date': self.user_progress.last_activity_date.isoformat() if self.user_progress.last_activity_date else None
        }
        
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def calculate_level(self, points: int) -> int:
        """Calculate user level based on points (exponential scaling)"""
        if points < 100:
            return 1
        elif points < 300:
            return 2
        elif points < 600:
            return 3
        elif points < 1000:
            return 4
        elif points < 1500:
            return 5
        elif points < 2500:
            return 6
        elif points < 4000:
            return 7
        elif points < 6000:
            return 8
        elif points < 10000:
            return 9
        else:
            return 10  # Max level
    
    def check_git_activity(self) -> bool:
        """Check if there has been git activity today"""
        try:
            # Get today's commits
            today = datetime.now().strftime("%Y-%m-%d")
            result = subprocess.run(
                ["git", "log", "--since", today, "--oneline"], 
                capture_output=True, 
                text=True,
                cwd=self.base_dir
            )
            
            return len(result.stdout.strip()) > 0
        except:
            return False
    
    def update_streak(self):
        """Update streak based on daily activity"""
        today = datetime.now().date()
        
        if self.user_progress.last_activity_date:
            last_date = self.user_progress.last_activity_date.date()
            days_diff = (today - last_date).days
            
            if days_diff == 1:  # Consecutive day
                self.user_progress.current_streak += 1
                if self.user_progress.current_streak > self.user_progress.longest_streak:
                    self.user_progress.longest_streak = self.user_progress.current_streak
            elif days_diff > 1:  # Streak broken
                self.user_progress.current_streak = 1
        else:
            # First activity
            self.user_progress.current_streak = 1
        
        self.user_progress.last_activity_date = datetime.now()
    
    def check_achievements(self) -> List[Achievement]:
        """Check and unlock new achievements"""
        newly_unlocked = []
        
        # Check document generation achievements
        if self.output_dir.exists():
            cv_files = list(self.output_dir.rglob("CV_*.md"))
            sop_files = list(self.output_dir.rglob("SOP_*.md"))
            
            if cv_files and not self.achievements["first_cv"].unlocked:
                newly_unlocked.append(self.unlock_achievement("first_cv"))
            
            if sop_files and not self.achievements["first_sop"].unlocked:
                newly_unlocked.append(self.unlock_achievement("first_sop"))
        
        # Check IELTS achievements (based on profile - hardcoded for now)
        # In real implementation, this would read from user profile
        ielts_overall = 7.0  # Current score
        ielts_writing = 5.5   # Current score
        
        if ielts_overall >= 7.0 and not self.achievements["polyglot"].unlocked:
            newly_unlocked.append(self.unlock_achievement("polyglot"))
        
        if ielts_writing >= 6.5 and not self.achievements["writing_master"].unlocked:
            newly_unlocked.append(self.unlock_achievement("writing_master"))
        
        # Check application status achievements
        submitted_count = 0
        all_before_deadline = True
        
        for school_id, school in self.schools.items():
            if school.get('application_status') == 'SUBMITTED':
                submitted_count += 1
            elif school.get('application_status') in ['NOT_STARTED', 'DRAFTING']:
                # Check if deadline is passed
                deadline_str = school.get('application_deadline', '')
                if deadline_str:  # Simplified deadline check
                    all_before_deadline = False
        
        if submitted_count >= 1 and not self.achievements["first_blood"].unlocked:
            newly_unlocked.append(self.unlock_achievement("first_blood"))
        
        if submitted_count >= 3 and not self.achievements["application_spree"].unlocked:
            newly_unlocked.append(self.unlock_achievement("application_spree"))
        
        # Check streak achievements
        if self.user_progress.current_streak >= 3 and not self.achievements["consistent_worker"].unlocked:
            newly_unlocked.append(self.unlock_achievement("consistent_worker"))
        
        if self.user_progress.current_streak >= 7 and not self.achievements["dedication"].unlocked:
            newly_unlocked.append(self.unlock_achievement("dedication"))
        
        if self.user_progress.current_streak >= 14 and not self.achievements["unstoppable"].unlocked:
            newly_unlocked.append(self.unlock_achievement("unstoppable"))
        
        # Check system achievements
        if self.output_dir.exists():
            execution_reports = list(self.output_dir.glob("execution_report.md"))
            if execution_reports and not self.achievements["intelligence_master"].unlocked:
                newly_unlocked.append(self.unlock_achievement("intelligence_master"))
        
        # Filter out None values
        newly_unlocked = [ach for ach in newly_unlocked if ach is not None]
        
        return newly_unlocked
    
    def unlock_achievement(self, achievement_id: str) -> Optional[Achievement]:
        """Unlock an achievement and award points"""
        if achievement_id in self.achievements and not self.achievements[achievement_id].unlocked:
            achievement = self.achievements[achievement_id]
            achievement.unlocked = True
            achievement.unlock_date = datetime.now()
            
            # Add to user progress
            self.user_progress.achievements_unlocked.append(achievement_id)
            self.user_progress.total_points += achievement.points
            
            # Update level
            old_level = self.user_progress.level
            self.user_progress.level = self.calculate_level(self.user_progress.total_points)
            
            print(f"🎉 Achievement Unlocked: {achievement.icon} {achievement.name}")
            print(f"    {achievement.description}")
            print(f"    +{achievement.points} points!")
            
            if self.user_progress.level > old_level:
                print(f"🆙 Level Up! You are now level {self.user_progress.level}!")
            
            return achievement
        
        return None
    
    def calculate_progress_percentage(self) -> float:
        """Calculate overall application progress percentage"""
        if not self.schools:
            return 0.0
        
        total_schools = len([s for s in self.schools.values() if s.get('status') == 'active'])
        if total_schools == 0:
            return 0.0
        
        # Weight different statuses
        status_weights = {
            'NOT_STARTED': 0.0,
            'DRAFTING': 0.3,
            'SUBMITTED': 0.7,
            'DECISION_PENDING': 0.8,
            'ACCEPTED': 1.0,
            'REJECTED': 1.0  # Complete, even if negative
        }
        
        total_progress = 0.0
        for school in self.schools.values():
            if school.get('status') == 'active':
                app_status = school.get('application_status', 'NOT_STARTED')
                total_progress += status_weights.get(app_status, 0.0)
        
        return (total_progress / total_schools) * 100
    
    def generate_motivational_message(self) -> str:
        """Generate personalized motivational message"""
        progress_pct = self.calculate_progress_percentage()
        level = self.user_progress.level
        streak = self.user_progress.current_streak
        
        messages = []
        
        # Progress-based messages
        if progress_pct < 20:
            messages.append("🌱 每一個偉大的旅程都始於第一步。您已經開始了！")
        elif progress_pct < 50:
            messages.append("🚀 進展順利！保持這個勢頭，成功就在前方。")
        elif progress_pct < 80:
            messages.append("⭐ 您已經走過了大部分路程。勝利在望！")
        else:
            messages.append("🏆 即將抵達終點線！您的努力即將得到回報。")
        
        # Level-based messages
        if level >= 5:
            messages.append(f"👑 Level {level} - 您已經是申請專家了！")
        elif level >= 3:
            messages.append(f"💪 Level {level} - 經驗豐富的申請者！")
        
        # Streak-based messages
        if streak >= 7:
            messages.append(f"🔥 連續{streak}天的專注！您的毅力令人敬佩。")
        elif streak >= 3:
            messages.append(f"✨ {streak}天連擊！保持這個節奏。")
        
        return " ".join(messages) if messages else "💡 繼續努力，您正在朝著目標穩步前進！"
    
    def generate_gamification_dashboard(self) -> str:
        """Generate gamified dashboard content"""
        progress_pct = self.calculate_progress_percentage()
        
        dashboard_lines = [
            "# 🎮 申請進度遊戲化儀表板",
            "",
            f"**玩家**: Pei-Chen Lee | **等級**: {self.user_progress.level} | **總分**: {self.user_progress.total_points:,}",
            f"**當前連擊**: {self.user_progress.current_streak}天 🔥 | **最長連擊**: {self.user_progress.longest_streak}天 ⚡",
            "",
            "## 📊 總體進度",
            ""
        ]
        
        # Progress bar
        progress_blocks = int(progress_pct / 5)  # 20 blocks for 100%
        progress_bar = "█" * progress_blocks + "░" * (20 - progress_blocks)
        dashboard_lines.extend([
            f"**申請完成度**: {progress_pct:.1f}%",
            f"```",
            f"{progress_bar} {progress_pct:.1f}%",
            f"```",
            ""
        ])
        
        # Level progress
        level_points = [0, 100, 300, 600, 1000, 1500, 2500, 4000, 6000, 10000, 999999]
        current_level_start = level_points[self.user_progress.level - 1] if self.user_progress.level <= 10 else 10000
        next_level_start = level_points[self.user_progress.level] if self.user_progress.level < 10 else 999999
        
        if self.user_progress.level < 10:
            level_progress = (self.user_progress.total_points - current_level_start) / (next_level_start - current_level_start)
            level_progress_blocks = int(level_progress * 20)
            level_progress_bar = "█" * level_progress_blocks + "░" * (20 - level_progress_blocks)
            
            dashboard_lines.extend([
                f"**等級進度**: Level {self.user_progress.level} → {self.user_progress.level + 1}",
                f"```",
                f"{level_progress_bar} {self.user_progress.total_points - current_level_start}/{next_level_start - current_level_start}",
                f"```",
                ""
            ])
        else:
            dashboard_lines.extend([
                f"**等級進度**: ⭐ **滿級達成！** ⭐",
                ""
            ])
        
        # Achievements section
        dashboard_lines.extend([
            "## 🏆 成就系統",
            ""
        ])
        
        # Group achievements by category
        categories = {}
        for achievement in self.achievements.values():
            if achievement.category not in categories:
                categories[achievement.category] = []
            categories[achievement.category].append(achievement)
        
        for category, achievements in categories.items():
            unlocked_in_category = sum(1 for ach in achievements if ach.unlocked)
            total_in_category = len(achievements)
            
            dashboard_lines.extend([
                f"### {category} ({unlocked_in_category}/{total_in_category})",
                ""
            ])
            
            for achievement in achievements:
                if achievement.unlocked:
                    unlock_date = achievement.unlock_date.strftime("%Y-%m-%d") if achievement.unlock_date else "Unknown"
                    dashboard_lines.append(
                        f"✅ {achievement.icon} **{achievement.name}** - {achievement.description} "
                        f"*({achievement.points} pts, {unlock_date})*"
                    )
                else:
                    dashboard_lines.append(
                        f"🔒 {achievement.icon} **{achievement.name}** - {achievement.description} "
                        f"*({achievement.points} pts)*"
                    )
            
            dashboard_lines.append("")
        
        # Current streak section
        if self.user_progress.current_streak > 0:
            dashboard_lines.extend([
                "## 🔥 連擊系統",
                "",
                f"**當前連擊**: {self.user_progress.current_streak} 天",
                f"**歷史最高**: {self.user_progress.longest_streak} 天",
                ""
            ])
            
            # Streak visual
            streak_visual = "🔥" * min(self.user_progress.current_streak, 10)
            if self.user_progress.current_streak > 10:
                streak_visual += f" (+{self.user_progress.current_streak - 10})"
            
            dashboard_lines.extend([
                f"```",
                f"{streak_visual}",
                f"```",
                ""
            ])
        
        # Motivational message
        motivational_msg = self.generate_motivational_message()
        dashboard_lines.extend([
            "## 💬 今日激勵",
            "",
            f"*{motivational_msg}*",
            ""
        ])
        
        # Next milestones
        dashboard_lines.extend([
            "## 🎯 下個目標",
            ""
        ])
        
        # Find next unachieved achievements
        next_achievements = [ach for ach in self.achievements.values() if not ach.unlocked]
        next_achievements.sort(key=lambda x: x.points)  # Sort by points (difficulty)
        
        for achievement in next_achievements[:3]:  # Show next 3 achievements
            dashboard_lines.append(f"🎯 {achievement.icon} **{achievement.name}** - {achievement.description} ({achievement.points} pts)")
        
        dashboard_lines.extend([
            "",
            "---",
            "",
            f"*遊戲化系統更新於: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            f"*繼續努力，向著夢想學校前進！* 🚀"
        ])
        
        return "\n".join(dashboard_lines)
    
    def run_gamification_update(self) -> Dict[str, Any]:
        """Run complete gamification system update"""
        print("🎮 Running gamification system update...")
        
        # Update activity streak
        if self.check_git_activity():
            self.update_streak()
            print(f"📈 Activity detected! Current streak: {self.user_progress.current_streak} days")
        
        # Check for new achievements
        new_achievements = self.check_achievements()
        
        # Save progress
        self.save_user_progress()
        
        # Generate dashboard
        dashboard_content = self.generate_gamification_dashboard()
        
        # Save dashboard
        dashboard_file = self.output_dir / "gamification_dashboard.md"
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(dashboard_content)
        
        print(f"🎮 Gamification dashboard saved to {dashboard_file}")
        
        # Return summary
        summary = {
            'current_level': self.user_progress.level,
            'total_points': self.user_progress.total_points,
            'current_streak': self.user_progress.current_streak,
            'new_achievements': len(new_achievements),
            'progress_percentage': self.calculate_progress_percentage(),
            'achievements_unlocked': len(self.user_progress.achievements_unlocked),
            'total_achievements': len(self.achievements)
        }
        
        return summary

def main():
    """Main gamification execution"""
    engine = GamificationEngine()
    
    try:
        # Run gamification update
        summary = engine.run_gamification_update()
        
        # Print summary
        print(f"\n🎮 Gamification Summary:")
        print(f"   Level: {summary['current_level']}")
        print(f"   Points: {summary['total_points']:,}")
        print(f"   Streak: {summary['current_streak']} days")
        print(f"   Progress: {summary['progress_percentage']:.1f}%")
        print(f"   Achievements: {summary['achievements_unlocked']}/{summary['total_achievements']}")
        
        if summary['new_achievements'] > 0:
            print(f"   🎉 New achievements unlocked: {summary['new_achievements']}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Gamification update failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
