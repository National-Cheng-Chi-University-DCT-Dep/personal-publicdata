#!/usr/bin/env python3
"""
Application Document Generator
Generates customized CV and SOP documents for university applications

Usage:
    python generate_docs.py --school taltech
    python generate_docs.py --school aalto
    python generate_docs.py --all
"""

import os
import sys
import yaml
import argparse
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class DocumentGenerator:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.templates_dir = self.base_dir / "templates"
        self.source_data_dir = self.base_dir / "source_data"
        self.output_dir = self.base_dir / "final_applications"
        
        # Load school data
        with open(self.source_data_dir / "schools.yml", 'r', encoding='utf-8') as f:
            self.schools_data = yaml.safe_load(f)
        
        # Load recommender data
        with open(self.source_data_dir / "recommenders.yml", 'r', encoding='utf-8') as f:
            self.recommenders_data = yaml.safe_load(f)

    def get_school_by_id(self, school_id: str) -> Optional[Dict]:
        """Get school information by school_id"""
        for school in self.schools_data['schools']:
            if school['school_id'] == school_id:
                return school
        return None

    def load_template(self, template_name: str) -> str:
        """Load template file content"""
        template_path = self.templates_dir / template_name
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()

    def load_bridge_content(self, bridge_file: str) -> str:
        """Load bridge content for specific school"""
        try:
            bridge_path = self.templates_dir / bridge_file
            with open(bridge_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Remove the "## Bridge:" header since it's already in the master template
                content = re.sub(r'^## Bridge:.*?\n', '', content, flags=re.MULTILINE)
                return content.strip()
        except FileNotFoundError:
            print(f"Warning: Bridge file {bridge_file} not found, using generic content")
            return self._generate_generic_bridge()

    def _generate_generic_bridge(self) -> str:
        """Generate generic bridge content when specific bridge file is not available"""
        return """
        This program represents an ideal opportunity to advance my cybersecurity expertise
        while building the foundation for my long-term research interests in quantum computing
        and AI-driven security systems. The university's strong research focus and practical
        approach to cybersecurity education align perfectly with my professional background
        and academic goals.
        """

    def generate_sop(self, school_id: str) -> str:
        """Generate SOP for specific school"""
        school = self.get_school_by_id(school_id)
        if not school:
            raise ValueError(f"School {school_id} not found")

        # Load master template
        master_template = self.load_template("sop_master_template.md")
        
        # Load bridge content
        bridge_content = self.load_bridge_content(school['sop_bridge_file'])
        
        # Replace placeholders
        sop_content = master_template.replace("{{PROGRAM_NAME}}", school['program'])
        sop_content = sop_content.replace("{{UNIVERSITY_NAME}}", school['school'])
        sop_content = sop_content.replace("{{BRIDGE_CONTENT}}", bridge_content)
        
        return sop_content

    def generate_cv(self, school_id: str) -> str:
        """Generate CV for specific school (currently uses same template for all)"""
        school = self.get_school_by_id(school_id)
        if not school:
            raise ValueError(f"School {school_id} not found")
        
        # Load CV template
        cv_template = self.load_template("cv_template.md")
        
        # For now, CV is the same for all schools
        # In the future, you could add school-specific customizations here
        return cv_template

    def save_document(self, content: str, school_id: str, doc_type: str, format: str = "md"):
        """Save document to appropriate directory"""
        school = self.get_school_by_id(school_id)
        if not school:
            raise ValueError(f"School {school_id} not found")
        
        # Create school directory
        school_dir = self.output_dir / school['school']
        school_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        if doc_type == "sop":
            filename = f"SOP_PeiChenLee_{school['school']}.{format}"
        elif doc_type == "cv":
            filename = f"CV_PeiChenLee.{format}"
        else:
            filename = f"{doc_type}_PeiChenLee_{school['school']}.{format}"
        
        # Save file
        file_path = school_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Generated: {file_path}")
        return file_path

    def convert_to_pdf(self, markdown_path: Path):
        """Convert markdown to PDF (placeholder for future implementation)"""
        # This would use a library like weasyprint or pandoc
        # For now, we'll just create a placeholder
        pdf_path = markdown_path.with_suffix('.pdf')
        print(f"📄 PDF conversion placeholder: {pdf_path}")
        return pdf_path

    def generate_for_school(self, school_id: str):
        """Generate all documents for a specific school"""
        school = self.get_school_by_id(school_id)
        if not school:
            print(f"❌ Error: School '{school_id}' not found")
            return
        
        if school['status'] != 'active':
            print(f"⚠️  Warning: School '{school_id}' status is '{school['status']}', skipping...")
            return
        
        print(f"\n🎯 Generating documents for {school['full_name']} ({school['school']})...")
        
        try:
            # Generate SOP
            sop_content = self.generate_sop(school_id)
            sop_path = self.save_document(sop_content, school_id, "sop")
            
            # Generate CV
            cv_content = self.generate_cv(school_id)
            cv_path = self.save_document(cv_content, school_id, "cv")
            
            # Future: Convert to PDF
            # self.convert_to_pdf(sop_path)
            # self.convert_to_pdf(cv_path)
            
            print(f"✅ Successfully generated documents for {school['school']}")
            
        except Exception as e:
            print(f"❌ Error generating documents for {school['school']}: {str(e)}")

    def generate_all_active_schools(self):
        """Generate documents for all active schools"""
        active_schools = [school for school in self.schools_data['schools'] 
                         if school['status'] == 'active']
        
        print(f"🚀 Generating documents for {len(active_schools)} active schools...")
        
        for school in active_schools:
            self.generate_for_school(school['school_id'])

    def list_schools(self):
        """List all available schools"""
        print("\n📋 Available Schools:")
        print("=" * 60)
        for school in self.schools_data['schools']:
            status_icon = "✅" if school['status'] == 'active' else "⏸️"
            priority_icon = {"high": "🔥", "medium": "⚡", "low": "💫"}.get(school.get('priority_level'), "❓")
            
            print(f"{status_icon} {priority_icon} {school['school_id']:<15} | {school['full_name']}")
            print(f"    Program: {school['program']}")
            print(f"    Country: {school['country']} | Fee: {school['tuition_fee']}")
            print()

def main():
    parser = argparse.ArgumentParser(description='Generate university application documents')
    parser.add_argument('--school', type=str, help='Generate documents for specific school (by school_id)')
    parser.add_argument('--all', action='store_true', help='Generate documents for all active schools')
    parser.add_argument('--list', action='store_true', help='List all available schools')
    
    args = parser.parse_args()
    
    generator = DocumentGenerator()
    
    if args.list:
        generator.list_schools()
    elif args.all:
        generator.generate_all_active_schools()
    elif args.school:
        generator.generate_for_school(args.school)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
