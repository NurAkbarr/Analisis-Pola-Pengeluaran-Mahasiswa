#!/usr/bin/env python3
"""
Script untuk menjalankan semua proses analisis pola pengeluaran mahasiswa
"""

import os
import subprocess
import sys

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print(f"\n{'='*50}")
    print(f"🚀 {description}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print(f"Warnings: {result.stderr}")
        print(f"✅ {description} berhasil!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error saat menjalankan {script_name}:")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"❌ File {script_name} tidak ditemukan!")
        return False

def check_requirements():
    """Check if all required packages are installed"""
    print("🔍 Checking requirements...")

    required_packages = {
        'pandas': 'pandas',
        'numpy': 'numpy',
        'scikit-learn': 'sklearn',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'plotly': 'plotly',
        'streamlit': 'streamlit',
        'joblib': 'joblib'
    }

    missing_packages = []

    for pip_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(pip_name)

    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Please run: pip install " + " ".join(missing_packages))
        return False

    print("✅ All required packages are installed!")
    return True

def create_file_structure():
    """Create necessary directories and files"""
    print("📁 Creating file structure...")
    
    # Create directories if they don't exist
    directories = ['data', 'models', 'outputs']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"  Created directory: {directory}")
    
    return True

def main():
    """Main execution function"""
    print("🎯 ANALISIS POLA PENGELUARAN MAHASISWA")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        return False
    
    # Create file structure
    create_file_structure()
    
    # List of scripts to run in order
    scripts = [
        ("generate_data.py", "Generating synthetic dataset"),
        ("explore_data.py", "Exploring and visualizing data"),
        ("kmeans_analysis.py", "Running K-Means clustering analysis"),
        ("recommendations.py", "Testing recommendation system")
    ]
    
    # Run each script
    all_success = True
    for script, description in scripts:
        success = run_script(script, description)
        if not success:
            all_success = False
            print(f"⚠️ Continuing despite error in {script}...")
    
    print(f"\n{'='*60}")
    if all_success:
        print("🎉 SEMUA PROSES BERHASIL!")
        print("✅ Dataset telah dibuat")
        print("✅ Model telah dilatih")
        print("✅ Sistem rekomendasi siap digunakan")
        print("\n🚀 Untuk menjalankan aplikasi web:")
        print("   streamlit run app.py")
    else:
        print("⚠️ BEBERAPA PROSES GAGAL")
        print("Silakan periksa error di atas dan perbaiki sebelum melanjutkan")
    
    print(f"{'='*60}")
    
    return all_success

if __name__ == "__main__":
    success = main()
    if success:
        # Ask user if they want to run the Streamlit app
        while True:
            choice = input("\n🤔 Apakah Anda ingin menjalankan aplikasi web sekarang? (y/n): ").lower().strip()
            if choice in ['y', 'yes', 'ya']:
                print("\n🚀 Menjalankan aplikasi Streamlit...")
                try:
                    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
                except KeyboardInterrupt:
                    print("\n👋 Aplikasi dihentikan oleh user")
                except Exception as e:
                    print(f"\n❌ Error menjalankan Streamlit: {e}")
                break
            elif choice in ['n', 'no', 'tidak']:
                print("\n💡 Untuk menjalankan aplikasi nanti, gunakan command:")
                print("   streamlit run app.py")
                break
            else:
                print("   Silakan jawab 'y' atau 'n'")
    else:
        sys.exit(1)