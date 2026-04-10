# 贡献指南

感谢您对 VideoCraft 的关注！我们欢迎各种形式的贡献。

## 如何贡献

### 1. 报告问题

如果您发现了 bug 或有功能建议，请通过 GitHub Issues 提交：

1. 检查是否已有相关 issue
2. 创建新 issue，详细描述问题
3. 提供复现步骤（如果是 bug）

### 2. 提交代码

#### 开发环境搭建

```bash
# 1. Fork 项目
# 2. 克隆您的 fork
git clone https://github.com/YOUR_USERNAME/video-craft.git
cd video-craft

# 3. 创建分支
git checkout -b feature/your-feature-name

# 4. 安装依赖并启动
cd frontend && npm install
cd ../backend && pip install -r requirements.txt

# 5. 启动开发服务器
./scripts/dev-start.sh
```

#### 代码规范

**前端 (Vue)**:
- 使用 Composition API
- 组件名使用 PascalCase
- 变量名使用 camelCase
- 常量名使用 UPPER_SNAKE_CASE

**后端 (Python)**:
- 遵循 PEP 8 规范
- 使用类型注解
- 函数和类添加 docstring

#### 提交规范

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型 (type)**:
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建过程或辅助工具的变动

**示例**:
```
feat(image): 添加批量生成功能

支持一次生成多张图片，提高生产效率

Closes #123
```

### 3. 提交 Pull Request

1. 确保代码通过测试
2. 更新相关文档
3. 提交 PR 到 main 分支
4. 描述清楚改动内容

## 开发流程

```
Fork → Clone → Branch → Develop → Test → Commit → Push → PR
```

## 代码审查

所有提交都需要经过代码审查：
- 至少 1 个 approve 才能合并
- 解决所有 review 意见
- 保持 CI 通过

## 联系我们

- GitHub Issues: [提交问题](https://github.com/yourusername/video-craft/issues)
- Email: support@videocraft.app

## 许可证

通过贡献代码，您同意您的贡献将在 MIT 许可证下发布。
