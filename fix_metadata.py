#!/usr/bin/env python3
import zipfile
import tempfile
import shutil
import os

def fix_wheel_metadata(wheel_path):
    """Fix the metadata version in a wheel file to be compatible with twine."""
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract the wheel
        with zipfile.ZipFile(wheel_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find the metadata file
        metadata_file = None
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file == 'METADATA':
                    metadata_file = os.path.join(root, file)
                    break
            if metadata_file:
                break
        
        if not metadata_file:
            print(f"Could not find METADATA file in {wheel_path}")
            return False
        
        # Read and fix the metadata
        with open(metadata_file, 'r') as f:
            content = f.read()
        
        # Replace Metadata-Version: 2.4 with Metadata-Version: 2.2
        content = content.replace('Metadata-Version: 2.4', 'Metadata-Version: 2.2')
        
        # Write back the fixed metadata
        with open(metadata_file, 'w') as f:
            f.write(content)
        
        # Create a new wheel with the fixed metadata
        new_wheel_path = wheel_path.replace('.whl', '_fixed.whl')
        
        with zipfile.ZipFile(new_wheel_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zip_ref.write(file_path, arcname)
        
        # Replace the original wheel
        shutil.move(new_wheel_path, wheel_path)
        print(f"Fixed metadata in {wheel_path}")
        return True

if __name__ == "__main__":
    wheel_file = "dist/pbesa-4.0.48-py3-none-any.whl"
    if os.path.exists(wheel_file):
        fix_wheel_metadata(wheel_file)
    else:
        print(f"Wheel file {wheel_file} not found") 