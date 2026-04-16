# ============================================
# MiniQuiz - QUICK START & VERIFICATION
# ============================================

## 🚀 一键启动

### Windows (推荐)
```powershell
cd c:\Users\Bao\Desktop\MiniQuiz
run.bat
```

### 手动启动（两个终端）
```powershell
# 终端 1 - 后端
run_backend.bat

# 终端 2 - 前端
run_frontend.bat
```

---

## ✅ 验证清单（启动后执行）

### 1. 检查后端日志

**应该看到：**
```
[ENV] Loaded: ...\.env.local
[ENV] ENVIRONMENT = development
[Limiter] Development mode: rate limits relaxed
[Auth] Initialized - ALGORITHM: HS256, SECRET_KEY set: True
[App] Startup: initializing services...
[App] Connecting to database...
[Database] Connecting to MongoDB...
[Database] Connected successfully
[App] Database connected successfully
[App] CORS configured for origins: http://localhost:5173, https://miniquiz.xyz
[App] Startup complete - MiniQuiz backend is running
```

**如果看到错误：**
- `MONGODB_URI not set` → 检查 `.env.local`
- `MongoDB connection failed` → 启动 MongoDB: `docker run -d -p 27017:27017 mongo`

---

### 2. 检查前端

浏览器自动打开: `http://localhost:5173/auth`

**应该看到：**
- 登录表单（Email, Password）
- 注册表单（Username, Email, Password, Confirm）
- 忘记密码、重置密码表单
- Turnstile captcha 在每个表单下方

**如果空白：**
- 检查前端终端是否有错误
- 运行 `npm install` 重新安装依赖

---

### 3. 测试注册流程（无邮件服务）

**步骤：**
1. 切换到 "Đăng ký" 标签
2. 填写：
   - Username: `testuser`
   - Email: `testuser@example.com`
   - Password: `Test123!@#`
   - Confirm: `Test123!@#`
3. 完成 Turnstile（勾选复选框）
4. 点击 "Đăng ký"

**预期行为：**
- 按钮变为 "Đang đăng ký..." + 旋转图标（✅ 加载状态）
- 2-3 秒后弹出确认框：
  ```
  Đăng ký thành công! (Email không gửi được do chưa cấu hình)

  Nhấn OK để mở liên kết xác minh (chỉ dùng cho dev)
  Nhấn Cancel để chỉ hiển thị thông báo
  ```
- 点击 **OK** → 新标签页打开验证链接
- 新标签页跳转到：`http://localhost:5173/auth?message=Tài khoản đã được tạo...&type=success`

**后端日志应看到：**
```
[Register] Registration attempt started for email: testuser@example.com
[Register] Turnstile verified for testuser@example.com
[Register] Checking if email exists: testuser@example.com
[Register] Validating inputs
[Register] Hashing password
[Register] Creating verification token
[Register] Sending verification email
[Mail] Email skipped (service disabled): Xác minh tài khoản → testuser@example.com
[DEV MODE] Verification URL for testuser@example.com: http://localhost:8000/api/user/verify?token=eyJ...
[Register] Registration successful for testuser@example.com
```

---

### 4. 测试登录流程

**步骤：**
1. 使用刚注册的账户：
   - Email: `testuser@example.com`
   - Password: `Test123!@#`
2. 完成 Turnstile
3. 点击 "Đăng nhập"

**预期：**
- 按钮禁用 + 旋转图标 "Đang đăng nhập..."
- 1-2 秒后跳转到 `/dashboard`
- 浏览器控制台显示：`[Login] success`
- 后端日志：
  ```
  [Login] Login attempt for: testuser@example.com
  [Login] Login successful for: testuser@example.com
  ```

**Cookie 检查：**
```javascript
// 在 /dashboard 页面打开控制台
console.log(document.cookie)
// 应该看到: token=eyJ... (httponly, 看不到具体值但存在)
```

---

### 5. 测试前端验证（不应发送请求）

