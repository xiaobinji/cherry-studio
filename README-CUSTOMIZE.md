# Cherry Studio 自动化定制和打包脚本

这个脚本可以自动化完成 Cherry Studio 的定制修改和打包流程。

## 功能特性

- 自动隐藏"数据设置"模块
- 应用 BailianStrategy baseURL 自定义功能
- 修改打包配置（appId、productName 等）
- 自动构建和打包 Mac/Windows 安装包
- 支持重复执行（幂等性）
- 自动备份和回滚机制
- 详细的日志记录

## 环境要求

- Python 3.7 或更高版本
- pnpm（用于构建和打包）
- PyYAML 库：`pip install pyyaml`

## 快速开始

### 1. 初次设置

克隆或拉取最新代码：

```bash
git clone https://github.com/kangfenmao/cherry-studio.git
cd cherry-studio
```

### 2. 安装 Python 依赖

```bash
pip install pyyaml
```

### 3. 配置定制参数

编辑 `customize-config.json` 文件：

```json
{
  "appId": "com.yourcompany.YourAppName",
  "productName": "Your App Name",
  "packageName": "YourAppName",
  "version": "1.0.0",
  "hideDataSettings": true,
  "applyBailianFix": true,
  "buildPlatforms": ["mac", "windows"],
  "autoBuild": true,
  "skipBuildCheck": false,
  "skipInstall": false
}
```

**配置说明**：

- `appId`: 应用 ID（格式：com.company.appname）
- `productName`: 产品显示名称
- `packageName`: 包名（用于 package.json）
- `version`: 版本号
- `hideDataSettings`: 是否隐藏数据设置模块
- `applyBailianFix`: 是否应用 Bailian baseURL 修改
- `buildPlatforms`: 打包平台，可选值：["mac", "windows"]
- `autoBuild`: 是否自动执行构建和打包
- `skipBuildCheck`: 是否跳过 build:check（不推荐）
- `skipInstall`: 是否跳过 pnpm install（如果依赖已安装可跳过）

### 4. 运行脚本

```bash
python3 customize-and-build.py
```

脚本会自动完成所有修改和打包流程。

### 5. 获取安装包

打包完成后，安装包位于 `dist/` 目录：

- macOS: `dist/Cherry Studio-{version}.dmg`
- Windows: `dist/Cherry Studio Setup {version}.exe`

## 日常更新流程

每次需要更新时：

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 运行脚本（自动应用所有修改并打包）
python3 customize-and-build.py

# 3. 安装包位于 dist/ 目录
```

## 命令行选项

```bash
python3 customize-and-build.py [options]

Options:
  --config FILE    指定配置文件路径（默认：customize-config.json）
  --dry-run       只显示将要执行的操作，不实际修改
  --restore       从备份恢复所有文件
  --help          显示帮助信息
```

### 示例

**预览修改（不实际执行）**：

```bash
python3 customize-and-build.py --dry-run
```

**使用自定义配置文件**：

```bash
python3 customize-and-build.py --config my-config.json
```

**恢复原始文件**：

```bash
python3 customize-and-build.py --restore
```

## 文件修改说明

脚本会自动修改以下文件：

### 1. SettingsPage.tsx

**文件路径**: `src/renderer/src/pages/settings/SettingsPage.tsx`

**修改内容**：
- 移除 DataSettings 导入
- 移除 HardDrive 图标导入
- 移除数据设置菜单项
- 移除数据设置路由

### 2. BailianStrategy.ts

**文件路径**: `src/main/knowledge/reranker/strategies/BailianStrategy.ts`

**修改内容**：
- 为 `buildUrl` 方法添加可选的 `baseURL` 参数
- 支持自定义 baseURL 或使用默认的阿里云地址

### 3. electron-builder.yml

**文件路径**: `electron-builder.yml`

**修改内容**：
- 更新 `appId`
- 更新 `productName`

### 4. package.json

**文件路径**: `package.json`

**修改内容**：
- 更新 `name`
- 更新 `productName`
- 更新 `version`

## 备份和恢复

### 自动备份

脚本在修改文件前会自动备份到 `.customize-backup/` 目录：

```
.customize-backup/
  ├── SettingsPage.tsx.bak
  ├── BailianStrategy.ts.bak
  ├── electron-builder.yml.bak
  └── package.json.bak
```

### 手动恢复

如果需要恢复原始文件：

```bash
python3 customize-and-build.py --restore
```

## 日志记录

所有操作都会记录到 `customize-build.log` 文件中，包括：

- 配置加载
- 文件备份
- 文件修改
- 构建过程
- 错误信息

## 安装说明

### macOS

1. 双击 DMG 文件，拖动应用到 Applications
2. 首次打开时右键点击应用 → 选择"打开"
3. 点击"打开"确认

### Windows

1. 运行安装程序
2. 如果出现 SmartScreen 警告，点击"更多信息"
3. 点击"仍要运行"

## 常见问题

### Q: 脚本执行失败怎么办？

A: 检查 `customize-build.log` 文件查看详细错误信息。脚本会自动从备份恢复文件。

### Q: 可以跳过构建检查吗？

A: 可以在配置文件中设置 `"skipBuildCheck": true`，但不推荐，因为可能导致打包失败。

### Q: 如何只修改文件不打包？

A: 在配置文件中设置 `"autoBuild": false`。

### Q: 打包需要多长时间？

A: 完整的构建和打包过程可能需要 10-30 分钟，取决于机器性能。

### Q: 需要签名吗？

A: 内部使用不需要签名。对外发布建议配置签名以提升用户体验。

### Q: 如何修改打包平台？

A: 在配置文件中修改 `buildPlatforms` 字段，可选值：["mac", "windows"]。

## 注意事项

1. **磁盘空间**: 确保有足够的磁盘空间（至少 5GB）用于构建和打包
2. **网络连接**: 首次运行需要下载依赖，确保网络连接正常
3. **版本号**: 建议使用新的版本号，避免与原版本冲突
4. **幂等性**: 可以重复执行脚本，不会产生副作用
5. **备份**: 脚本会自动备份所有修改的文件

## 故障排除

### 问题：PyYAML 未安装

**错误信息**: `Error: PyYAML is required`

**解决方案**:

```bash
pip install pyyaml
```

### 问题：pnpm 未找到

**错误信息**: `pnpm: command not found`

**解决方案**:

```bash
npm install -g pnpm
```

### 问题：构建失败

**可能原因**:
- 依赖未安装
- 代码有语法错误
- 磁盘空间不足

**解决方案**:
1. 检查 `customize-build.log` 查看详细错误
2. 尝试手动运行 `pnpm install` 和 `pnpm build:check`
3. 使用 `--restore` 恢复原始文件后重试

### 问题：文件修改失败

**可能原因**:
- 文件路径不存在
- 文件内容格式已变化

**解决方案**:
1. 确认当前目录是项目根目录
2. 检查文件是否存在
3. 查看 `customize-build.log` 了解详细错误

## 技术支持

如有问题，请查看：
- 日志文件：`customize-build.log`
- 项目文档：`CLAUDE.md`
- GitHub Issues: https://github.com/kangfenmao/cherry-studio/issues

## 许可证

本脚本遵循 Cherry Studio 项目的许可证。
