#!/usr/bin/env python
"""
MiniQuiz Integrity Verification Script
Checks all critical fixes are applied correctly.
"""

import os
import sys
import re

PROJECT_ROOT = r"c:\Users\Bao\Desktop\MiniQuiz\MiniQuiz"
backend_dir = os.path.join(PROJECT_ROOT, "backend")

# UTF-8 output for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 70)
print("MiniQuiz - Integrity Verification Report")
print("=" * 70)

all_ok = True

# 1. Python syntax check
print("\n[1] Python Syntax Check")
print("-" * 70)
python_files = [
    "app.py",
    "routers/users.py",
    "utils/auth.py",
    "utils/database.py",
    "utils/mail.py",
    "utils/limiter.py",
    "utils/models.py",
]
for f in python_files:
    fpath = os.path.join(backend_dir, f)
    try:
        with open(fpath, 'r', encoding='utf-8') as fh:
            compile(fh.read(), fpath, 'exec')
        print(f"  [OK] {f}")
    except SyntaxError as e:
        print(f"  [FAIL] {f}: {e}")
        all_ok = False

# 2. Critical code fixes verification
print("\n[2] Critical Code Fixes")
print("-" * 70)

# auth.py checks
auth_path = os.path.join(backend_dir, "utils/auth.py")
with open(auth_path, 'r', encoding='utf-8') as f:
    auth_content = f.read()

if 'os.environ.get("ALGORITHM", "HS256")' in auth_content:
    print("  [OK] auth.py: ALGORITHM default set to 'HS256'")
else:
    print("  [FAIL] auth.py: ALGORITHM default missing")
    all_ok = False

if 'jwt.ExpiredSignatureError' in auth_content:
    print("  [OK] auth.py: JWT exception handling enhanced")
else:
    print("  [FAIL] auth.py: JWT exception handling insufficient")
    all_ok = False

# database.py checks
db_path = os.path.join(backend_dir, "utils/database.py")
with open(db_path, 'r', encoding='utf-8') as f:
    db_content = f.read()

if 'ObjectId(user_id)' in db_content:
    print("  [OK] database.py: ObjectId conversion added to get_user")
else:
    print("  [FAIL] database.py: ObjectId conversion missing in get_user")
    all_ok = False

if 'ObjectId(quiz_id)' in db_content:
    print("  [OK] database.py: ObjectId conversion added to get_quiz")
else:
    print("  [FAIL] database.py: ObjectId conversion missing in get_quiz")
    all_ok = False

if 'await self.client.aclose()' in db_content:
    print("  [OK] database.py: Async aclose() used")
else:
    print("  [FAIL] database.py: sync close() still present")
    all_ok = False

if 'async def disconnect' in db_content:
    print("  [OK] database.py: disconnect() method added")
else:
    print("  [FAIL] database.py: disconnect() method missing")
    all_ok = False

# users.py checks
users_path = os.path.join(backend_dir, "routers/users.py")
with open(users_path, 'r', encoding='utf-8') as f:
    users_content = f.read()

# users.py checks
users_path = os.path.join(backend_dir, "routers/users.py")
with open(users_path, 'r', encoding='utf-8') as f:
    users_content = f.read()

# Check all create_user calls use keyword args
create_user_calls = re.findall(r'db\.create_user\([^)]+\)', users_content)
if create_user_calls:
    keyword_ok = all('username=' in call and 'email=' in call and 'password=' in call for call in create_user_calls)
    if keyword_ok:
        print(f"  [OK] users.py: All {len(create_user_calls)} create_user calls use keyword args")
    else:
        print(f"  [FAIL] users.py: Some create_user calls use positional args")
        all_ok = False

# AUTH FIXES - Email normalization and verification
print("\n[2a] Auth Flow Fixes (Email Normalization & Verification)")
print("-" * 70)

# Check login endpoint normalizes email
if 'normalized_email = normalize_email(user.email)' in users_content and 'db.get_user_by_email(normalized_email)' in users_content:
    print("  [OK] users.py: Login normalizes email before query")
else:
    print("  [FAIL] users.py: Login does not normalize email")
    all_ok = False

# Check login checks email_verified
if 'if not user_db.get("email_verified", False):' in users_content and 'Tài khoản chưa xác minh email' in users_content:
    print("  [OK] users.py: Login checks email_verified status")
else:
    print("  [FAIL] users.py: Login missing email_verified check")
    all_ok = False

# Check login creates token with normalized email
if 'auth_manager.create_access_token({"type": "token", "sub": normalized_email})' in users_content:
    print("  [OK] users.py: Login token uses normalized email")
else:
    print("  [FAIL] users.py: Login token may use non-normalized email")
    all_ok = False

