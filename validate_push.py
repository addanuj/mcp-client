import subprocess
import re
import os

repo = "/Users/anujshrivastava/code/mcp-client"

print("=" * 70)
print("🔒 PRE-PUSH SECURITY VALIDATION")
print("=" * 70)

# Check 1: Git status
print("\n1️⃣  CHECKING GIT STATUS")
print("-" * 70)

result = subprocess.run(
    ["git", "-C", repo, "status", "--short"],
    capture_output=True,
    text=True
)

if result.stdout.strip():
    print("Modified files:")
    print(result.stdout)
else:
    print("✅ Working tree clean")

# Check 2: Show all tracked files
print("\n2️⃣  ALL TRACKED FILES")
print("-" * 70)

result = subprocess.run(
    ["git", "-C", repo, "ls-files"],
    capture_output=True,
    text=True
)

tracked = result.stdout.strip().split('\n')
print(f"Total tracked files: {len(tracked)}")

# Check for forbidden patterns in tracked files
forbidden_found = []
for file in tracked:
    if any(x in file for x in ['.env', '.github', '.vscode', '__pycache__', 'node_modules', 'venv', '.venv']):
        forbidden_found.append(file)

if forbidden_found:
    print(f"❌ FORBIDDEN files in tracking:")
    for f in forbidden_found:
        print(f"   - {f}")
else:
    print("✅ No forbidden files tracked")

# Check 3: Verify .gitignore
print("\n3️⃣  VERIFYING .gitignore")
print("-" * 70)

with open(os.path.join(repo, ".gitignore"), 'r') as f:
    content = f.read()
    
required = ['.env', '__pycache__', 'node_modules', 'venv', '.vscode', 'dist', '.github']
missing = [p for p in required if p not in content]

if missing:
    print(f"❌ Missing in .gitignore: {missing}")
else:
    print("✅ .gitignore properly configured")

# Check 4: Search for common secrets patterns
print("\n4️⃣  SCANNING FOR SECRETS")
print("-" * 70)

result = subprocess.run(
    ["git", "-C", repo, "grep", "-i", "api.key\\|password\\|token\\|secret"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("⚠️  Potential secrets found (verify these are false positives):")
    print(result.stdout[:500])
else:
    print("✅ No obvious secrets in tracked files")

print("\n" + "=" * 70)
print("✅ VALIDATION COMPLETE")
print("=" * 70)
