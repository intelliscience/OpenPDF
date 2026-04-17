import PyInstaller.__main__
import platform
import os
import sys
import shutil

def run_build():
    sys_platform = platform.system().lower()
    machine = platform.machine().lower()

    if sys_platform == 'darwin':
        binary_name = 'openpdf-macos-universal'
        target_arch = 'universal2'
    elif sys_platform == 'windows':
        arch = "x64" if "64" in machine else "x86"
        binary_name = f'openpdf-windows-{arch}'
        target_arch = None
    else:
        arch = "arm64" if "arm" in machine or "aarch" in machine else "x86_64"
        binary_name = f'openpdf-linux-{arch}'
        target_arch = None

    build_args = [
        'openpdf.py',
        '--onefile',
        '--clean',
        f'--name={binary_name}'
    ]

    if target_arch:
        build_args.append(f'--target-arch={target_arch}')

    print(f"--- Starting build for {binary_name} ---")
    PyInstaller.__main__.run(build_args)

    # File handling
    extension = ".exe" if sys_platform == "windows" else ""
    source_path = os.path.join('dist', f"{binary_name}{extension}")
    destination_path = f"./{binary_name}{extension}"

    print("--- Finalizing files ---")
    
    # 1. Move binary to root
    if os.path.exists(source_path):
        if os.path.exists(destination_path):
            os.remove(destination_path)
        shutil.move(source_path, destination_path)
        print(f"Moved binary to root: {destination_path}")

    # 2. Cleanup all build artifacts
    folders_to_delete = ['build', 'dist']
    for folder in folders_to_delete:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"Deleted folder: {folder}")

    spec_file = f"{binary_name}.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"Deleted spec file: {spec_file}")

    print(f"\n[SUCCESS] Build complete. {binary_name}{extension} is in the project root.")

if __name__ == "__main__":
    run_build()