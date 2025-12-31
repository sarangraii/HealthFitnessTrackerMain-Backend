import os

# Create directory structure
directories = [
    'app',
    'app/models',
    'app/routers',
    'app/services',
    'app/utils'
]

print("Creating directory structure...")
for directory in directories:
    os.makedirs(directory, exist_ok=True)
    init_file = os.path.join(directory, '__init__.py')
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write('# This file makes the directory a Python package\n')
        print(f"✅ Created {init_file}")
    else:
        print(f"✓ {init_file} already exists")

print("\n✅ Directory structure created successfully!")
print("\nNext steps:")
print("1. Make sure MongoDB is running")
print("2. Install dependencies: pip install -r requirements.txt")
print("3. Run: uvicorn app.main:app --reload --port 8000")