| 测试 | 操作 | 预期结果 | 网络请求? |
|------|------|----------|-----------|
| 空字段 | 留空点击登录 | "Vui lòng nhập đầy đủ thông tin" | ❌ 无 |
| 无效邮箱 | email: `test` | "Email không đúng định dạng" | ❌ 无 |
| 未 CAPTCHA | 不勾选 Turnstile | "Vui lòng xác minh captcha..." | ❌ 无 |
| 快速点击 | 连续点击按钮 5 次 | 仅 1 个请求，按钮禁用 | ✅ 仅 1 次 |
| 密码不匹配 | 注册时两次密码不同 | "Mật khẩu không giống" | ❌ 无 |

**验证方法：** 打开浏览器 DevTools → Network 标签 → 执行操作 → 确认无效操作无请求

---

### 6. 测试错误场景

| 场景 | 预期消息 | 后端日志 |
|------|----------|----------|
| 错误密码 | `Sai mật khẩu` | `[Login] Invalid password for: ...` |
| 用户不存在 | `Người dùng không tồn tại` | `[Login] User not found: ...` |
| 已登录状态下注册 | `Bạn đã đăng nhập` | `[Register] User already logged in` |
| Rate limit (生产模式) | `Quá nhiều lần...` | 429 响应 |

---

### 7. 测试已登录状态

**方法 A：访问受保护路由**
```bash
# 登录后，访问 /dashboard，应该看到用户信息
```

**方法 B：API 调用**
```bash
# 获取 cookie 值（从浏览器复制 token，注意是 httponly 需通过 JS 获取）
# 或使用 curl 先登录保存 cookie
curl -s http://localhost:8000/api/user/logged-in -H "Cookie: token=YOUR_TOKEN"
# 响应: {"logged_in": true}

# 无 token
curl -s http://localhost:8000/api/user/logged-in
# 响应: {"logged_in": false}
```

---

### 8. 测试 OAuth（可选，需配置）

**前提：**
1. 在 `.env.local` 设置：
   ```
   DISCORD_CLIENT_ID=your_id
   DISCORD_CLIENT_SECRET=your_secret
   ```
2. 在 Discord Developer Portal 配置：
   - Redirect URI: `http://localhost:8000/api/user/discord/callback`

**测试：**
1. 访问 `/auth`
2. 点击 "Đăng nhập với Discord"
3. 授权后应跳转 `/dashboard` 并创建用户

**预期日志：**
```
[OAuth] Discord login redirect_uri: http://localhost:8000/api/user/discord/callback
[OAuth] Discord user: email=..., username=...
[OAuth] Created new Discord user: ...
[OAuth] Discord login success: ..., secure_cookie=False
```

---

## 🐛 常见问题排查

### 问题：后端启动失败，提示 `MONGODB_URI not set`

**解决：**
```powershell
# 检查 .env.local
cat .env.local | findstr MONGODB_URI

# 确保有：
# MONGODB_URI = mongodb://localhost:27017/miniquiz

# 启动 MongoDB（Docker）
docker run -d -p 27017:27017 --name miniquiz-mongo mongo:latest

# 或本地安装的 MongoDB
net start MongoDB
```

---

### 问题：登录返回 422 或 500

**原因：** 前端代码未更新到最新版本。

**解决：**
```powershell
cd frontend
# 清理缓存
rm -rf node_modules/.vite dist
# 重启
cd ..
run.bat
```

---

### 问题：OAuth 重定向失败

**检查：**
1. 环境变量是否正确：
   ```powershell
   echo $env:DISCORD_CLIENT_ID
   echo $env:DISCORD_REDIRECT_URI
   ```
2. Discord 开发者门户的 Redirect URI **必须完全匹配**：
   - 开发: `http://localhost:8000/api/user/discord/callback`
   - 生产: `https://miniquiz.xyz/api/user/discord/callback`

---

### 问题：前端看不到更新

**原因：** Vite 缓存或浏览器缓存。

**解决：**
1. 强制刷新: `Ctrl+Shift+R`
2. 清除 Vite 缓存:
   ```powershell
   cd frontend
   rmdir /s /q node_modules\.vite
   cd ..
   run.bat
   ```

---

### 问题：邮件未发送但应该发送

