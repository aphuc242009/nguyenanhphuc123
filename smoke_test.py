"""Quick smoke test: import backend and test email validation"""
import sys
import os

# Change to project dir
os.chdir(r"C:\Users\Bao\Desktop\MiniQuiz\MiniQuiz")

# Test 1: Backend import
print("=== Test 1: Backend import ===")
try:
    from backend.app import app
    print("[OK] Backend app imported successfully")
except Exception as e:
    print(f"[FAIL] Backend import failed: {e}")
    sys.exit(1)

# Test 2: Email validator
print("\n=== Test 2: Email validation ===")
from backend.utils.validators import is_valid_email

test_emails = [
    'taquangbao2006@gmail.com',
    'abc.xyz@gmail.com',
    'bao_2006@gmail.com',
    'test-user123@outlook.com',
    'hello.world@company.vn',
]

all_pass = True
for email in test_emails:
    result = is_valid_email(email)
    status = "PASS" if result else "FAIL"
    print(f"  [{status}] {email}")
    if not result:
        all_pass = False

if all_pass:
    print("\n[SUCCESS] All test emails PASSED")
else:
    print("\n[FAILURE] Some emails FAILED")
    sys.exit(1)

print("\n=== SMOKE TEST PASSED ===")
