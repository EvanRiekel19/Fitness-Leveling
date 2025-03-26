import os
import sys
from pathlib import Path

def create_desktop_shortcut():
    # Get the desktop path
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    
    # Get the current directory (where the app is installed)
    current_dir = os.path.abspath(os.path.dirname(__file__))
    
    # Create the shortcut file
    shortcut_path = os.path.join(desktop, "Fitness Leveling.lnk")
    
    # Create the VBScript to create the shortcut
    vbs_content = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{os.path.join(current_dir, 'launch_app.bat')}"
oLink.WorkingDirectory = "{current_dir}"
oLink.Description = "Fitness Leveling App"
oLink.Save
'''
    
    # Write the VBScript to a temporary file
    vbs_path = os.path.join(current_dir, "create_shortcut.vbs")
    with open(vbs_path, "w") as f:
        f.write(vbs_content)
    
    # Execute the VBScript
    os.system(f'cscript //nologo "{vbs_path}"')
    
    # Clean up the temporary VBScript file
    os.remove(vbs_path)
    
    print(f"Desktop shortcut created at: {shortcut_path}")
    print("\nYou can now launch the app by double-clicking the shortcut on your desktop!")

if __name__ == "__main__":
    create_desktop_shortcut() 