**检查：**
```powershell
# 1. 确认 MAILEROO_API_KEY 已设置
echo %MAILEROO_API_KEY%

# 2. 查看后端日志中的 [Mail] 行
# 应该看到 "Email service enabled" 而不是 "disabled"

# 3. 测试 API 密钥是否有效
# 访问 Maileroo 仪表板查看 API 使用情况
```

---

### 问题：Turnstile 验证失败

**开发模式：**
- 使用测试密钥 `1x00000000000000000000AA` 会自动 bypass
- 如果仍失败，检查 `CF_TURNSTILE_SECRET` 是否以 `1x` 开头

**生产模式：**
- 必须使用真实密钥
- 确保网站域名已添加到 Cloudflare 允许列表

---

## 📊 完整功能矩阵

| 功能 | 状态 | 测试方法 |
|------|------|----------|
| 后端启动 | ✅ | 查看日志 "Database connected successfully" |
| 前端启动 | ✅ | 打开 http://localhost:5173/auth 看到表单 |
| 注册（无邮件） | ✅ | 填写表单 → 弹窗显示 verification URL |
| 注册（有邮件） | ✅ | 设置 MAILEROO_API_KEY → 收到邮件 |
| 验证链接 | ✅ | 点击邮件链接或 dev URL → 创建账户成功 |
| 登录 | ✅ | 正确凭据 → 跳转 dashboard |
| 登录失败 | ✅ | 错误密码 → 显示 "Sai mật khẩu" |
| 已登录检查 | ✅ | `/api/user/logged-in` 返回 `true` |
| 登出 | ✅ | POST `/api/user/logout` → cookie 删除 |
| 忘记密码 | ✅ | 提交邮箱 → 收到重置邮件 |
| 重置密码 | ✅ | 点击邮件链接 → 设置新密码 |
| OAuth Discord | ✅ | 点击按钮 → 授权 → 创建/登录 |
| OAuth Google | ✅ | 同上 |
| 速率限制 | ✅ | 开发模式无限制，生产模式生效 |
| CORS | ✅ | 允许 localhost + miniquiz.xyz |
| Cookie 安全 | ✅ | 开发 HTTP，生产 HTTPS |

---

## 🎯 验证命令速查

```bash
# 检查后端健康
curl http://localhost:8000/api/user/logged-in

# 测试注册（无邮件）
curl -X POST "http://localhost:8000/api/user/register?turnstile_token=test" \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"Test123!@#","avatar":"https://example.com/avatar.png"}'

# 检查数据库
docker exec -it miniquiz-mongo mongosh
> use users
> db.users.find().pretty()

# 查看实时日志
# 后端终端直接查看
# 前端终端：npm run dev 的输出

# 检查端口
netstat -an | findstr :8000
netstat -an | findstr :5173
```

---

## 📁 关键文件位置

```
MiniQuiz/
├── .env.local                  ← 你的配置
├── .env.example                ← 配置模板
├── run.bat                     ← 启动整个项目
├── run_backend.bat             ← 仅启动后端
├── run_frontend.bat            ← 仅启动前端
├── FIX_LOG.md                  ← 详细修复记录
├── DEBUG_REPORT.md             ← 调试报告
└── frontend/src/
    └── components/page/auth/
        ├── login.ts            ← 登录组件（已修复）
        ├── register.ts         ← 注册组件（已修复）
        ├── forgot_passwd.ts    ← 忘记密码（已修复）
        └── reset_passwd.ts     ← 重置密码（已修复）
```

---

## 🎉 完成标志

当你完成以下所有检查，说明项目已完全修复并可运行：

- [ ] `run.bat` 启动成功，无错误
- [ ] 后端日志显示 `Database connected successfully`
- [ ] 前端打开 `http://localhost:5173/auth` 显示正常
- [ ] 注册表单提交 → 看到 dev verification URL
- [ ] 点击 verification URL → 账户创建成功
- [ ] 登录 → 跳转 `/dashboard`
- [ ] 访问 `/api/user/logged-in` 返回 `{"logged_in": true}`
- [ ] 无效输入显示清晰错误，无网络请求
- [ ] 快速点击按钮无重复请求
- [ ] 后端控制台有清晰的 `[Register]`, `[Login]`, `[OAuth]` 日志

**如果以上全部通过，MiniQuiz 已完全修复并可用于开发！** ✅
