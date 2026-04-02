#!/usr/bin/env python
"""
Validation script to check that the IncidentCommander environment is set up correctly.
Run this before deployment to catch any issues early.
"""

import sys
import os
from pathlib import Path

def check_structure():
    """Verify all required files exist."""
    print("\n📁 Checking project structure...")
    
    required_files = [
        "app.py",
        "inference.py",
        "requirements.txt",
        "Dockerfile",
        "openenv.yaml",
        "README.md",
        "LICENSE",
        "env/__init__.py",
        "env/models.py",
        "env/environment.py",
        "env/incidents.py",
        "env/rewards.py",
        "env/graders.py",
        "data/__init__.py",
        "data/scenarios.py",
        "data/log_templates.py",
        "data/metrics_data.py",
        "tasks/__init__.py",
        "tasks/task_easy.py",
        "tasks/task_medium.py",
        "tasks/task_hard.py",
        "tests/__init__.py",
        "tests/test_env.py",
    ]
    
    all_exist = True
    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (MISSING)")
            all_exist = False
    
    return all_exist


def check_imports():
    """Verify all imports work."""
    print("\n🔗 Checking imports...")
    
    modules_to_check = [
        ("env.models", ["Action", "Observation", "EnvironmentState"]),
        ("env.environment", ["IncidentCommanderEnv"]),
        ("env.incidents", ["IncidentGenerator"]),
        ("env.rewards", ["RewardCalculator"]),
        ("env.graders", ["get_grader"]),
        ("data.scenarios", ["get_scenario"]),
        ("data.log_templates", ["LOG_TEMPLATES"]),
        ("data.metrics_data", ["SERVICE_DEPENDENCIES"]),
    ]
    
    all_imports_ok = True
    for module_name, items in modules_to_check:
        try:
            module = __import__(module_name, fromlist=items)
            for item in items:
                if hasattr(module, item):
                    print(f"  ✓ {module_name}.{item}")
                else:
                    print(f"  ✗ {module_name}.{item} (not found)")
                    all_imports_ok = False
        except Exception as e:
            print(f"  ✗ {module_name} (import failed: {e})")
            all_imports_ok = False
    
    return all_imports_ok


def check_dependencies():
    """Verify dependencies are installed."""
    print("\n📦 Checking dependencies...")
    
    dependencies = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "openai",
        "requests",
    ]
    
    all_installed = True
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  ✓ {dep}")
        except ImportError:
            print(f"  ✗ {dep} (NOT INSTALLED)")
            all_installed = False
    
    return all_installed


def check_environment_functionality():
    """Test basic environment functionality."""
    print("\n🧪 Testing environment functionality...")
    
    try:
        from env.environment import IncidentCommanderEnv
        from env.models import Action
        
        # Create environment
        env = IncidentCommanderEnv()
        print("  ✓ Environment created")
        
        # Reset
        obs = env.reset("single_service_outage", "easy")
        print("  ✓ Reset works")
        
        # Take action
        action = Action(
            action_type="check_logs",
            target_service="payment-service"
        )
        obs, reward, done, info = env.step(action)
        print("  ✓ Step works")
        
        # Get state
        state = env.state()
        print("  ✓ State retrieval works")
        
        # Check observation has required fields
        assert obs.timestamp is not None
        assert obs.active_alerts is not None
        assert obs.recent_logs is not None
        print("  ✓ Observation structure is valid")
        
        # Check state has required fields
        assert state.incident_id is not None
        assert state.root_causes is not None
        assert state.score is not None
        print("  ✓ State structure is valid")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Environment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_openenv_yaml():
    """Validate openenv.yaml structure."""
    print("\n📋 Checking openenv.yaml...")
    
    try:
        import yaml
        with open("openenv.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        required_fields = ["name", "description", "version", "tasks"]
        for field in required_fields:
            if field in config:
                print(f"  ✓ {field} present")
            else:
                print(f"  ✗ {field} missing")
                return False
        
        if len(config.get("tasks", [])) >= 3:
            print(f"  ✓ All 3 tasks defined")
            return True
        else:
            print(f"  ✗ Not all tasks defined")
            return False
    
    except Exception as e:
        print(f"  ✗ openenv.yaml validation failed: {e}")
        return False


def main():
    """Run all checks."""
    print("=" * 60)
    print("IncidentCommander Environment Validation")
    print("=" * 60)
    
    checks = [
        ("Project Structure", check_structure),
        ("Module Imports", check_imports),
        ("Dependencies", check_dependencies),
        ("OpenEnv Config", check_openenv_yaml),
        ("Environment Functionality", check_environment_functionality),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n✗ {name} check failed with exception: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {name}")
    
    all_pass = all(results.values())
    
    if all_pass:
        print("\n✓ All checks passed! Ready for deployment.")
        return 0
    else:
        print("\n✗ Some checks failed. Please fix issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
