"""
自動化資料庫更新與 PR 生成
Automated Database Update & Pull Request Generation

功能：
- 比對新發現的課程與現有 schools.yml
- 自動建立新分支
- 將新課程附加到 schools.yml
- 自動生成 Pull Request
- 產生 discovery_report.md
"""

import yaml
import json
import sys
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class DatabaseUpdater:
    """資料庫更新器"""
    
    def __init__(self):
        """初始化更新器"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.schools_file = 'source_data/schools.yml'
        self.discovery_dir = Path('discovery')
        self.report_file = self.discovery_dir / 'discovery_report.md'
    
    def load_existing_schools(self) -> List[Dict[str, Any]]:
        """載入現有的學校資料"""
        try:
            with open(self.schools_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                schools = data.get('schools', [])
                self.logger.info(f"載入了 {len(schools)} 所現有學校")
                return schools
        except Exception as e:
            self.logger.error(f"載入現有學校資料失敗: {e}")
            return []
    
    def load_qualified_schools(self) -> List[Dict[str, Any]]:
        """載入篩選後的合格課程"""
        try:
            # 找到最新的 qualified_schools 檔案
            yml_files = sorted(self.discovery_dir.glob('qualified_schools_*.yml'), reverse=True)
            
            if not yml_files:
                self.logger.warning("沒有找到 qualified_schools 檔案")
                return []
            
            latest_file = yml_files[0]
            self.logger.info(f"載入篩選結果: {latest_file}")
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                schools = data.get('schools', [])
                self.logger.info(f"載入了 {len(schools)} 個合格課程")
                return schools
        
        except Exception as e:
            self.logger.error(f"載入合格課程失敗: {e}")
            return []
    
    def find_new_schools(self, existing: List[Dict[str, Any]], qualified: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """找出新發現的課程"""
        # 建立現有學校的索引（使用 name + program_name）
        existing_index = set()
        for school in existing:
            key = f"{school.get('name', '')}_{school.get('program_name', '')}"
            existing_index.add(key.lower())
        
        # 找出新課程
        new_schools = []
        for school in qualified:
            key = f"{school.get('name', '')}_{school.get('program_name', '')}"
            if key.lower() not in existing_index:
                new_schools.append(school)
        
        self.logger.info(f"找到 {len(new_schools)} 個新課程")
        return new_schools
    
    def create_git_branch(self) -> tuple[bool, str]:
        """
        建立新的 Git 分支
        
        Returns:
            (是否成功, 分支名稱)
        """
        try:
            branch_name = f"course-discovery-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            # 建立並切換到新分支
            result = subprocess.run(
                ['git', 'checkout', '-b', branch_name],
                capture_output=True,
                text=True,
                check=True
            )
            
            self.logger.info(f"✅ 已建立分支: {branch_name}")
            return True, branch_name
        
        except subprocess.CalledProcessError as e:
            self.logger.error(f"建立分支失敗: {e.stderr}")
            return False, ""
    
    def update_schools_yml(self, new_schools: List[Dict[str, Any]]) -> bool:
        """更新 schools.yml"""
        try:
            # 載入現有資料
            with open(self.schools_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # 附加新學校
            existing_schools = data.get('schools', [])
            existing_schools.extend(new_schools)
            data['schools'] = existing_schools
            
            # 儲存
            with open(self.schools_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            
            self.logger.info(f"✅ 已更新 {self.schools_file}，新增 {len(new_schools)} 所學校")
            return True
        
        except Exception as e:
            self.logger.error(f"更新 schools.yml 失敗: {e}")
            return False
    
    def git_commit_and_push(self, branch_name: str, new_schools: List[Dict[str, Any]]) -> bool:
        """Commit 並 Push 變更"""
        try:
            # Add 檔案
            subprocess.run(
                ['git', 'add', self.schools_file],
                check=True
            )
            
            subprocess.run(
                ['git', 'add', str(self.report_file)],
                check=True
            )
            
            # Commit
            commit_message = f"🔍 Add {len(new_schools)} newly discovered courses [automated]"
            subprocess.run(
                ['git', 'commit', '-m', commit_message],
                check=True
            )
            
            # Push
            subprocess.run(
                ['git', 'push', 'origin', branch_name],
                check=True
            )
            
            self.logger.info("✅ 變更已 commit 並 push")
            return True
        
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git 操作失敗: {e}")
            return False
    
    def create_pull_request(self, branch_name: str, new_schools: List[Dict[str, Any]]) -> bool:
        """
        使用 GitHub CLI 建立 Pull Request
        
        Args:
            branch_name: 分支名稱
            new_schools: 新學校清單
            
        Returns:
            是否成功
        """
        try:
            # 建立 PR 描述
            pr_body = self.generate_pr_description(new_schools)
            
            # 使用 gh CLI 建立 PR
            result = subprocess.run(
                [
                    'gh', 'pr', 'create',
                    '--title', f'🔍 Discovered {len(new_schools)} new courses',
                    '--body', pr_body,
                    '--base', 'main',
                    '--head', branch_name
                ],
                capture_output=True,
                text=True,
                check=True
            )
            
            self.logger.info(f"✅ Pull Request 已建立")
            self.logger.info(f"PR URL: {result.stdout.strip()}")
            return True
        
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"建立 PR 失敗: {e.stderr}")
            self.logger.info("提示：如果沒有安裝 GitHub CLI，請手動在 GitHub 上建立 PR")
            return False
        except FileNotFoundError:
            self.logger.warning("GitHub CLI 未安裝，請手動建立 PR")
            self.logger.info("安裝方式: https://cli.github.com/")
            return False
    
    def generate_pr_description(self, new_schools: List[Dict[str, Any]]) -> str:
        """生成 PR 描述"""
        description = f"## 🔍 新發現的課程\n\n"
        description += f"**發現時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        description += f"**新課程數**: {len(new_schools)}\n\n"
        description += "### 課程清單\n\n"
        
        for idx, school in enumerate(new_schools[:20], 1):  # 最多列出 20 個
            description += f"{idx}. **{school.get('name')}** - {school.get('program_name')}\n"
            description += f"   - 國家: {school.get('country')}\n"
            description += f"   - 匹配分數: {school.get('match_score', 0):.1f}\n"
            if school.get('application_url'):
                description += f"   - [課程網址]({school.get('application_url')})\n"
            description += "\n"
        
        if len(new_schools) > 20:
            description += f"\n... 以及其他 {len(new_schools) - 20} 個課程\n"
        
        description += "\n### 📊 統計\n\n"
        
        # 按國家統計
        country_count = {}
        for school in new_schools:
            country = school.get('country', 'Unknown')
            country_count[country] = country_count.get(country, 0) + 1
        
        description += "按國家分布：\n"
        for country, count in sorted(country_count.items(), key=lambda x: x[1], reverse=True):
            description += f"- {country}: {count} 個課程\n"
        
        description += "\n### ✅ 請審查\n\n"
        description += "請檢查以下項目後再 merge：\n"
        description += "- [ ] 課程是否符合申請目標\n"
        description += "- [ ] 學校資訊是否正確\n"
        description += "- [ ] 優先級設定是否需要調整\n"
        
        return description
    
    def generate_discovery_report(self, new_schools: List[Dict[str, Any]], branch_name: str) -> None:
        """生成探索報告"""
        report = f"# 課程探索報告\n\n"
        report += f"**執行時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"**分支名稱**: `{branch_name}`\n\n"
        
        report += "## 📊 摘要\n\n"
        report += f"- **新發現課程數**: {len(new_schools)}\n"
        
        if new_schools:
            # 按國家統計
            country_count = {}
            for school in new_schools:
                country = school.get('country', 'Unknown')
                country_count[country] = country_count.get(country, 0) + 1
            
            report += f"- **涵蓋國家數**: {len(country_count)}\n\n"
            
            report += "### 按國家分布\n\n"
            for country, count in sorted(country_count.items(), key=lambda x: x[1], reverse=True):
                report += f"- {country}: {count} 個\n"
            
            report += "\n## 📋 新發現的課程\n\n"
            report += "| 學校 | 課程 | 國家 | 匹配分數 |\n"
            report += "|------|------|------|----------|\n"
            
            for school in sorted(new_schools, key=lambda x: x.get('match_score', 0), reverse=True):
                report += f"| {school.get('name', 'Unknown')} "
                report += f"| {school.get('program_name', 'Unknown')} "
                report += f"| {school.get('country', 'Unknown')} "
                report += f"| {school.get('match_score', 0):.1f} |\n"
            
            report += "\n## 🔗 課程連結\n\n"
            for idx, school in enumerate(new_schools, 1):
                if school.get('application_url'):
                    report += f"{idx}. [{school.get('name')} - {school.get('program_name')}]({school.get('application_url')})\n"
        else:
            report += "- **無新發現課程**\n\n"
            report += "所有搜尋到的課程都已存在於 schools.yml 中。\n"
        
        report += f"\n---\n\n"
        report += f"**下一步動作**:\n"
        if new_schools:
            report += f"1. 檢查 Pull Request: `{branch_name}`\n"
            report += f"2. 審查新發現的課程\n"
            report += f"3. Merge PR 或調整優先級\n"
        else:
            report += f"1. 無需動作\n"
            report += f"2. 系統將在下次排程時再次搜尋\n"
        
        # 儲存報告
        try:
            with open(self.report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            self.logger.info(f"探索報告已儲存: {self.report_file}")
        except Exception as e:
            self.logger.error(f"儲存報告失敗: {e}")
    
    def run(self, create_pr: bool = True) -> Dict[str, Any]:
        """
        執行資料庫更新
        
        Args:
            create_pr: 是否建立 PR
            
        Returns:
            執行結果
        """
        try:
            self.logger.info("=== 開始資料庫更新流程 ===")
            
            # 1. 載入資料
            existing_schools = self.load_existing_schools()
            qualified_schools = self.load_qualified_schools()
            
            if not qualified_schools:
                self.logger.warning("沒有合格課程資料")
                return {'success': False, 'error': 'No qualified courses'}
            
            # 2. 找出新課程
            new_schools = self.find_new_schools(existing_schools, qualified_schools)
            
            if not new_schools:
                self.logger.info("沒有新發現的課程")
                
                # 生成報告（無新課程）
                self.generate_discovery_report([], "")
                
                return {
                    'success': True,
                    'new_schools_count': 0,
                    'message': 'No new courses discovered'
                }
            
            self.logger.info(f"✅ 發現 {len(new_schools)} 個新課程")
            
            if create_pr:
                # 3. 建立 Git 分支
                success, branch_name = self.create_git_branch()
                if not success:
                    return {'success': False, 'error': 'Failed to create branch'}
                
                # 4. 更新 schools.yml
                if not self.update_schools_yml(new_schools):
                    return {'success': False, 'error': 'Failed to update schools.yml'}
                
                # 5. 生成報告
                self.generate_discovery_report(new_schools, branch_name)
                
                # 6. Commit 和 Push
                if not self.git_commit_and_push(branch_name, new_schools):
                    return {'success': False, 'error': 'Failed to commit and push'}
                
                # 7. 建立 Pull Request
                pr_created = self.create_pull_request(branch_name, new_schools)
                
                # 8. 切回 main 分支
                subprocess.run(['git', 'checkout', 'main'], check=True)
                
                return {
                    'success': True,
                    'new_schools_count': len(new_schools),
                    'branch_name': branch_name,
                    'pr_created': pr_created,
                    'new_schools': new_schools
                }
            else:
                # 只生成報告，不建立 PR
                self.generate_discovery_report(new_schools, "preview-only")
                
                return {
                    'success': True,
                    'new_schools_count': len(new_schools),
                    'preview_only': True,
                    'new_schools': new_schools
                }
        
        except Exception as e:
            self.logger.error(f"資料庫更新失敗: {e}")
            
            # 嘗試切回 main 分支
            try:
                subprocess.run(['git', 'checkout', 'main'], check=False)
            except:
                pass
            
            return {'success': False, 'error': str(e)}
    
    def find_new_schools(self, existing: List[Dict[str, Any]], qualified: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """找出新學校"""
        existing_index = set()
        for school in existing:
            key = f"{school.get('name', '')}_{school.get('program_name', '')}"
            existing_index.add(key.lower())
        
        new_schools = []
        for school in qualified:
            key = f"{school.get('name', '')}_{school.get('program_name', '')}"
            if key.lower() not in existing_index:
                new_schools.append(school)
        
        return new_schools
    
    def create_git_branch(self) -> tuple[bool, str]:
        """建立 Git 分支"""
        try:
            branch_name = f"course-discovery-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            subprocess.run(['git', 'checkout', '-b', branch_name], capture_output=True, check=True)
            self.logger.info(f"✅ 建立分支: {branch_name}")
            return True, branch_name
        except subprocess.CalledProcessError as e:
            self.logger.error(f"建立分支失敗: {e}")
            return False, ""
    
    def update_schools_yml(self, new_schools: List[Dict[str, Any]]) -> bool:
        """更新 schools.yml"""
        try:
            with open(self.schools_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            existing = data.get('schools', [])
            existing.extend(new_schools)
            data['schools'] = existing
            
            with open(self.schools_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            
            self.logger.info(f"✅ 更新 schools.yml，新增 {len(new_schools)} 所")
            return True
        except Exception as e:
            self.logger.error(f"更新失敗: {e}")
            return False
    
    def git_commit_and_push(self, branch_name: str, new_schools: List[Dict[str, Any]]) -> bool:
        """Commit 並 Push"""
        try:
            subprocess.run(['git', 'add', self.schools_file], check=True)
            subprocess.run(['git', 'add', str(self.report_file)], check=True)
            
            commit_msg = f"🔍 Add {len(new_schools)} newly discovered courses [automated]"
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            subprocess.run(['git', 'push', 'origin', branch_name], check=True)
            
            self.logger.info("✅ Commit and Push 成功")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git 操作失敗: {e}")
            return False
    
    def create_pull_request(self, branch_name: str, new_schools: List[Dict[str, Any]]) -> bool:
        """建立 Pull Request"""
        try:
            pr_body = self.generate_pr_description(new_schools)
            
            result = subprocess.run(
                ['gh', 'pr', 'create', '--title', f'🔍 Discovered {len(new_schools)} new courses',
                 '--body', pr_body, '--base', 'main', '--head', branch_name],
                capture_output=True, text=True, check=True
            )
            
            self.logger.info(f"✅ PR 已建立: {result.stdout.strip()}")
            return True
        except:
            self.logger.warning("建立 PR 失敗，請手動建立")
            return False


def main():
    """主函式"""
    import argparse
    
    parser = argparse.ArgumentParser(description='資料庫更新工具')
    parser.add_argument('--no-pr', action='store_true', help='不建立 PR，只生成預覽')
    
    args = parser.parse_args()
    
    print("""
╔══════════════════════════════════════════════════════════╗
║         自動化資料庫更新                                ║
║         Automated Database Updater                      ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    updater = DatabaseUpdater()
    result = updater.run(create_pr=not args.no_pr)
    
    if result['success']:
        print(f"\n✅ 更新完成")
        print(f"新發現課程: {result['new_schools_count']}")
        
        if result.get('pr_created'):
            print(f"Pull Request 已建立")
        elif not result.get('preview_only'):
            print(f"分支已建立: {result.get('branch_name')}")
            print(f"請手動在 GitHub 上建立 PR")
    else:
        print(f"\n❌ 更新失敗: {result.get('error')}")
        sys.exit(1)


if __name__ == '__main__':
    main()

