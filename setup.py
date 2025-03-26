import os
import subprocess
import sys
import venv
from pathlib import Path

def create_virtual_environment():
    """Create a virtual environment if it doesn't exist."""
    if not os.path.exists('venv'):
        print("Creating virtual environment...")
        venv.create('venv', with_pip=True)
    else:
        print("Virtual environment already exists.")

def get_python_executable():
    """Get the correct Python executable path based on the OS."""
    if sys.platform == 'win32':
        return os.path.join('venv', 'Scripts', 'python.exe')
    return os.path.join('venv', 'bin', 'python')

def get_pip_executable():
    """Get the correct pip executable path based on the OS."""
    if sys.platform == 'win32':
        return os.path.join('venv', 'Scripts', 'pip.exe')
    return os.path.join('venv', 'bin', 'pip')

def install_requirements():
    """Install the required packages from requirements.txt."""
    pip_executable = get_pip_executable()
    print("Installing required packages...")
    subprocess.check_call([pip_executable, 'install', '-r', 'requirements.txt'])

def create_project_structure():
    """Create the basic project structure."""
    directories = [
        'app',
        'app/static',
        'app/static/css',
        'app/static/js',
        'app/static/images',
        'app/templates',
        'app/models',
        'app/forms',
        'app/routes',
        'migrations',
        'instance'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

def create_initial_files():
    """Create initial project files."""
    # Create __init__.py files
    init_files = [
        'app/__init__.py',
        'app/models/__init__.py',
        'app/forms/__init__.py',
        'app/routes/__init__.py'
    ]
    
    for file in init_files:
        Path(file).touch()
        print(f"Created file: {file}")

def create_desktop_shortcut():
    """Create a desktop shortcut for the application."""
    if sys.platform == 'win32':
        print("Creating desktop shortcut...")
        subprocess.check_call([sys.executable, 'create_shortcut.py'])
    else:
        print("Desktop shortcuts are only supported on Windows.")

def main():
    print("Starting Fitness Leveling app setup...")
    
    # Create virtual environment
    create_virtual_environment()
    
    # Install requirements
    install_requirements()
    
    # Create project structure
    create_project_structure()
    
    # Create initial files
    create_initial_files()
    
    # Create desktop shortcut
    create_desktop_shortcut()
    
    print("\nSetup completed successfully!")
    print("\nTo start using the app:")
    print("1. Double-click the 'Fitness Leveling' shortcut on your desktop")
    print("   OR")
    print("2. Activate the virtual environment:")
    if sys.platform == 'win32':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("   Then run: flask run")

if __name__ == '__main__':
    main() 