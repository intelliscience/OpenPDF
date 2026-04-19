import os
import sys
import subprocess
import shutil
import platform
import datetime
import importlib.util
import argparse

class OpenPDFBuilder:
    def __init__(self, verbose=False):
        self.project_name = "OpenPDF Professional 2026"
        self.script_target = "openpdf.py"
        self.binary_name = f"openpdf-linux-{platform.machine()}"
        self.dist_path = os.path.join(os.getcwd(), "dist")
        self.build_path = os.path.join(os.getcwd(), "build")
        self.verbose = verbose
        self.dependencies = ["pypdf", "pyinstaller"]
        self.use_break_flag = "--break-system-packages"

    def _print_banner(self):
        print("=" * 70)
        print(f"{self.project_name} - Build System")
        print(f"Log Level: {'VERBOSE' if self.verbose else 'STANDARD'}")
        print(f"Deployment Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

    def _is_installed(self, package_name):
        if package_name == "pyinstaller":
            return shutil.which("pyinstaller") is not None
        try:
            return importlib.util.find_spec(package_name) is not None
        except (ImportError, ValueError):
            return False

    def _check_environment(self):
        print(f"[*] Hostname: {platform.node()}")
        print(f"[*] Platform: {platform.system()} {platform.machine()}")
        print(f"[*] Python:   {sys.version.split()[0]}")
        if not os.path.exists(self.script_target):
            print(f"[ERROR] Source file '{self.script_target}' not found.")
            sys.exit(1)

    def _handle_dependencies(self):
        print("[*] Verifying build-time dependencies...")
        for pkg in self.dependencies:
            status = "[FOUND]" if self._is_installed(pkg) else "[MISSING]"
            print(f"    - {pkg:15}: {status}")
            if status == "[MISSING]":
                print(f"    - Installing {pkg}...")
                try:
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", pkg, self.use_break_flag],
                        stdout=None if self.verbose else subprocess.DEVNULL,
                        stderr=None if self.verbose else subprocess.STDOUT
                    )
                except subprocess.CalledProcessError:
                    print(f"[FATAL] Dependency installation failed for {pkg}")
                    sys.exit(1)

    def _cleanup(self):
        print("[*] Preparing workspace for compilation...")
        targets = [self.dist_path, self.build_path, f"{self.binary_name}.spec"]
        for target in targets:
            try:
                if os.path.isdir(target):
                    shutil.rmtree(target)
                elif os.path.isfile(target):
                    os.remove(target)
            except Exception:
                pass

    def _compile(self):
        print(f"[*] Compiling stand-alone binary: {self.binary_name}")
        cmd = [
            "pyinstaller",
            "--onefile",
            "--clean",
            "--name", self.binary_name,
            self.script_target
        ]
        try:
            if self.verbose:
                result = subprocess.run(cmd, capture_output=False, text=True)
            else:
                result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"\n[ERROR] Compilation failed (Exit Code {result.returncode})")
                if not self.verbose:
                    print("-" * 30 + " RAW ERROR LOG " + "-" * 30)
                    print(result.stdout)
                    print(result.stderr)
                    print("-" * 75)
                sys.exit(1)
            print("[SUCCESS] Compilation phase finished.")
        except FileNotFoundError:
            print("[FATAL] PyInstaller not found in system PATH.")
            sys.exit(1)
        except Exception as e:
            print(f"[FATAL] Unexpected error: {e}")
            sys.exit(1)

    def _finalize(self):
        origin = os.path.join(self.dist_path, self.binary_name)
        destination = os.path.join(os.getcwd(), self.binary_name)
        if os.path.exists(origin):
            if os.path.exists(destination):
                os.remove(destination)
            shutil.move(origin, destination)
            os.chmod(destination, 0o755)
            f_size = os.path.getsize(destination) / (1024 * 1024)
            print("=" * 70)
            print(f"Final Path:  {destination}")
            print(f"Build Size:  {f_size:.2f} MB")
            print("=" * 70)
            print("PROCESS COMPLETE")
        else:
            print("[ERROR] Binary not found.")
            sys.exit(1)

    def run(self):
        try:
            self._print_banner()
            self._check_environment()
            self._handle_dependencies()
            self._cleanup()
            self._compile()
            self._finalize()
        except KeyboardInterrupt:
            print("\n[!] User aborted.")
            sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="OpenPDF 2026 Build Script")
    parser.add_argument("--verbose", action="store_true")
    args, unknown = parser.parse_known_args()
    builder = OpenPDFBuilder(verbose=args.verbose)
    builder.run()

if __name__ == "__main__":
    main()