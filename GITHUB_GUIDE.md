# GitHub 上传指南

## 步骤 1: 在 GitHub 上创建仓库

1. 访问 https://github.com/new
2. 填写仓库信息：
   - **Repository name**: `video-craft` (或你喜欢的名字)
   - **Description**: 电商视频智能创作平台 - AI Video/Image Generation Platform
   - **Visibility**: Public (或 Private)
   - **Initialize**: 不要勾选任何选项 (README, .gitignore, license)
3. 点击 **Create repository**

## 步骤 2: 推送本地代码到 GitHub

创建仓库后，GitHub 会显示类似下面的命令：

```bash
# 添加远程仓库 (替换 yourusername 为你的 GitHub 用户名)
git remote add origin https://github.com/yourusername/video-craft.git

# 推送代码
git branch -M main
git push -u origin main
```

## 步骤 3: 验证上传

1. 刷新 GitHub 页面
2. 确认所有文件都已上传
3. 检查 README.md 是否正确显示

## 可选: 添加截图

为了让 README 更美观，建议添加截图：

1. 在项目中创建 `screenshots/` 目录
2. 添加截图文件：
   - `dashboard.png` - 仪表盘页面
   - `video-gen.png` - 视频生成页面
   - `history.png` - 历史记录页面
3. 提交并推送：

```bash
git add screenshots/
git commit -m "Add screenshots"
git push
```

## 可选: 添加 Topics

在 GitHub 仓库页面，点击右侧的 **⚙️ Manage topics**，添加以下标签：

- `vue3`
- `fastapi`
- `ai`
- `video-generation`
- `image-generation`
- `doubao`
- `volcengine`
- `ecommerce`

## 可选: 启用 GitHub Pages (前端演示)

如果你想展示前端演示：

1. 进入仓库 **Settings** → **Pages**
2. Source 选择 **Deploy from a branch**
3. Branch 选择 **main** 和 **/ (root)** 或 **/docs**
4. 点击 **Save**

## 本地备份命令

如果你只是想本地备份，可以创建裸仓库：

```bash
# 创建本地裸仓库作为备份
git clone --bare video-craft video-craft-backup.git

# 或者打包整个项目
tar -czvf video-craft-backup-$(date +%Y%m%d).tar.gz video-craft/
```

## 当前 Git 状态

项目已初始化 Git 仓库，位于：
```
C:\Users\EDY\.stepclaw\workspace\video-craft\.git
```

提交记录：
- 初始提交: `d627e68` - "Initial commit: VideoCraft - AI Video/Image Generation Platform"
- 61 个文件已提交

## 需要帮助？

如果在推送过程中遇到问题：

1. **认证问题**: 使用 GitHub Personal Access Token 代替密码
2. **LF/CRLF 警告**: 已配置 Git 自动处理换行符
3. **大文件问题**: 确保没有提交 node_modules 或上传的视频文件

---

执行完上述步骤后，你的项目就安全备份到 GitHub 了！
