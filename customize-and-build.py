#!/usr/bin/env python3
"""
Cherry Studio Customization and Build Script

This script automates the process of:
1. Hiding the "Data Settings" module
2. Applying BailianStrategy baseURL customization
3. Modifying build configuration (appId, productName, etc.)
4. Building and packaging for Mac and Windows

Usage:
    python3 customize-and-build.py [options]

Options:
    --config FILE    Specify config file path (default: customize-config.json)
    --dry-run       Show what would be done without making changes
    --restore       Restore all files from backup
    --help          Show this help message
"""

import os
import sys
import json
import shutil
import subprocess
import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install it with: pip install pyyaml")
    sys.exit(1)


class Logger:
    """Logger for recording all operations"""

    def __init__(self, log_file: str = "customize-build.log"):
        self.log_file = log_file
        self.log_handle = open(log_file, 'a', encoding='utf-8')

    def log(self, level: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        self.log_handle.write(log_message + "\n")
        self.log_handle.flush()

    def info(self, message: str):
        self.log(level="INFO", message=message)

    def warning(self, message: str):
        self.log(level="WARN", message=message)

    def error(self, message: str):
        self.log(level="ERROR", message=message)

    def success(self, message: str):
        self.log(level="SUCCESS", message=message)

    def close(self):
        self.log_handle.close()


class ConfigManager:
    """Configuration manager"""

    def __init__(self, config_path: str, logger: Logger):
        self.config_path = config_path
        self.logger = logger
        self.config: Dict = {}

    def load(self) -> bool:
        """Load and validate configuration"""
        try:
            if not os.path.exists(self.config_path):
                self.logger.error(f"Config file not found: {self.config_path}")
                return False

            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)

            # Validate required fields
            required_fields = ['appId', 'productName', 'packageName', 'version']
            for field in required_fields:
                if field not in self.config:
                    self.logger.error(f"Missing required field in config: {field}")
                    return False

            self.logger.info(f"Configuration loaded from {self.config_path}")
            return True

        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in config file: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return False

    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)


