#!/usr/bin/env python3
"""
Validate the reorganized project structure and dependencies
"""

import os
import sys
from pathlib import Path

def check_file_structure():
    """Verify all files are in their expected locations"""
    print("🔍 Validating Project Structure...")
    print("=" * 50)
    
    expected_structure = {
        "analysis/london/": [
            "london_constituencies_bulleted.py",
            "test_london_search.py", 
            "test_london_search_refined.py"
        ],
        "analysis/harrow/": [
            "find_harrow_crossing_roads.py",
            "get_harrow_map.py",
            "harrow_roads_analysis.py"
        ],
        "tests/mcp_tests/": [
            "test_os_ngd_api.py",
            "test_os_ngd_mcp_integration.py",
            "test_real_os_mcp.py",
            "simple_os_ngd_test.py"
        ],
        "web/": [
            "harrow_os_map.html"
        ],
        "mock_servers/": [
            "os_ngd_mcp_server.py"
        ],
        "data/": [
            "constituency_list.txt"
        ],
        "logs/": []  # May be empty, that's fine
    }
    
    workspace = Path("/workspace")
    all_good = True
    
    for directory, files in expected_structure.items():
        dir_path = workspace / directory
        
        if not dir_path.exists():
            print(f"❌ Missing directory: {directory}")
            all_good = False
            continue
            
        print(f"✅ Directory exists: {directory}")
        
        for file in files:
            file_path = dir_path / file
            if not file_path.exists():
                print(f"  ❌ Missing file: {directory}{file}")
                all_good = False
            else:
                print(f"  ✅ File exists: {file}")
    
    return all_good

def check_import_dependencies():
    """Check if import paths are correct in moved files"""
    print("\n🔧 Checking Import Dependencies...")
    print("=" * 50)
    
    # Files that should import from mock_servers
    files_to_check = [
        "/workspace/tests/mcp_tests/test_os_ngd_mcp_integration.py"
    ]
    
    all_good = True
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            all_good = False
            continue
            
        with open(file_path, 'r') as f:
            content = f.read()
            
        if "from mock_servers.os_ngd_mcp_server import OSNGDClient" in content:
            print(f"✅ Correct import in: {os.path.basename(file_path)}")
        elif "from os_ngd_mcp_server import OSNGDClient" in content:
            print(f"❌ Old import path in: {os.path.basename(file_path)}")
            all_good = False
        else:
            print(f"⚠️  No relevant imports in: {os.path.basename(file_path)}")
    
    return all_good

def check_mcp_configuration():
    """Verify MCP configuration is still valid"""
    print("\n⚙️  Checking MCP Configuration...")
    print("=" * 50)
    
    mcp_config_path = "/workspace/.vscode/mcp.json"
    
    if not os.path.exists(mcp_config_path):
        print("❌ MCP configuration file missing")
        return False
    
    try:
        import json
        with open(mcp_config_path, 'r') as f:
            # Remove JSON comments for parsing
            content = f.read()
            # Simple comment removal (not perfect but works for this case)
            lines = content.split('\n')
            cleaned_lines = []
            for line in lines:
                if '//' not in line:
                    cleaned_lines.append(line)
                else:
                    # Keep the part before the comment
                    cleaned_lines.append(line.split('//')[0].rstrip())
            cleaned_content = '\n'.join(cleaned_lines)
            
            config = json.loads(cleaned_content)
        
        if "servers" in config:
            servers = config["servers"]
            if "parliament-mcp" in servers and "os-ngd-api" in servers:
                print("✅ Both MCP servers configured")
                
                # Check paths exist
                parliament_path = "/workspace/mcp_server"
                os_mcp_path = "/workspace/os-mcp"
                
                if os.path.exists(parliament_path):
                    print("✅ Parliament MCP path exists")
                else:
                    print("❌ Parliament MCP path missing")
                    return False
                    
                if os.path.exists(os_mcp_path):
                    print("✅ OS MCP path exists")
                else:
                    print("❌ OS MCP path missing")
                    return False
                    
                return True
            else:
                print("❌ Missing MCP server configurations")
                return False
        else:
            print("❌ Invalid MCP configuration format")
            return False
            
    except Exception as e:
        print(f"❌ Error reading MCP configuration: {e}")
        return False

def check_security_fixes():
    """Verify security issues are fixed"""
    print("\n🔒 Checking Security Fixes...")
    print("=" * 50)
    
    html_file = "/workspace/web/harrow_os_map.html"
    
    if not os.path.exists(html_file):
        print("❌ HTML file not found")
        return False
    
    with open(html_file, 'r') as f:
        content = f.read()
    
    # Check for API key exposure
    if "key=test_key" in content or "key=" in content:
        print("❌ API key still exposed in HTML")
        return False
    
    if "Security Notice" in content:
        print("✅ Security warning added to HTML")
    else:
        print("⚠️  No security warning found")
        
    if "api.os.uk" not in content:
        print("✅ No direct OS API calls in HTML")
        return True
    else:
        print("❌ Direct API calls still present")
        return False

def main():
    """Run all validation checks"""
    print("🔍 Project Structure Validation")
    print("=" * 60)
    
    checks = [
        ("File Structure", check_file_structure),
        ("Import Dependencies", check_import_dependencies), 
        ("MCP Configuration", check_mcp_configuration),
        ("Security Fixes", check_security_fixes)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        result = check_func()
        results.append((check_name, result))
    
    print("\n📊 Validation Summary")
    print("=" * 60)
    
    all_passed = True
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {check_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All validation checks passed!")
        print("✅ Project structure is properly organized")
        print("✅ Dependencies are correctly updated")
        print("✅ Security issues are resolved") 
        print("✅ MCP configuration is valid")
    else:
        print("\n⚠️  Some validation checks failed")
        print("Please review the issues above and fix them")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
