#!/usr/bin/env python3
"""
AI Flashcard Generator - Execution Guide & Helper Script

This script helps you set up and run the AI Flashcard Generator project.
It checks prerequisites and guides you through the setup process.
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print formatted header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")


def print_section(text):
    """Print section title."""
    print(f"\n📌 {text}")
    print("-" * 70)


def check_python_version():
    """Check if Python version is compatible."""
    print_section("Checking Python Version")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    
    print("✓ Python version OK")
    return True


def check_pip():
    """Check if pip is available."""
    print_section("Checking pip")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', '--version'],
            capture_output=True,
            text=True
        )
        print(f"pip version: {result.stdout.strip()}")
        print("✓ pip available")
        return True
    except Exception as e:
        print(f"❌ pip check failed: {e}")
        return False


def check_venv():
    """Check if running in virtual environment."""
    print_section("Virtual Environment Check")
    
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ Running in virtual environment")
        return True
    else:
        print("⚠ Not in virtual environment (optional but recommended)")
        return None


def install_dependencies():
    """Install project dependencies."""
    print_section("Installing Dependencies")
    
    req_file = Path('requirements.txt')
    if not req_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    print("Installing packages from requirements.txt...")
    print("This may take several minutes...\n")
    
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            check=True
        )
        print("\n✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Installation failed: {e}")
        return False


def train_model():
    """Run model training."""
    print_section("Training Model")
    
    print("This will download SQuAD v1.1 and train T5-small model")
    print("Estimated time: 30-60 minutes (GPU) or 2-3 hours (CPU)")
    print("Estimated download: ~100MB")
    
    response = input("\nContinue with training? (yes/no): ").lower().strip()
    if response != 'yes':
        print("Training skipped")
        return False
    
    try:
        print("\nStarting training...\n")
        subprocess.run(
            [sys.executable, 'train.py'],
            check=True
        )
        print("\n✓ Training completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Training failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ train.py not found")
        return False


def run_tests():
    """Run installation tests."""
    print_section("Running Tests")
    
    try:
        print("Running installation tests...\n")
        subprocess.run(
            [sys.executable, 'test_installation.py'],
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        print("\n⚠ Some tests failed")
        return False
    except FileNotFoundError:
        print("⚠ test_installation.py not found")
        return None


def launch_web_ui():
    """Launch Streamlit web UI."""
    print_section("Launching Web UI")
    
    print("Starting Streamlit server...")
    print("The web interface will open at http://localhost:8501")
    print("Press Ctrl+C to stop the server\n")
    
    try:
        subprocess.run(
            [sys.executable, '-m', 'streamlit', 'run', 'app.py']
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped")
    except Exception as e:
        print(f"❌ Failed to launch web UI: {e}")
        return False
    
    return True


def show_quick_commands():
    """Display quick command reference."""
    print_header("QUICK COMMAND REFERENCE")
    
    commands = [
        ("Install dependencies", "pip install -r requirements.txt"),
        ("Train model", "python train.py"),
        ("Launch web UI", "streamlit run app.py"),
        ("Run tests", "python test_installation.py"),
        ("View logs", "cat flashcard_t5/logs/*"),
    ]
    
    for desc, cmd in commands:
        print(f"{desc:.<30} {cmd}")


def check_model_exists():
    """Check if trained model exists."""
    model_dir = Path('flashcard_t5')
    return model_dir.exists() and (model_dir / 'pytorch_model.bin').exists()


def main_menu():
    """Main interactive menu."""
    print_header("AI FLASHCARD GENERATOR - SETUP WIZARD")
    
    print("What would you like to do?")
    print("1. Fresh setup (install + train)")
    print("2. Install dependencies only")
    print("3. Train model")
    print("4. Run tests")
    print("5. Launch web UI")
    print("6. Show commands")
    print("0. Exit")
    
    choice = input("\nSelect option (0-6): ").strip()
    
    if choice == '1':
        print_header("FRESH SETUP")
        if not check_python_version():
            return False
        if not check_pip():
            return False
        if not install_dependencies():
            return False
        if not train_model():
            return False
        if not run_tests():
            return False
        if input("\nLaunch web UI now? (yes/no): ").lower() == 'yes':
            launch_web_ui()
        return True
    
    elif choice == '2':
        if not check_python_version():
            return False
        if not install_dependencies():
            return False
        return True
    
    elif choice == '3':
        if not check_model_exists():
            print("\n⚠ Model directory not found. Install dependencies first.")
            return False
        if not train_model():
            return False
        return True
    
    elif choice == '4':
        if not check_model_exists():
            print("\n⚠ Model not trained yet. Run 'Train model' first.")
            return False
        run_tests()
        return True
    
    elif choice == '5':
        if not check_model_exists():
            print("\n❌ Model not found. Run training first:")
            print("   python train.py")
            return False
        launch_web_ui()
        return True
    
    elif choice == '6':
        show_quick_commands()
        return True
    
    elif choice == '0':
        print("\nGoodbye!")
        return True
    
    else:
        print("Invalid option")
        return False


def automated_setup():
    """Run automated setup (non-interactive)."""
    print_header("AUTOMATED SETUP")
    
    steps = [
        ("Checking Python", check_python_version),
        ("Checking pip", check_pip),
        ("Installing dependencies", install_dependencies),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            return False
    
    print_header("SETUP COMPLETE!")
    print("Next steps:")
    print("1. Run: python train.py")
    print("2. Run: streamlit run app.py")
    print("3. Open: http://localhost:8501")
    
    return True


if __name__ == '__main__':
    os.chdir(Path(__file__).parent)
    
    # Check for command-line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--auto':
            sys.exit(0 if automated_setup() else 1)
        elif sys.argv[1] == '--train':
            if check_model_exists():
                sys.exit(0 if train_model() else 1)
            else:
                print("❌ Install dependencies first: pip install -r requirements.txt")
                sys.exit(1)
        elif sys.argv[1] == '--ui':
            if check_model_exists():
                sys.exit(0 if launch_web_ui() else 1)
            else:
                print("❌ Model not found. Run: python train.py")
                sys.exit(1)
        elif sys.argv[1] == '--help':
            print("Usage: python run.py [OPTION]")
            print("Options:")
            print("  --auto      Run automated setup")
            print("  --train     Run model training")
            print("  --ui        Launch web UI")
            print("  --help      Show this help")
            sys.exit(0)
    
    # Interactive menu
    try:
        success = main_menu()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