class BackupManager:
    """Backup manager for file operations"""

    def __init__(self, backup_dir: str, logger: Logger):
        self.backup_dir = backup_dir
        self.logger = logger
        self.backed_up_files: List[str] = []

    def create_backup_dir(self):
        """Create backup directory"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            self.logger.info(f"Created backup directory: {self.backup_dir}")

    def backup_file(self, file_path: str) -> bool:
        """Backup a file"""
        try:
            if not os.path.exists(file_path):
                self.logger.warning(f"File not found, skipping backup: {file_path}")
                return False

            backup_path = os.path.join(self.backup_dir, os.path.basename(file_path) + '.bak')
            shutil.copy2(file_path, backup_path)
            self.backed_up_files.append(file_path)
            self.logger.info(f"Backed up: {file_path} -> {backup_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to backup {file_path}: {e}")
            return False

    def restore_all(self) -> bool:
        """Restore all backed up files"""
        try:
            for file_path in self.backed_up_files:
                backup_path = os.path.join(self.backup_dir, os.path.basename(file_path) + '.bak')
                if os.path.exists(backup_path):
                    shutil.copy2(backup_path, file_path)
                    self.logger.info(f"Restored: {backup_path} -> {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to restore files: {e}")
            return False


class FileModifier:
    """File modifier for code changes"""

    def __init__(self, logger: Logger, dry_run: bool = False):
        self.logger = logger
        self.dry_run = dry_run

    def modify_settings_page(self, file_path: str) -> bool:
        """Remove DataSettings module from SettingsPage.tsx"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Remove DataSettings import
            content = re.sub(
                r"import DataSettings from '\./DataSettings/DataSettings'\n",
                '',
                content
            )

            # Remove HardDrive from icon imports
            content = re.sub(
                r',\s*\n\s*HardDrive',
                '',
                content
            )

            # Remove data settings menu item
            content = re.sub(
                r'<MenuItemLink to="/settings/data">\s*\n\s*<MenuItem className=\{isRoute\(\'/settings/data\'\)\}>\s*\n\s*<HardDrive size=\{18\} />\s*\n\s*\{t\(\'settings\.data\.title\'\)\}\s*\n\s*</MenuItem>\s*\n\s*</MenuItemLink>\s*\n',
                '',
                content,
                flags=re.MULTILINE
            )

            # Remove data settings route
            content = re.sub(
                r'<Route path="data" element=\{<DataSettings />\} />\s*\n',
                '',
                content
            )

            if content == original_content:
                # Check if already modified
                if 'DataSettings' not in content:
                    self.logger.info("SettingsPage.tsx already has DataSettings removed - skipping")
                    return True
                self.logger.warning("No changes made to SettingsPage.tsx - patterns may not match")
                return False

            if not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.logger.success(f"Modified: {file_path}")
            else:
                self.logger.info(f"[DRY RUN] Would modify: {file_path}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to modify {file_path}: {e}")
            return False

    def modify_bailian_strategy(self, file_path: str) -> bool:
        """Add baseURL parameter to BailianStrategy.ts"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check if already modified
            if 'buildUrl(baseURL?: string)' in content:
                self.logger.info("BailianStrategy.ts already has baseURL parameter - skipping")
                return True

            # Replace buildUrl method
            old_method = r"buildUrl\(\): string \{\s*\n\s*return 'https://dashscope\.aliyuncs\.com/api/v1/services/rerank/text-rerank/text-rerank'\s*\n\s*\}"

            new_method = """buildUrl(baseURL?: string): string {
    // 如果提供了自定义 baseURL，使用自定义地址
    if (baseURL) {
      const cleanBaseURL = baseURL.endsWith('/') ? baseURL.slice(0, -1) : baseURL
      return `${cleanBaseURL}/api/v1/services/rerank/text-rerank/text-rerank`
    }
    // 否则使用默认的阿里云官方地址
    return 'https://dashscope.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank'
  }"""

            if not re.search(old_method, content):
                self.logger.warning("BailianStrategy.ts buildUrl method pattern not found - file may have unexpected format")
                return False

            content = re.sub(old_method, new_method, content)

            if not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.logger.success(f"Modified: {file_path}")
            else:
                self.logger.info(f"[DRY RUN] Would modify: {file_path}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to modify {file_path}: {e}")
            return False

    def modify_electron_builder_yml(self, file_path: str, app_id: str, product_name: str) -> bool:
        """Modify electron-builder.yml"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            config['appId'] = app_id
            config['productName'] = product_name

            if not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                self.logger.success(f"Modified: {file_path}")
            else:
                self.logger.info(f"[DRY RUN] Would modify: {file_path}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to modify {file_path}: {e}")
            return False

    def hide_update_ui(self) -> bool:
        """Hide update-related UI elements"""
        success = True

        # --- UpdateAppButton.tsx: return null immediately ---
        btn_path = 'src/renderer/src/pages/home/components/UpdateAppButton.tsx'
        try:
            with open(btn_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'return null // customized: hidden' in content:
                self.logger.info("UpdateAppButton.tsx already hidden - skipping")
            else:
                content = re.sub(
                    r'(const UpdateAppButton: FC = \(\) => \{)',
                    r'\1\n  return null // customized: hidden',
                    content
                )
                if not self.dry_run:
                    with open(btn_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.logger.success(f"Modified: {btn_path}")
                else:
                    self.logger.info(f"[DRY RUN] Would modify: {btn_path}")
        except Exception as e:
            self.logger.error(f"Failed to modify {btn_path}: {e}")
            success = False

        # --- AboutSettings.tsx: remove CheckUpdateButton and auto-update/test-plan rows ---
        about_path = 'src/renderer/src/pages/settings/AboutSettings.tsx'
        try:
            with open(about_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if '// customized: update ui hidden' in content:
                self.logger.info("AboutSettings.tsx already hidden - skipping")
            else:
                # Remove CheckUpdateButton block (inside AboutHeader, guarded by !isPortable)
                old_check_btn = """          {!isPortable && (
            <CheckUpdateButton
              onClick={onCheckUpdate}
              loading={update.checking}
              disabled={update.downloading || update.checking}>
              {update.downloading
                ? t('settings.about.downloading')
                : update.available
                  ? t('settings.about.checkUpdate.available')
                  : t('settings.about.checkUpdate.label')}
            </CheckUpdateButton>
          )}"""
                content = content.replace(old_check_btn, '')

                # Remove auto-update + test-plan block (second !isPortable guard after AboutHeader)
                old_update_block = """        {!isPortable && (
          <>
            <SettingDivider />
            <SettingRow>
              <SettingRowTitle>{t('settings.general.auto_check_update.title')}</SettingRowTitle>
              <Switch value={autoCheckUpdate} onChange={(v) => setAutoCheckUpdate(v)} />
            </SettingRow>
            <SettingDivider />
            <SettingRow>
              <SettingRowTitle>{t('settings.general.test_plan.title')}</SettingRowTitle>
              <Tooltip title={t('settings.general.test_plan.tooltip')} trigger={['hover', 'focus']}>
                <Switch value={testPlan} onChange={(v) => handleSetTestPlan(v)} />
              </Tooltip>
            </SettingRow>
            {testPlan && (
              <>
                <SettingDivider />
                <SettingRow>
                  <SettingRowTitle>{t('settings.general.test_plan.version_options')}</SettingRowTitle>
                  <Radio.Group
                    size="small"
                    buttonStyle="solid"
                    value={getTestChannel()}
                    onChange={(e) => handleTestChannelChange(e.target.value)}>
                    {getAvailableTestChannels().map((option) => (
                      <Tooltip key={option.value} title={option.tooltip}>
                        <Radio.Button value={option.value}>{option.label}</Radio.Button>
                      </Tooltip>
                    ))}
                  </Radio.Group>
                </SettingRow>
              </>
            )}
          </>
        )}"""
                content = content.replace(old_update_block, '')

                # Remove unused state and functions
                content = content.replace(
                    "  const [isPortable, setIsPortable] = useState(false)\n",
                    ''
                )
                content = content.replace(
                    "  const { autoCheckUpdate, setAutoCheckUpdate, testPlan, setTestPlan, testChannel, setTestChannel } = useSettings()\n",
                    "  const { autoCheckUpdate, setAutoCheckUpdate } = useSettings()\n"
                )
                content = content.replace(
                    "\n  const onCheckUpdate = debounce(\n    async () => {\n      if (update.checking || update.downloading) {\n        return\n      }\n\n      if (update.downloaded) {\n        // Open update dialog directly in renderer\n        UpdateDialogPopup.show({ releaseInfo: update.info || null })\n        return\n      }\n\n      dispatch(setUpdateState({ checking: true }))\n\n      try {\n        await window.api.checkForUpdate()\n      } catch (error) {\n        window.toast.error(t('settings.about.updateError'))\n      }\n\n      dispatch(setUpdateState({ checking: false }))\n    },\n    2000,\n    { leading: true, trailing: false }\n  )\n",
                    '\n'
                )
                content = content.replace(
                    "\n  const currentChannelByVersion =\n    [\n      { pattern: `-${UpgradeChannel.BETA}.`, channel: UpgradeChannel.BETA },\n      { pattern: `-${UpgradeChannel.RC}.`, channel: UpgradeChannel.RC }\n    ].find(({ pattern }) => version.includes(pattern))?.channel || UpgradeChannel.LATEST\n\n  const handleTestChannelChange = async (value: UpgradeChannel) => {\n    if (testPlan && currentChannelByVersion !== UpgradeChannel.LATEST && value !== currentChannelByVersion) {\n      window.toast.warning(t('settings.general.test_plan.version_channel_not_match'))\n    }\n    setTestChannel(value)\n    // Clear update info when switching upgrade channel\n    dispatch(\n      setUpdateState({\n        available: false,\n        info: null,\n        downloaded: false,\n        checking: false,\n        downloading: false,\n        downloadProgress: 0\n      })\n    )\n  }\n\n  // Get available test version options based on current version\n  const getAvailableTestChannels = () => {\n    return [\n      {\n        tooltip: t('settings.general.test_plan.rc_version_tooltip'),\n        label: t('settings.general.test_plan.rc_version'),\n        value: UpgradeChannel.RC\n      },\n      {\n        tooltip: t('settings.general.test_plan.beta_version_tooltip'),\n        label: t('settings.general.test_plan.beta_version'),\n        value: UpgradeChannel.BETA\n      }\n    ]\n  }\n\n  const handleSetTestPlan = (value: boolean) => {\n    setTestPlan(value)\n    dispatch(\n      setUpdateState({\n        available: false,\n        info: null,\n        downloaded: false,\n        checking: false,\n        downloading: false,\n        downloadProgress: 0\n      })\n    )\n\n    if (value === true) {\n      setTestChannel(getTestChannel())\n    }\n  }\n\n  const getTestChannel = () => {\n    if (testChannel === UpgradeChannel.LATEST) {\n      return UpgradeChannel.RC\n    }\n    return testChannel\n  }\n",
                    '\n'
                )
                # Fix useEffect: remove setIsPortable call
                content = content.replace(
                    "      setVersion(appInfo.version)\n      setIsPortable(appInfo.isPortable)\n",
                    "      setVersion(appInfo.version)\n"
                )
                # Remove CheckUpdateButton styled component
                content = content.replace(
                    "\nconst CheckUpdateButton = styled(Button)``\n",
                    '\n'
                )
                # Remove unused dispatch
                content = content.replace(
                    "  const dispatch = useAppDispatch()\n",
                    ''
                )
                content += '\n// customized: update ui hidden'
                if not self.dry_run:
                    with open(about_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.logger.success(f"Modified: {about_path}")
                else:
                    self.logger.info(f"[DRY RUN] Would modify: {about_path}")
        except Exception as e:
            self.logger.error(f"Failed to modify {about_path}: {e}")
            success = False

        # --- settings.ts: set autoCheckUpdate default to false ---
        store_path = 'src/renderer/src/store/settings.ts'
        try:
            with open(store_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'autoCheckUpdate: false, // customized' in content:
                self.logger.info("settings.ts autoCheckUpdate already false - skipping")
            else:
                content = re.sub(
                    r'autoCheckUpdate: true,',
                    'autoCheckUpdate: false, // customized',
                    content
                )
                if not self.dry_run:
                    with open(store_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.logger.success(f"Modified: {store_path}")
                else:
                    self.logger.info(f"[DRY RUN] Would modify: {store_path}")
        except Exception as e:
            self.logger.error(f"Failed to modify {store_path}: {e}")
            success = False

        return success

    def modify_package_json(self, file_path: str, package_name: str, product_name: str, version: str) -> bool:
        """Modify package.json"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            config['name'] = package_name
            config['productName'] = product_name
            config['version'] = version

            if not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                    f.write('\n')  # Add trailing newline
                self.logger.success(f"Modified: {file_path}")
            else:
                self.logger.info(f"[DRY RUN] Would modify: {file_path}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to modify {file_path}: {e}")
            return False


class BuildManager:
    """Build and package manager"""

    def __init__(self, logger: Logger, dry_run: bool = False):
        self.logger = logger
        self.dry_run = dry_run

    def run_command(self, command: List[str], description: str) -> bool:
        """Run a shell command"""
        try:
            self.logger.info(f"{description}...")

            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would run: {' '.join(command)}")
                return True

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                shell=sys.platform == 'win32'
            )

            if result.returncode == 0:
                self.logger.success(f"{description} completed")
                return True
            else:
                self.logger.error(f"{description} failed")
                if result.stdout:
                    self.logger.error(f"Output: {result.stdout[-3000:]}")
                if result.stderr:
                    self.logger.error(f"Error output: {result.stderr[-3000:]}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to run command: {e}")
            return False

    def install_dependencies(self) -> bool:
        """Install dependencies"""
        return self.run_command(['pnpm', 'install'], "Installing dependencies")

    def run_build_check(self) -> bool:
        """Run build check (lint + test + typecheck)"""
        return self.run_command(['pnpm', 'build:check'], "Running build check")

    def build_mac(self) -> bool:
        """Build Mac package"""
        return self.run_command(['pnpm', 'build:mac'], "Building Mac package")

    def build_windows(self) -> bool:
        """Build Windows package"""
        return self.run_command(['pnpm', 'build:win'], "Building Windows package")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Cherry Studio Customization and Build Script',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--config', default='customize-config.json', help='Config file path')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    parser.add_argument('--restore', action='store_true', help='Restore from backup')

    args = parser.parse_args()

    # Initialize logger
    logger = Logger()
    logger.info("=" * 60)
    logger.info("Cherry Studio Customization and Build Script")
    logger.info("=" * 60)

    # Initialize backup manager
    backup_manager = BackupManager('.customize-backup', logger)
    backup_manager.create_backup_dir()

    # Handle restore mode
    if args.restore:
        logger.info("Restoring files from backup...")
        if backup_manager.restore_all():
            logger.success("All files restored successfully")
        else:
            logger.error("Failed to restore files")
        logger.close()
        return

    # Load configuration
    config_manager = ConfigManager(args.config, logger)
    if not config_manager.load():
        logger.error("Failed to load configuration. Exiting.")
        logger.close()
        sys.exit(1)

    # Define files to modify
    files_to_modify = [
        'src/renderer/src/pages/settings/SettingsPage.tsx',
        'src/main/knowledge/reranker/strategies/BailianStrategy.ts',
        'electron-builder.yml',
        'package.json',
        'src/renderer/src/pages/home/components/UpdateAppButton.tsx',
        'src/renderer/src/pages/settings/AboutSettings.tsx',
        'src/renderer/src/store/settings.ts',
    ]

    # Backup files
    logger.info("Backing up files...")
    for file_path in files_to_modify:
        backup_manager.backup_file(file_path)

    # Initialize file modifier
    file_modifier = FileModifier(logger, args.dry_run)

    # Modify files
    success = True

    if config_manager.get('hideDataSettings', True):
        logger.info("Removing DataSettings module...")
        if not file_modifier.modify_settings_page('src/renderer/src/pages/settings/SettingsPage.tsx'):
            success = False

    if config_manager.get('applyBailianFix', True):
        logger.info("Applying BailianStrategy baseURL modification...")
        if not file_modifier.modify_bailian_strategy('src/main/knowledge/reranker/strategies/BailianStrategy.ts'):
            success = False

    if config_manager.get('hideUpdateUI', True):
        logger.info("Hiding update UI elements...")
        if not file_modifier.hide_update_ui():
            success = False

    logger.info("Updating build configuration...")
    if not file_modifier.modify_electron_builder_yml(
        'electron-builder.yml',
        config_manager.get('appId'),
        config_manager.get('productName')
    ):
        success = False

    if not file_modifier.modify_package_json(
        'package.json',
        config_manager.get('packageName'),
        config_manager.get('productName'),
        config_manager.get('version')
    ):
        success = False

    if not success:
        logger.error("Some modifications failed. Check the log for details.")
        if not args.dry_run:
            logger.info("Restoring from backup...")
            backup_manager.restore_all()
        logger.close()
        sys.exit(1)

    # Build and package
    if config_manager.get('autoBuild', True) and not args.dry_run:
        build_manager = BuildManager(logger, args.dry_run)

        if not config_manager.get('skipInstall', False):
            if not build_manager.install_dependencies():
                logger.error("Failed to install dependencies")
                logger.close()
                sys.exit(1)

        if not build_manager.run_command(['pnpm', 'format'], "Formatting code"):
            logger.error("Code formatting failed")
            logger.close()
            sys.exit(1)

        if not config_manager.get('skipBuildCheck', False):
            if not build_manager.run_build_check():
                logger.error("Build check failed")
                logger.close()
                sys.exit(1)

        build_platforms = config_manager.get('buildPlatforms', [])

        if 'mac' in build_platforms:
            if not build_manager.build_mac():
                logger.error("Mac build failed")
                logger.close()
                sys.exit(1)

        if 'windows' in build_platforms:
            if not build_manager.build_windows():
                logger.error("Windows build failed")
                logger.close()
                sys.exit(1)

        logger.success("Build completed successfully!")
        logger.info("Installation packages are in the 'dist/' directory")

    logger.info("=" * 60)
    logger.success("Customization completed successfully!")
    logger.info("=" * 60)
    logger.close()


if __name__ == '__main__':
    main()
