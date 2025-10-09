"""
智慧篩選與驗證引擎
Smart Filtering & Validation Engine

功能：
- 根據 my_profile.yml 篩選符合條件的課程
- IELTS 要求驗證
- 學術興趣匹配
- 學費驗證
- 產出符合 schools.yml 格式的資料
"""

import yaml
import json
import sys
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class CourseFilter:
    """課程篩選與驗證引擎"""
    
    def __init__(self):
        """初始化篩選引擎"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.profile_file = 'source_data/my_profile.yml'
        self.raw_data_dir = Path('discovery/raw_data')
        self.output_dir = Path('discovery')
        self.profile = None
    
    def load_profile(self) -> Dict[str, Any]:
        """載入個人申請條件"""
        try:
            with open(self.profile_file, 'r', encoding='utf-8') as f:
                profile = yaml.safe_load(f)
                self.logger.info("個人申請條件已載入")
                return profile
        except Exception as e:
            self.logger.error(f"載入個人條件失敗: {e}")
            return {}
    
    def load_raw_courses(self) -> List[Dict[str, Any]]:
        """載入所有原始課程資料"""
        all_courses = []
        
        try:
            json_files = list(self.raw_data_dir.glob('*.json'))
            self.logger.info(f"找到 {len(json_files)} 個原始資料檔案")
            
            for json_file in json_files:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    courses = data.get('courses', [])
                    all_courses.extend(courses)
            
            self.logger.info(f"總共載入 {len(all_courses)} 個課程")
            return all_courses
        
        except Exception as e:
            self.logger.error(f"載入原始資料失敗: {e}")
            return []
    
    def validate_ielts(self, course: Dict[str, Any]) -> bool:
        """
        驗證 IELTS 要求
        
        Args:
            course: 課程資料
            
        Returns:
            是否符合要求
        """
        try:
            # 取得個人 IELTS 分數
            my_ielts = self.profile.get('language_proficiency', {}).get('ielts', {})
            my_overall = my_ielts.get('overall', 0)
            my_writing = my_ielts.get('writing', 0)
            
            # 取得課程要求
            course_ielts_text = course.get('ielts_requirement', '')
            course_ielts_overall = course.get('ielts_overall')
            
            # 如果沒有 IELTS 要求資訊，假設符合
            if not course_ielts_text and not course_ielts_overall:
                return True
            
            # 如果有明確的總分要求
            if course_ielts_overall:
                if my_overall < course_ielts_overall:
                    return False
            
            # 如果只有文字描述，嘗試解析
            if course_ielts_text:
                # 提取數字
                numbers = re.findall(r'(\d+\.?\d*)', course_ielts_text)
                if numbers:
                    required_score = float(numbers[0])
                    if my_overall < required_score:
                        return False
            
            return True
        
        except Exception as e:
            self.logger.debug(f"IELTS 驗證時發生錯誤: {e}")
            return True  # 無法驗證時假設符合
    
    def validate_interest(self, course: Dict[str, Any]) -> tuple[bool, float]:
        """
        驗證學術興趣匹配
        
        Args:
            course: 課程資料
            
        Returns:
            (是否匹配, 匹配分數)
        """
        try:
            interests = self.profile.get('academic_interests', {})
            primary_interests = interests.get('primary', [])
            secondary_interests = interests.get('secondary', [])
            keywords = interests.get('keywords', [])
            
            all_interests = primary_interests + secondary_interests + keywords
            
            # 取得課程名稱（轉為小寫）
            program_name = course.get('program_name', '').lower()
            
            # 計算匹配分數
            match_score = 0.0
            matched_keywords = []
            
            for interest in all_interests:
                if interest.lower() in program_name:
                    matched_keywords.append(interest)
                    # 主要興趣權重較高
                    if interest in primary_interests:
                        match_score += 2.0
                    elif interest in secondary_interests:
                        match_score += 1.5
                    else:
                        match_score += 1.0
            
            if matched_keywords:
                self.logger.info(f"興趣匹配: {course.get('program_name')} -> {matched_keywords}")
                return True, match_score
            
            return False, 0.0
        
        except Exception as e:
            self.logger.debug(f"興趣驗證時發生錯誤: {e}")
            return False, 0.0
    
    def validate_tuition(self, course: Dict[str, Any]) -> bool:
        """驗證學費"""
        try:
            # 取得預算上限
            max_fee = self.profile.get('financial', {}).get('max_tuition_fee', {})
            max_amount = max_fee.get('amount', 999999)
            
            # 如果偏好免學費
            prefer_free = self.profile.get('financial', {}).get('prefer_tuition_free', False)
            
            # 取得課程學費資訊
            tuition_info = course.get('tuition_info', '').lower()
            
            # 如果包含 free 關鍵字
            if any(keyword in tuition_info for keyword in ['free', 'no tuition', 'tuition-free']):
                return True
            
            # 如果沒有學費資訊，假設符合
            if not tuition_info or tuition_info == 'n/a':
                return True
            
            # 嘗試提取金額（簡單處理）
            numbers = re.findall(r'(\d+[,\d]*)', tuition_info)
            if numbers:
                # 移除逗號並轉換
                amount_str = numbers[0].replace(',', '')
                try:
                    amount = float(amount_str)
                    # 簡單判斷（實際需要更複雜的幣別處理）
                    if amount > max_amount:
                        return False
                except:
                    pass
            
            return True
        
        except Exception as e:
            self.logger.debug(f"學費驗證時發生錯誤: {e}")
            return True
    
    def validate_country(self, course: Dict[str, Any]) -> bool:
        """驗證國家偏好"""
        try:
            preferred = self.profile.get('geographic_preferences', {}).get('preferred_countries', [])
            excluded = self.profile.get('geographic_preferences', {}).get('excluded_countries', [])
            
            course_country = course.get('country', '')
            
            # 檢查是否在排除清單
            if course_country in excluded:
                return False
            
            # 如果沒有偏好清單，接受所有
            if not preferred:
                return True
            
            # 檢查是否在偏好清單
            return course_country in preferred
        
        except Exception as e:
            self.logger.debug(f"國家驗證時發生錯誤: {e}")
            return True
    
    def filter_courses(self, courses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """篩選課程"""
        filtered = []
        stats = {
            'total': len(courses),
            'passed_ielts': 0,
            'passed_interest': 0,
            'passed_tuition': 0,
            'passed_country': 0,
            'passed_all': 0
        }
        
        for course in courses:
            # 驗證各項條件
            ielts_ok = self.validate_ielts(course)
            interest_ok, interest_score = self.validate_interest(course)
            tuition_ok = self.validate_tuition(course)
            country_ok = self.validate_country(course)
            
            # 統計
            if ielts_ok:
                stats['passed_ielts'] += 1
            if interest_ok:
                stats['passed_interest'] += 1
            if tuition_ok:
                stats['passed_tuition'] += 1
            if country_ok:
                stats['passed_country'] += 1
            
            # 所有條件都符合
            if ielts_ok and interest_ok and tuition_ok and country_ok:
                course['match_score'] = interest_score
                course['validation_passed'] = True
                filtered.append(course)
                stats['passed_all'] += 1
        
        self.logger.info(f"\n篩選統計:")
        self.logger.info(f"  總課程數: {stats['total']}")
        self.logger.info(f"  通過 IELTS: {stats['passed_ielts']}")
        self.logger.info(f"  通過興趣: {stats['passed_interest']}")
        self.logger.info(f"  通過學費: {stats['passed_tuition']}")
        self.logger.info(f"  通過國家: {stats['passed_country']}")
        self.logger.info(f"  全部通過: {stats['passed_all']}")
        
        # 按匹配分數排序
        filtered.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        return filtered
    
    def convert_to_schools_format(self, courses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """轉換為 schools.yml 格式"""
        schools = []
        
        for course in courses:
            school = {
                'name': course.get('university_name', 'Unknown'),
                'name_english': course.get('university_name', 'Unknown'),
                'country': course.get('country', 'Unknown'),
                'program_name': course.get('program_name', 'Unknown'),
                'application_url': course.get('program_url', ''),
                'priority': 'medium',  # 預設中等優先級
                'status': 'discovered',
                'source': course.get('source', 'Unknown'),
                'discovered_at': course.get('scraped_at'),
                'match_score': course.get('match_score', 0),
                'notes': f"自動發現 - 匹配分數: {course.get('match_score', 0)}"
            }
            
            # 如果有 IELTS 資訊
            if 'ielts_requirement' in course:
                school['ielts_requirement'] = course['ielts_requirement']
            
            # 如果有截止日期
            if 'application_deadline' in course:
                school['deadline'] = course['application_deadline']
            
            schools.append(school)
        
        return schools
    
    def save_filtered_results(self, filtered_courses: List[Dict[str, Any]]) -> Path:
        """儲存篩選結果"""
        filename = self.output_dir / f"filtered_courses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'filtered_at': datetime.now().isoformat(),
                    'total_courses': len(filtered_courses),
                    'courses': filtered_courses
                }, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"篩選結果已儲存: {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"儲存篩選結果失敗: {e}")
            return None
    
    def run(self) -> List[Dict[str, Any]]:
        """執行篩選"""
        try:
            self.logger.info("=== 開始篩選課程 ===")
            
            # 載入個人條件
            self.profile = self.load_profile()
            if not self.profile:
                self.logger.error("無法載入個人條件")
                return []
            
            # 載入原始課程資料
            raw_courses = self.load_raw_courses()
            if not raw_courses:
                self.logger.warning("沒有原始課程資料")
                return []
            
            # 篩選課程
            filtered = self.filter_courses(raw_courses)
            
            # 儲存結果
            self.save_filtered_results(filtered)
            
            # 轉換為 schools.yml 格式
            schools_format = self.convert_to_schools_format(filtered)
            
            # 儲存 schools 格式
            self.save_schools_format(schools_format)
            
            self.logger.info(f"=== 篩選完成，找到 {len(filtered)} 個符合的課程 ===")
            return schools_format
        
        except Exception as e:
            self.logger.error(f"篩選過程發生錯誤: {e}")
            return []
    
    def save_schools_format(self, schools: List[Dict[str, Any]]) -> None:
        """儲存 schools 格式"""
        filename = self.output_dir / f"qualified_schools_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yml"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                yaml.dump({'schools': schools}, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            
            self.logger.info(f"Schools 格式已儲存: {filename}")
        except Exception as e:
            self.logger.error(f"儲存 schools 格式失敗: {e}")


def main():
    """主函式"""
    print("""
╔══════════════════════════════════════════════════════════╗
║         智慧課程篩選引擎                                ║
║         Smart Course Filtering Engine                   ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    filter_engine = CourseFilter()
    qualified_schools = filter_engine.run()
    
    print(f"\n✅ 篩選完成！")
    print(f"符合條件的課程: {len(qualified_schools)} 個")
    print(f"結果已儲存至: discovery/")


if __name__ == '__main__':
    main()

