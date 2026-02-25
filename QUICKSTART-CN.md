# Cherry Studio 自动化定制脚本 - 快速开始

## 一、环境准备

### 1. 安装 Python 依赖

```bash
pip3 install pyyaml
```

### 2. 确认 pnpm 已安装

```bash
pnpm --version
```

如果未安装：

```bash
npm install -g pnpm
```

## 二、配置定制参数

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

### 配置说明

| 字段 | 说明 | 示例 |
|------|------|------|
| `appId` | 应用唯一标识符 | `com.yourcompany.YourAppName` |
| `productName` | 产品显示名称 | `Your App Name` |
| `packageName` | 包名（用于 package.json） | `YourAppName` |
| `version` | 版本号 | `1.0.0` |
| `hideDataSettings` | 是否隐藏数据设置模块 | `true` / `false` |
| `applyBailianFix` | 是否应用 Bailian baseURL 修改 | `true` / `false` |
| `buildPlatforms` | 打包平台 | `["mac"]` 或 `["windows"]` 或 `["mac", "windows"]` |
| `autoBuild` | 是否自动执行构建和打包 | `true` / `false` |
| `skipBuildCheck` | 是否跳过构建检查（不推荐） | `true` / `false` |
| `skipInstall` | 是否跳过依赖安装 | `true` / `false` |

## 三、运行脚本

### 预览模式（推荐首次运行）

```bash
python3 customize-and-build.py --dry-run
```

这会显示将要执行的操作，但不会实际修改文件。

### 正式运行

```bash
python3 customize-and-build.py
```

脚本会自动完成：
1. 备份原始文件
2. 修改代码
3. 更新配置
4. 安装依赖（如果需要）
5. 运行构建检查
6. 打包生成安装包

### 仅修改文件，不打包

如果只想修改文件，不想立即打包，可以在配置文件中设置：

```json
{
  "autoBuild": false
}
```

然后运行脚本。

## 四、获取安装包

打包完成后，安装包位于 `dist/` 目录：

- **macOS**: `dist/Your App Name-{version}.dmg`
- **Windows**: `dist/Your App Name Setup {version}.exe`

## 五、日常更新流程

每次从 GitHub 拉取最新代码后：

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 运行脚本
python3 customize-and-build.py

# 3. 等待完成，安装包位于 dist/ 目录
```

## 六、常用命令

### 查看帮助

```bash
python3 customize-and-build.py --help
```

### 使用自定义配置文件

```bash
python3 customize-and-build.py --config my-config.json
```

### 恢复原始文件

```bash
python3 customize-and-build.py --restore
```

## 七、故障排除

### 问题：脚本执行失败

**解决方案**：
1. 查看 `customize-build.log` 文件了解详细错误
2. 脚本会自动从备份恢复文件
3. 修复问题后重新运行

### 问题：构建检查失败

**可能原因**：
- 代码有语法错误
- 依赖未正确安装
- i18n 文件需要同步

**解决方案**：

```bash
# 同步 i18n 文件
pnpm i18n:sync

# 格式化代码
pnpm format

# 重新运行脚本
python3 customize-and-build.py
```

### 问题：打包失败

**解决方案**：
1. 确保有足够的磁盘空间（至少 5GB）
2. 检查网络连接是否正常
3. 查看日志文件了解详细错误

### 问题：安装包无法打开（macOS）

**解决方案**：
1. 右键点击应用
2. 选择"打开"
3. 点击"打开"确认

### 问题：SmartScreen 警告（Windows）

**解决方案**：
1. 点击"更多信息"
2. 点击"仍要运行"

## 八、文件说明

| 文件 | 说明 |
|------|------|
| `customize-and-build.py` | 主脚本 |
| `customize-config.json` | 配置文件 |
| `customize-config.example.json` | 配置文件示例 |
| `README-CUSTOMIZE.md` | 详细文档 |
| `QUICKSTART-CN.md` | 快速开始指南（本文件） |
| `.customize-backup/` | 备份目录（自动创建） |
| `customize-build.log` | 构建日志（自动创建） |

## 九、注意事项

1. **首次运行建议使用 `--dry-run` 模式**预览操作
2. **备份重要数据**，虽然脚本有自动备份机制
3. **版本号建议使用新的版本号**，避免与原版本冲突
4. **构建时间较长**，完整打包可能需要 10-30 分钟
5. **磁盘空间**确保至少有 5GB 可用空间
6. **网络连接**首次运行需要下载依赖

## 十、技术支持

- 查看日志：`customize-build.log`
- 项目文档：`README-CUSTOMIZE.md`
- GitHub Issues: https://github.com/kangfenmao/cherry-studio/issues

## 十一、脚本特性

- ✅ **幂等性**：可以重复执行，不会产生副作用
- ✅ **自动备份**：修改前自动备份所有文件
- ✅ **错误回滚**：遇到错误自动恢复原始文件
- ✅ **详细日志**：记录每一步操作
- ✅ **配置驱动**：所有自定义配置集中管理
- ✅ **预览模式**：支持 dry-run 模式预览操作
- ✅ **灵活构建**：可选择打包平台和构建选项