# Check register normalizes email before create_user
if 'normalized_email = normalize_email(user.email)' in users_content and users_content.count('await db.create_user') >= 2:
    # Check that the first create_user (in register) uses normalized_email
    register_section = users_content[users_content.find('@router.post("/register")'):users_content.find('@router.get("/verify")')]
    if 'normalized_email = normalize_email' in register_section and 'email=normalized_email' in register_section:
        print("  [OK] users.py: Register normalizes email and uses it in create_user")
    else:
        print("  [FAIL] users.py: Register does not properly normalize email")
        all_ok = False
else:
    print("  [FAIL] users.py: Register flow missing email normalization")
    all_ok = False

# Check register creates user with email_verified=False
register_section = users_content[users_content.find('@router.post("/register")'):users_content.find('@router.get("/verify")')]
if 'email_verified=False' in register_section or 'email_verified: False' in register_section:
    print("  [OK] users.py: Register creates user with email_verified=False")
else:
    print("  [FAIL] users.py: Register does not set email_verified=False")
    all_ok = False

# Check verify endpoint sets email_verified=True
verify_section = users_content[users_content.find('@router.get("/verify")'):users_content.find('@router.post("/login")')]
if 'email_verified=True' in verify_section:
    print("  [OK] users.py: Verify sets email_verified=True")
else:
    print("  [FAIL] users.py: Verify does not set email_verified=True")
    all_ok = False

# Check verify handles existing pending user
if 'existing_user = await db.get_user_by_email(normalized_email)' in verify_section and 'update_user' in verify_section:
    print("  [OK] users.py: Verify handles existing pending user")
else:
    print("  [FAIL] users.py: Verify does not handle existing pending user")
    all_ok = False

# Check forgot-password normalizes email
forgot_section = users_content[users_content.find('@router.post("/forgot-password")'):users_content.find('@router.post("/reset-password")')]
if 'normalized_email = normalize_email(email)' in forgot_section:
    print("  [OK] users.py: Forgot-password normalizes email")
else:
    print("  [FAIL] users.py: Forgot-password does not normalize email")
    all_ok = False

# redirect_uri validation (checks for OAuth env validation)
if 'if not client_id or not client_secret or not redirect_uri:' in users_content:
    print("  [OK] users.py: OAuth redirect_uri validation added")
else:
    print("  [FAIL] users.py: OAuth redirect_uri validation missing")
    all_ok = False

# secure flag dynamic
if 'secure=not IS_DEV' in users_content:
    print("  [OK] users.py: Cookie secure flag dynamic (dev=False, prod=True)")
else:
    print("  [FAIL] users.py: Cookie secure flag not dynamic")
    all_ok = False

# forgot-password URL dynamic
if 'FRONTEND_BASE' in users_content:
    print("  [OK] users.py: Forgot-password URL dynamic based on ENVIRONMENT")
else:
    print("  [FAIL] users.py: Forgot-password URL hardcoded")
    all_ok = False

# app.py checks
app_path = os.path.join(backend_dir, "app.py")
with open(app_path, 'r', encoding='utf-8') as f:
    app_content = f.read()

if '"https://miniquiz.xyz"' in app_content or "'https://miniquiz.xyz'" in app_content:
    print("  [OK] app.py: CORS includes production domain")
else:
    print("  [FAIL] app.py: CORS missing production domain")
    all_ok = False

# Middleware order
cors_pos = app_content.find('CORSMiddleware')
session_pos = app_content.find('SessionMiddleware')
slowapi_pos = app_content.find('SlowAPIMiddleware')
if cors_pos > 0 and session_pos > cors_pos and slowapi_pos > session_pos:
    print("  [OK] app.py: Middleware order correct (CORS -> Session -> SlowAPI)")
else:
    print("  [FAIL] app.py: Middleware order incorrect")
    all_ok = False

# 3. Environment configuration
print("\n[3] Environment Configuration")
print("-" * 70)
env_path = os.path.join(PROJECT_ROOT, ".env.local")
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        env_content = f.read()

    # Check API key removed
    if '8853c3a28c6ff3450f0b88c31cae030218a043bc4b4b99596502d48e01cdef41' not in env_content:
        print("  [OK] .env.local: Hardcoded API key removed")
    else:
        print("  [FAIL] .env.local: Hardcoded API key still present")
        all_ok = False

    # Check required vars
    if 'ENVIRONMENT' in env_content:
        print("  [OK] .env.local: ENVIRONMENT defined")
    else:
        print("  [WARN] .env.local: ENVIRONMENT not set")

    if 'MONGODB_URI' in env_content:
        print("  [OK] .env.local: MONGODB_URI defined")
    else:
        print("  [FAIL] .env.local: MONGODB_URI missing")
        all_ok = False

    if 'SECRET_KEY' in env_content:
        print("  [OK] .env.local: SECRET_KEY defined")
    else:
        print("  [FAIL] .env.local: SECRET_KEY missing")
        all_ok = False
else:
    print("  [FAIL] .env.local not found")
    all_ok = False

