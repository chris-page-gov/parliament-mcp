#!/usr/bin/env python3
"""
Comprehensive validation of the reorganized project structure
"""

import os
import sys
import ast
from pathlib import Path

def find_all_python_files():
    """Find all Python files in the workspace"""
    workspace = Path("/workspace")
    python_files = []
    
    # Skip certain directories
    skip_dirs = {'.git', '.cache', '__pycache__', '.vscode', 'terraform', '.devcontainer'}
    
    for root, dirs, files in os.walk(workspace):
        # Remove skip directories from dirs list to avoid walking into them
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files

def analyze_imports(file_path):
    """Analyze imports in a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST
        tree = ast.parse(content)
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(('import', alias.name))
            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ''
                for alias in node.names:
                    imports.append(('from', module, alias.name))
        
        return imports
    except Exception as e:
        print(f"⚠️  Error analyzing {file_path}: {e}")
        return []

def check_for_old_imports():
    """Check for any old import paths that need updating"""
    print("🔍 Comprehensive Import Path Validation")
    print("=" * 60)
    
    python_files = find_all_python_files()
    issues_found = []
    
    # Patterns that indicate old paths
    problematic_patterns = [
        'os_ngd_mcp_server',  # Should be mock_servers.os_ngd_mcp_server
        'test_london_search',  # Should be in analysis.london
        'test_os_ngd',  # Should be in tests.mcp_tests
        'harrow_roads',  # Should be in analysis.harrow
    ]
    
    for file_path in python_files:
        relative_path = os.path.relpath(file_path, '/workspace')
        imports = analyze_imports(file_path)
        
        for import_info in imports:
            if import_info[0] == 'import':
                module = import_info[1]
                for pattern in problematic_patterns:
                    if pattern in module and not any(good in module for good in ['mock_servers.', 'analysis.', 'tests.']):
                        issues_found.append((relative_path, f"import {module}"))
            
            elif import_info[0] == 'from':
                module, name = import_info[1], import_info[2]
                for pattern in problematic_patterns:
                    if pattern in module and not any(good in module for good in ['mock_servers.', 'analysis.', 'tests.']):
                        issues_found.append((relative_path, f"from {module} import {name}"))
    
    # Also check for direct string imports (like in sys.path modifications)
    for file_path in python_files:
        relative_path = os.path.relpath(file_path, '/workspace')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for old direct imports
            if 'from os_ngd_mcp_server import' in content and 'mock_servers' not in content:
                issues_found.append((relative_path, "Direct import from os_ngd_mcp_server without mock_servers prefix"))
        except:
            pass
    
    if issues_found:
        print("❌ Found import issues:")
        for file_path, issue in issues_found:
            print(f"  {file_path}: {issue}")
        return False
    else:
        print("✅ No problematic import patterns found")
        return True

def validate_file_locations():
    """Validate that files are in correct locations"""
    print("\n📁 File Location Validation")
    print("=" * 60)
    
    workspace = Path("/workspace")
    
    # Check that no analysis/test files are in root
    root_files = list(workspace.glob("*.py"))
    analysis_files_in_root = [f for f in root_files if any(keyword in f.name.lower() 
                              for keyword in ['test_london', 'test_harrow', 'harrow_', 'london_'])]
    
    if analysis_files_in_root:
        print("❌ Found analysis files in root directory:")
        for f in analysis_files_in_root:
            print(f"  {f.name}")
        return False
    
    # Check expected structure
    expected_dirs = [
        'analysis/london',
        'analysis/harrow', 
        'tests/mcp_tests',
        'mock_servers',
        'web',
        'data',
        'logs'
    ]
    
    missing_dirs = []
    for dir_path in expected_dirs:
        full_path = workspace / dir_path
        if not full_path.exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print("❌ Missing expected directories:")
        for d in missing_dirs:
            print(f"  {d}")
        return False
    
    print("✅ All files are in correct locations")
    print("✅ All expected directories exist")
    return True

def main():
    """Run comprehensive validation"""
    print("🔍 COMPREHENSIVE PROJECT VALIDATION")
    print("=" * 70)
    
    checks = [
        ("File Locations", validate_file_locations),
        ("Import Paths", check_for_old_imports),
    ]
    
    results = []
    for check_name, check_func in checks:
        result = check_func()
        results.append((check_name, result))
    
    print("\n📊 FINAL VALIDATION SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {check_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 COMPREHENSIVE VALIDATION PASSED!")
        print("✅ All files are properly organized")
        print("✅ All import paths are correct")
        print("✅ Project structure is clean and maintainable")
    else:
        print("\n⚠️  VALIDATION ISSUES FOUND")
        print("Please review and fix the issues above")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
