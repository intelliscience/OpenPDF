import PyInstaller.__main__
import platform
import os
import sys

def run_build():
    sys_platform = platform.system().lower()
    machine = platform.machine().lower()

    build_args = [
        'openpdf.py',
        '--onefile',
        '--clean',
    ]

    if sys_platform == 'darwin':
        print("--- Building Universal2 Binary for macOS ---")
        build_args.extend([
            '--name=openpdf-macos-universal',
            '--target-arch=universal2' 
        ])
    
    elif sys_platform == 'windows':
        arch = "x64" if "64" in machine else "x86"
        print(f"--- Building Windows {arch} Binary ---")
        build_args.append(f'--name=openpdf-windows-{arch}')
        
    else:
        arch = "arm64" if "arm" in machine or "aarch" in machine else "x86_64"
        print(f"--- Building Linux {arch} Binary ---")
        build_args.append(f'--name=openpdf-linux-{arch}')

    PyInstaller.__main__.run(build_args)

if __name__ == "__main__":
    run_build()