# .env.example check
env_example = os.path.join(PROJECT_ROOT, ".env.example")
if os.path.exists(env_example):
    with open(env_example, 'r', encoding='utf-8') as f:
        example_content = f.read()
    required = ['ENVIRONMENT', 'MONGODB_URI', 'SECRET_KEY', 'ALGORITHM', 'CF_TURNSTILE_SECRET', 'MAILEROO_API_KEY']
    missing = [v for v in required if f'{v} =' not in example_content]
    if not missing:
        print("  [OK] .env.example: Contains all required variables")
    else:
        print(f"  [WARN] .env.example: Missing: {missing}")
else:
    print("  [WARN] .env.example not found")

# 4. Frontend TypeScript fixes
print("\n[4] Frontend TypeScript Checks")
print("-" * 70)
frontend_src = os.path.join(PROJECT_ROOT, "frontend", "src")

# login.ts
login_path = os.path.join(frontend_src, "components/page/auth/login.ts")
if os.path.exists(login_path):
    with open(login_path, 'r', encoding='utf-8') as f:
        login_content = f.read()
    if 'isSubmitting' in login_content and '?disabled=${this.isSubmitting}' in login_content:
        print("  [OK] login.ts: isSubmitting state + loading UI")
    else:
        print("  [FAIL] login.ts: Missing isSubmitting")
        all_ok = False
    if 'isValidEmail' in login_content:
        print("  [OK] login.ts: Email validation present")
    else:
        print("  [FAIL] login.ts: Email validation missing")
        all_ok = False
else:
    print("  [FAIL] login.ts not found")
    all_ok = False

# register.ts
register_path = os.path.join(frontend_src, "components/page/auth/register.ts")
if os.path.exists(register_path):
    with open(register_path, 'r', encoding='utf-8') as f:
        reg_content = f.read()
    if 'isSubmitting' in reg_content:
        print("  [OK] register.ts: isSubmitting state present")
    else:
        print("  [FAIL] register.ts: isSubmitting missing")
        all_ok = False
else:
    print("  [FAIL] register.ts not found")
    all_ok = False

# forgot_passwd.ts
forgot_path = os.path.join(frontend_src, "components/page/auth/forgot_passwd.ts")
if os.path.exists(forgot_path):
    with open(forgot_path, 'r', encoding='utf-8') as f:
        forgot_content = f.read()
    if '@state() private isSubmitting' in forgot_content:
        print("  [OK] forgot_passwd.ts: isSubmitting state added")
    else:
        print("  [FAIL] forgot_passwd.ts: isSubmitting missing")
        all_ok = False
else:
    print("  [FAIL] forgot_passwd.ts not found")
    all_ok = False

# reset_passwd.ts
reset_path = os.path.join(frontend_src, "components/page/auth/reset_passwd.ts")
if os.path.exists(reset_path):
    with open(reset_path, 'r', encoding='utf-8') as f:
        reset_content = f.read()
    if '@state() private isSubmitting' in reset_content:
        print("  [OK] reset_passwd.ts: isSubmitting state added")
    else:
        print("  [FAIL] reset_passwd.ts: isSubmitting missing")
        all_ok = False
else:
    print("  [FAIL] reset_passwd.ts not found")
    all_ok = False

# input.ts (get_value return type)
input_path = os.path.join(frontend_src, "components/page/auth/input.ts")
if os.path.exists(input_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        input_content = f.read()
    if 'get_value(): string | undefined' in input_content:
        print("  [OK] input.ts: get_value() return type annotated")
    else:
        print("  [FAIL] input.ts: get_value() missing return type")
        all_ok = False
else:
    print("  [FAIL] input.ts not found")
    all_ok = False

# 5. Startup scripts
print("\n[5] Startup Scripts")
print("-" * 70)
run_bat = os.path.join(PROJECT_ROOT, "run.bat")
if os.path.exists(run_bat):
    with open(run_bat, 'r', encoding='utf-8') as f:
        run_content = f.read()
    if 'setlocal' in run_content and 'EnableDelayedExpansion' in run_content:
        print("  [OK] run.bat: Uses setlocal with delayed expansion")
    else:
        print("  [WARN] run.bat: May lack proper batch setup")
    if 'if /I ' in run_content or 'if defined ' in run_content:
        print("  [OK] run.bat: Uses safe comparison patterns")
    else:
        print("  [WARN] run.bat: May use unsafe comparisons")
else:
    print("  [FAIL] run.bat not found")
    all_ok = False

# Final result
print("\n" + "=" * 70)
if all_ok:
    print("RESULT: ALL CHECKS PASSED")
    print("\nThe project is ready to run:")
    print("  1. Start MongoDB: docker run -d -p 27017:27017 mongo")
    print("  2. Verify .env.local has MONGODB_URI set")
    print("  3. Run: run.bat")
    print("  4. Open: http://localhost:5173/auth")
else:
    print("RESULT: SOME CHECKS FAILED")
    print("Review the failures above and fix them.")
print("=" * 70)
