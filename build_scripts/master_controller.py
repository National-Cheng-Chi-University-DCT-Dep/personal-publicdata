#!/usr/bin/env python3
"""
University Application Intelligence System - Master Controller
Complete automation pipeline for intelligent university application management

Features:
- Coordinated data collection, validation, and document generation
- Academic intelligence gathering
- Monitoring and alerting
- GitHub integration for task management
- Comprehensive reporting and dashboards
"""

import os
import sys
import argparse
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import system modules with error handling
try:
    from build_scripts.generate_docs import DocumentGenerator
except ImportError as e:
    print(f"[WARNING] Could not import DocumentGenerator: {e}")
    DocumentGenerator = None

try:
    from data_collection.scraper import UniversityScraper
except ImportError as e:
    print(f"[WARNING] Could not import UniversityScraper: {e}")
    UniversityScraper = None

try:
    from data_collection.validator import ApplicationValidator
except ImportError as e:
    print(f"[WARNING] Could not import ApplicationValidator: {e}")
    ApplicationValidator = None

try:
    from monitoring.dashboard import ApplicationDashboard
except ImportError as e:
    print(f"[WARNING] Could not import ApplicationDashboard: {e}")
    ApplicationDashboard = None

try:
    from notifications.alert_system import NotificationCenter
except ImportError as e:
    print(f"[WARNING] Could not import NotificationCenter: {e}")
    NotificationCenter = None

try:
    from analysis.academic_radar import AcademicRadar
except ImportError as e:
    print(f"[WARNING] Could not import AcademicRadar: {e}")
    AcademicRadar = None

