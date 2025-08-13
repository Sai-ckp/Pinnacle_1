import os
import glob

for root, dirs, files in os.walk('.'):
    if 'migrations' in dirs:
        mig_dir = os.path.join(root, 'migrations')
        print(f"Cleaning: {mig_dir}")
        for file in glob.glob(os.path.join(mig_dir, '*.py')):
            if not file.endswith('__init__.py'):
                print(f"Deleting: {file}")
                os.remove(file)
        for file in glob.glob(os.path.join(mig_dir, '*.pyc')):
            print(f"Deleting: {file}")
            os.remove(file)

