#!/usr/bin/env python3
"""
Test script specifically for verifying blank field saving functionality in projects.
This tests the fix for the issue where editing projects to remove data was not working.
"""

import requests
import sys
import json
from datetime import datetime

class ProjectBlankFieldsTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.token = None
        self.test_project_id = None
        
    def login(self):
        """Login as admin to get authentication token"""
        print("🔐 Logging in as admin...")
        
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"username": "admin", "password": "@dminsesg705"}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get('access_token')
            print(f"✅ Login successful, token obtained")
            return True
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    
    def get_headers(self):
        """Get headers with authentication"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}' if self.token else ''
        }
    
    def get_existing_projects(self):
        """Get list of existing projects"""
        print("\n📋 Getting existing projects...")
        
        response = requests.get(f"{self.base_url}/api/projects")
        
        if response.status_code == 200:
            projects = response.json()
            print(f"✅ Found {len(projects)} existing projects")
            return projects
        else:
            print(f"❌ Failed to get projects: {response.status_code}")
            return []
    
    def create_test_project(self):
        """Create a test project with all fields populated"""
        print("\n🆕 Creating test project with all fields populated...")
        
        project_data = {
            "name": "Test Project for Blank Fields",
            "description": "This project is created to test the blank field saving functionality",
            "start_date": "2024-01-15",
            "end_date": "2025-12-31",
            "team_leader": "Dr. Test Leader",
            "team_members": "Dr. Member One, Dr. Member Two, Dr. Member Three",
            "funded_by": "Test Funding Agency",
            "total_members": 5,
            "status": "ongoing",
            "research_area": "Test Research Area",
            "project_link": "https://example.com/test-project",
            "image": "https://example.com/test-image.jpg"
        }
        
        response = requests.post(
            f"{self.base_url}/api/projects",
            json=project_data,
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            project = response.json()
            self.test_project_id = project.get('id')
            print(f"✅ Test project created with ID: {self.test_project_id}")
            print(f"   Team Leader: {project.get('team_leader')}")
            print(f"   Team Members: {project.get('team_members')}")
            print(f"   Funded By: {project.get('funded_by')}")
            return project
        else:
            print(f"❌ Failed to create test project: {response.status_code} - {response.text}")
            return None
    
    def update_project_with_blank_fields(self):
        """Update the test project to clear specific fields"""
        print(f"\n🔄 Updating project {self.test_project_id} to clear fields...")
        
        # Update with blank/empty values for key fields
        update_data = {
            "name": "Test Project for Blank Fields",  # Keep name (required)
            "description": "This project is created to test the blank field saving functionality",  # Keep description (required)
            "start_date": "2024-01-15",  # Keep dates
            "end_date": "2025-12-31",
            "team_leader": "",  # CLEAR THIS FIELD
            "team_members": "",  # CLEAR THIS FIELD  
            "funded_by": "",  # CLEAR THIS FIELD
            "total_members": 5,  # Keep this
            "status": "ongoing",  # Keep status (required)
            "research_area": "",  # CLEAR THIS FIELD
            "project_link": "",  # CLEAR THIS FIELD
            "image": ""  # CLEAR THIS FIELD
        }
        
        response = requests.put(
            f"{self.base_url}/api/projects/{self.test_project_id}",
            json=update_data,
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            updated_project = response.json()
            print("✅ Project updated successfully")
            print(f"   Team Leader: '{updated_project.get('team_leader')}'")
            print(f"   Team Members: '{updated_project.get('team_members')}'")
            print(f"   Funded By: '{updated_project.get('funded_by')}'")
            print(f"   Research Area: '{updated_project.get('research_area')}'")
            print(f"   Project Link: '{updated_project.get('project_link')}'")
            print(f"   Image: '{updated_project.get('image')}'")
            return updated_project
        else:
            print(f"❌ Failed to update project: {response.status_code} - {response.text}")
            return None
    
    def verify_blank_fields_persisted(self):
        """Verify that blank fields are actually saved and persisted"""
        print(f"\n🔍 Verifying blank fields persisted for project {self.test_project_id}...")
        
        response = requests.get(f"{self.base_url}/api/projects")
        
        if response.status_code == 200:
            projects = response.json()
            test_project = None
            
            for project in projects:
                if project.get('id') == self.test_project_id:
                    test_project = project
                    break
            
            if test_project:
                print("✅ Found test project in database")
                
                # Check if fields are actually blank/empty
                fields_to_check = ['team_leader', 'team_members', 'funded_by', 'research_area', 'project_link', 'image']
                all_blank = True
                
                for field in fields_to_check:
                    value = test_project.get(field)
                    is_blank = value == "" or value is None
                    status = "✅ BLANK" if is_blank else f"❌ NOT BLANK ('{value}')"
                    print(f"   {field}: {status}")
                    
                    if not is_blank:
                        all_blank = False
                
                return all_blank
            else:
                print("❌ Test project not found in database")
                return False
        else:
            print(f"❌ Failed to retrieve projects: {response.status_code}")
            return False
    
    def cleanup_test_project(self):
        """Clean up the test project"""
        if self.test_project_id:
            print(f"\n🧹 Cleaning up test project {self.test_project_id}...")
            
            response = requests.delete(
                f"{self.base_url}/api/projects/{self.test_project_id}",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                print("✅ Test project cleaned up successfully")
            else:
                print(f"⚠️  Failed to clean up test project: {response.status_code}")
    
    def run_full_test(self):
        """Run the complete test suite"""
        print("🚀 Starting Project Blank Fields Test")
        print("=" * 60)
        
        # Step 1: Login
        if not self.login():
            return False
        
        # Step 2: Get existing projects (for context)
        existing_projects = self.get_existing_projects()
        
        # Step 3: Create test project with populated fields
        created_project = self.create_test_project()
        if not created_project:
            return False
        
        # Step 4: Update project to clear fields
        updated_project = self.update_project_with_blank_fields()
        if not updated_project:
            return False
        
        # Step 5: Verify blank fields persisted
        fields_cleared = self.verify_blank_fields_persisted()
        
        # Step 6: Cleanup
        self.cleanup_test_project()
        
        # Final result
        print("\n" + "=" * 60)
        if fields_cleared:
            print("🎉 SUCCESS: Blank field saving functionality is working correctly!")
            print("   ✅ Fields can be cleared by setting them to empty strings")
            print("   ✅ Blank fields persist after saving")
            print("   ✅ No reversion to old data occurs")
        else:
            print("❌ FAILURE: Blank field saving functionality is NOT working correctly!")
            print("   ❌ Some fields did not remain blank after saving")
            print("   ❌ Old data may be persisting instead of being cleared")
        
        return fields_cleared

def main():
    tester = ProjectBlankFieldsTester()
    success = tester.run_full_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())