class ApplicationIntelligenceSystem:
    """Master controller for the complete application intelligence system"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.base_dir = Path(__file__).parent.parent
        
        # Initialize system components with error handling
        self.document_generator = DocumentGenerator() if DocumentGenerator else None
        self.scraper = UniversityScraper() if UniversityScraper else None
        self.validator = ApplicationValidator() if ApplicationValidator else None
        self.dashboard = ApplicationDashboard() if ApplicationDashboard else None
        self.notification_center = NotificationCenter() if NotificationCenter else None
        self.academic_radar = AcademicRadar() if AcademicRadar else None
        
        # Check which components are available
        available_components = []
        if self.document_generator: available_components.append("DocumentGenerator")
        if self.scraper: available_components.append("UniversityScraper")
        if self.validator: available_components.append("ApplicationValidator")
        if self.dashboard: available_components.append("ApplicationDashboard")
        if self.notification_center: available_components.append("NotificationCenter")
        if self.academic_radar: available_components.append("AcademicRadar")
        
        if self.verbose:
            print(f"[COMPONENTS] Available components: {', '.join(available_components)}")
            if len(available_components) < 6:
                print("[WARNING] Some components are unavailable due to missing dependencies")
        
        # Execution results
        self.execution_log = []
        self.errors = []
    
    def log(self, message: str, level: str = "INFO"):
        """Log execution messages"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {level}: {message}"
        
        if self.verbose or level in ["ERROR", "WARNING"]:
            print(log_entry)
        
        self.execution_log.append(log_entry)
        
        if level == "ERROR":
            self.errors.append(message)
    
    def run_data_collection(self) -> bool:
        """Execute data collection pipeline"""
        self.log("[COLLECTION] Starting data collection pipeline...")
        
        if not self.scraper:
            self.log("[WARNING] Scraper not available - skipping data collection", "WARNING")
            return False
        
        try:
            # Run web scraper
            self.log("Running university data scraper...")
            scraper_results = self.scraper.scrape_all_schools()
            self.scraper.save_scraped_data(scraper_results)
            
            successful_scrapes = sum(1 for data in scraper_results.values() 
                                   if data.confidence_score > 0)
            self.log(f"Scraper completed: {successful_scrapes}/{len(scraper_results)} successful")
            
            return True
            
        except Exception as e:
            self.log(f"Data collection failed: {str(e)}", "ERROR")
            return False
        
        finally:
            if self.scraper:
                self.scraper.cleanup()
    
    def run_data_validation(self) -> bool:
        """Execute data validation pipeline"""
        self.log("[VALIDATION] Starting data validation pipeline...")
        
        if not self.validator:
            self.log("[WARNING] Validator not available - skipping data validation", "WARNING")
            return False
        
        try:
            # Run validator
            self.log("Validating scraped data and application eligibility...")
            validation_results = self.validator.validate_all_schools()
            self.validator.save_validation_report(validation_results)
            
            eligible_count = sum(1 for r in validation_results.values() 
                               if r.overall_status == "ELIGIBLE")
            self.log(f"Validation completed: {eligible_count} schools eligible")
            
            return True
            
        except Exception as e:
            self.log(f"Data validation failed: {str(e)}", "ERROR")
            return False
    
    def run_academic_intelligence(self) -> bool:
        """Execute academic intelligence gathering"""
        self.log("🔬 Starting academic intelligence gathering...")
        
        try:
            # Run academic radar for priority schools
            target_schools = ['taltech', 'aalto']  # High priority schools
            school_analyses = {}
            
            for school_id in target_schools:
                self.log(f"Analyzing research opportunities for {school_id}...")
                analysis = self.academic_radar.analyze_research_opportunities(school_id)
                school_analyses[school_id] = analysis
                
                # Small delay between schools
                time.sleep(1)
            
            # Save academic intelligence
            self.academic_radar.save_academic_intelligence(school_analyses)
            
            total_opportunities = sum(len(analysis['action_items']) 
                                    for analysis in school_analyses.values())
            self.log(f"Academic intelligence completed: {total_opportunities} opportunities identified")
            
            return True
            
        except Exception as e:
            self.log(f"Academic intelligence failed: {str(e)}", "ERROR")
            return False
    
    def run_document_generation(self, school_ids: Optional[List[str]] = None) -> bool:
        """Execute document generation"""
        self.log("[DOCUMENTS] Starting document generation...")
        
        try:
            if school_ids:
                # Generate for specific schools
                for school_id in school_ids:
                    self.log(f"Generating documents for {school_id}...")
                    self.document_generator.generate_for_school(school_id)
            else:
                # Generate for all active schools
                self.log("Generating documents for all active schools...")
                self.document_generator.generate_all_active_schools()
            
            self.log("Document generation completed")
            return True
            
        except Exception as e:
            self.log(f"Document generation failed: {str(e)}", "ERROR")
            return False
    
    def run_monitoring_dashboard(self) -> bool:
        """Generate monitoring dashboard"""
        self.log("[DASHBOARD] Generating monitoring dashboard...")
        
        try:
            self.dashboard.save_dashboard()
            self.log("Dashboard generation completed")
            return True
            
        except Exception as e:
            self.log(f"Dashboard generation failed: {str(e)}", "ERROR")
            return False
    
    def run_notifications(self) -> bool:
        """Execute notification and alerting system"""
        self.log("[NOTIFICATIONS] Processing notifications and alerts...")
        
        if not self.notification_center:
            self.log("[WARNING] Notification center not available - skipping notifications", "WARNING")
            return False
        
        try:
            summary = self.notification_center.process_all_alerts()
            
            total_alerts = summary['total_alerts']
            created_issues = summary['created_github_issues']
            
            self.log(f"Notifications completed: {total_alerts} alerts, {created_issues} GitHub issues created")
            return True
            
        except Exception as e:
            self.log(f"Notification processing failed: {str(e)}", "ERROR")
            return False
    
    def run_validation_summary(self) -> bool:
        """Execute validation summary safely"""
        self.log("[SUMMARY] Generating validation summary...")
        
        try:
            # Import the validation summary module
            import sys
            validation_summary_path = self.base_dir / "data_collection" / "validation_summary.py"
            
            if validation_summary_path.exists():
                # Run the validation summary script
                import subprocess
                result = subprocess.run([
                    sys.executable, str(validation_summary_path)
                ], capture_output=True, text=True, cwd=str(self.base_dir))
                
                if result.returncode == 0:
                    # Print the summary output
                    if result.stdout:
                        print(result.stdout)
                    self.log("Validation summary completed successfully")
                    return True
                else:
                    self.log(f"Validation summary failed: {result.stderr}", "ERROR")
                    return False
            else:
                self.log("Validation summary script not found", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"Validation summary failed: {str(e)}", "ERROR")
            return False
    
    def run_full_pipeline(self, skip_scraping: bool = False, 
                         target_schools: Optional[List[str]] = None) -> Dict[str, bool]:
        """Execute the complete intelligence pipeline"""
        self.log("🚀 Starting complete application intelligence pipeline...")
        
        pipeline_results = {}
        
        # Stage 1: Data Collection (optional skip for speed)
        if not skip_scraping:
            pipeline_results['data_collection'] = self.run_data_collection()
        else:
            self.log("⏭️  Skipping data collection (using existing data)")
            pipeline_results['data_collection'] = True
        
        # Stage 2: Data Validation
        pipeline_results['data_validation'] = self.run_data_validation()
        
        # Run validation summary if validation was successful
        if pipeline_results['data_validation']:
            self.run_validation_summary()
        
        # Stage 3: Academic Intelligence
        pipeline_results['academic_intelligence'] = self.run_academic_intelligence()
        
        # Stage 4: Document Generation
        pipeline_results['document_generation'] = self.run_document_generation(target_schools)
        
        # Stage 5: Monitoring Dashboard
        pipeline_results['monitoring_dashboard'] = self.run_monitoring_dashboard()
        
        # Stage 6: Notifications and Alerts
        pipeline_results['notifications'] = self.run_notifications()
        
        # Pipeline completion summary
        successful_stages = sum(1 for success in pipeline_results.values() if success)
        total_stages = len(pipeline_results)
        
        self.log(f"🏁 Pipeline completed: {successful_stages}/{total_stages} stages successful")
        
        if self.errors:
            self.log(f"[WARNING] {len(self.errors)} errors encountered during execution", "WARNING")
        
        return pipeline_results
    
    def run_quick_update(self) -> Dict[str, bool]:
        """Execute quick update pipeline (no scraping, focus on analysis)"""
        self.log("⚡ Running quick update pipeline...")
        
        results = {}
        
        # Quick validation with existing data
        results['validation'] = self.run_data_validation()
        
        # Run validation summary if validation was successful
        if results['validation']:
            self.run_validation_summary()
        
        # Generate documents
        results['documents'] = self.run_document_generation()
        
        # Update dashboard
        results['dashboard'] = self.run_monitoring_dashboard()
        
        # Check alerts
        results['alerts'] = self.run_notifications()
        
        return results
    
    def generate_execution_report(self, pipeline_results: Dict[str, bool]) -> str:
        """Generate detailed execution report"""
        report_lines = [
            "# 🎓 Application Intelligence System - Execution Report",
            "",
            f"**Execution Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Pipeline Version**: 2.0.0",
            "",
            "## [RESULTS] Pipeline Results",
            ""
        ]
        
        # Results table
        report_lines.extend([
            "| Stage | Status | Details |",
            "|-------|--------|---------|"
        ])
        
        stage_names = {
            'data_collection': '[COLLECTION] Data Collection',
            'data_validation': '[VALIDATION] Data Validation',
            'academic_intelligence': '🔬 Academic Intelligence',
            'document_generation': '[DOCUMENTS] Document Generation',
            'monitoring_dashboard': '[DASHBOARD] Monitoring Dashboard', 
            'notifications': '[NOTIFICATIONS] Notifications & Alerts'
        }
        
        for stage_key, success in pipeline_results.items():
            stage_name = stage_names.get(stage_key, stage_key)
            status_icon = "[SUCCESS]" if success else "[FAILED]"
            status_text = "SUCCESS" if success else "FAILED"
            
            report_lines.append(f"| {stage_name} | {status_icon} {status_text} | - |")
        
        # Execution log
        if self.execution_log:
            report_lines.extend([
                "",
                "## [LOG] Detailed Execution Log",
                "",
                "```"
            ])
            
            # Show last 20 log entries
            for log_entry in self.execution_log[-20:]:
                report_lines.append(log_entry)
            
            report_lines.extend([
                "```",
                ""
            ])
        
        # Errors summary
        if self.errors:
            report_lines.extend([
                "## [ERRORS] Errors Encountered",
                ""
            ])
            
            for error in self.errors:
                report_lines.append(f"- {error}")
            
            report_lines.append("")
        
        # Generated files summary
        output_dir = self.base_dir / "final_applications"
        if output_dir.exists():
            files = list(output_dir.rglob("*.md")) + list(output_dir.rglob("*.json"))
            
            if files:
                report_lines.extend([
                    "## [FILES] Generated Files",
                    ""
                ])
                
                for file_path in sorted(files):
                    rel_path = file_path.relative_to(output_dir)
                    file_size = file_path.stat().st_size
                    report_lines.append(f"- `{rel_path}` ({file_size:,} bytes)")
                
                report_lines.append("")
        
        # Next steps
        successful_stages = sum(1 for success in pipeline_results.values() if success)
        total_stages = len(pipeline_results)
        
        if successful_stages == total_stages:
            report_lines.extend([
                "## [NEXT] Next Steps",
                "",
                "All pipeline stages completed successfully. You can now:",
                "",
                "1. Review the generated documents in `final_applications/`",
                "2. Check the application dashboard for status updates",
                "3. Address any alerts created in GitHub Issues",
                "4. Use the academic intelligence report to enhance your SOPs",
                ""
            ])
        else:
            report_lines.extend([
                "## [ACTION] Action Required",
                "",
                "Some pipeline stages failed. Please:",
                "",
                "1. Review the error log above",
                "2. Fix any configuration or dependency issues", 
                "3. Re-run the failed stages",
                "4. Check system requirements and credentials",
                ""
            ])
        
        report_lines.extend([
            "---",
            "",
            "*Report generated by Application Intelligence System v2.0*"
        ])
        
        return "\n".join(report_lines)
    
    def save_execution_report(self, pipeline_results: Dict[str, bool]):
        """Save execution report to file"""
        report_content = self.generate_execution_report(pipeline_results)
        
        output_dir = self.base_dir / "final_applications"
        output_dir.mkdir(exist_ok=True)
        
        report_file = output_dir / "execution_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.log(f"[REPORT] Execution report saved to {report_file}")

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='University Application Intelligence System - Master Controller'
    )
    
    # Pipeline options
    parser.add_argument('--full', action='store_true', 
                       help='Run complete pipeline including data collection')
    parser.add_argument('--quick', action='store_true',
                       help='Run quick update pipeline (no scraping)')
    parser.add_argument('--schools', nargs='+', 
                       help='Target specific schools (space-separated school IDs)')
    
    # Component options
    parser.add_argument('--scrape-only', action='store_true',
                       help='Run data collection only')
    parser.add_argument('--validate-only', action='store_true',
                       help='Run validation only')
    parser.add_argument('--docs-only', action='store_true',
                       help='Run document generation only')
    parser.add_argument('--dashboard-only', action='store_true',
                       help='Run dashboard generation only')
    parser.add_argument('--alerts-only', action='store_true',
                       help='Run notifications only')
    parser.add_argument('--academic-only', action='store_true',
                       help='Run academic intelligence only')
    
    # Options
    parser.add_argument('--skip-scraping', action='store_true',
                       help='Skip data collection in full pipeline')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--save-report', action='store_true',
                       help='Save detailed execution report')
    
    args = parser.parse_args()
    
    # Initialize system
    system = ApplicationIntelligenceSystem(verbose=args.verbose)
    
    try:
        pipeline_results = {}
        
        # Execute based on arguments
        if args.full:
            pipeline_results = system.run_full_pipeline(
                skip_scraping=args.skip_scraping,
                target_schools=args.schools
            )
        
        elif args.quick:
            pipeline_results = system.run_quick_update()
        
        # Individual component execution
        elif args.scrape_only:
            pipeline_results['scraping'] = system.run_data_collection()
        
        elif args.validate_only:
            pipeline_results['validation'] = system.run_data_validation()
        
        elif args.docs_only:
            pipeline_results['documents'] = system.run_document_generation(args.schools)
        
        elif args.dashboard_only:
            pipeline_results['dashboard'] = system.run_monitoring_dashboard()
        
        elif args.alerts_only:
            pipeline_results['alerts'] = system.run_notifications()
        
        elif args.academic_only:
            pipeline_results['academic'] = system.run_academic_intelligence()
        
        else:
            # Default: run quick pipeline
            print("No specific pipeline specified. Running quick update...")
            pipeline_results = system.run_quick_update()
        
        # Save execution report if requested
        if args.save_report and pipeline_results:
            system.save_execution_report(pipeline_results)
        
        # Return appropriate exit code
        if pipeline_results:
            failed_stages = [stage for stage, success in pipeline_results.items() if not success]
            if failed_stages:
                print(f"\n[FAILED] Pipeline completed with {len(failed_stages)} failed stages")
                return 1
            else:
                print(f"\n[SUCCESS] Pipeline completed successfully!")
                return 0
        else:
            print("\n[ERROR] No pipeline executed")
            return 1
    
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Pipeline interrupted by user")
        return 130
    
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed with error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
