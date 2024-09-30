import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    # List of packages to install
    required_packages = [
        "pytest"
    ]

    print("Installing required packages...")
    for package in required_packages:
        try:
            install(package)
            print(f"'{package}' installed successfully.")
        except Exception as e:
            print(f"Error installing '{package}': {e}")

    print("All packages installed successfully.")

if __name__ == "__main__":
    main()
