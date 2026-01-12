"""
Backup Manager - مدير النسخ الاحتياطي
يدير النسخ الاحتياطي التلقائي والاستعادة للبيانات
"""

import json
import os
import shutil
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any
import threading


class BackupManager:
    """مدير النسخ الاحتياطي التلقائي واليدوي"""

    def __init__(
        self,
        data_dir: str = "data",
        backup_dir: str = "backups",
        auto_backup_enabled: bool = True,
        backup_interval_hours: int = 24,
        max_backups: int = 30
    ):
        """
        تهيئة مدير النسخ الاحتياطي

        Args:
            data_dir: مجلد البيانات المراد نسخها
            backup_dir: مجلد حفظ النسخ الاحتياطية
            auto_backup_enabled: تفعيل النسخ التلقائي
            backup_interval_hours: الفترة بين كل نسخة (بالساعات)
            max_backups: الحد الأقصى للنسخ الاحتياطية المحفوظة
        """
        self.data_dir = Path(data_dir)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.auto_backup_enabled = auto_backup_enabled
        self.backup_interval_hours = backup_interval_hours
        self.max_backups = max_backups

        self.config_file = self.backup_dir / "backup_config.json"
        self._load_config()

        # بدء النسخ التلقائي إذا كان مفعلاً
        if self.auto_backup_enabled:
            self._start_auto_backup()

    def _load_config(self):
        """تحميل إعدادات النسخ الاحتياطي"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.last_backup_time = datetime.fromisoformat(config.get('last_backup_time', ''))
            except:
                self.last_backup_time = None
        else:
            self.last_backup_time = None

    def _save_config(self):
        """حفظ إعدادات النسخ الاحتياطي"""
        config = {
            'last_backup_time': self.last_backup_time.isoformat() if self.last_backup_time else None,
            'auto_backup_enabled': self.auto_backup_enabled,
            'backup_interval_hours': self.backup_interval_hours,
            'max_backups': self.max_backups
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def create_backup(self, backup_type: str = 'manual', description: str = '') -> Optional[str]:
        """
        إنشاء نسخة احتياطية

        Args:
            backup_type: نوع النسخة (manual أو auto)
            description: وصف النسخة الاحتياطية

        Returns:
            مسار ملف النسخة الاحتياطية أو None في حالة الفشل
        """
        try:
            # إنشاء اسم الملف
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"backup_{backup_type}_{timestamp}.zip"
            backup_path = self.backup_dir / backup_filename

            # إنشاء ملف مضغوط
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # نسخ جميع الملفات من مجلد البيانات
                for root, dirs, files in os.walk(self.data_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(self.data_dir.parent)
                        zipf.write(file_path, arcname)

                # إضافة ملف معلومات النسخة
                backup_info = {
                    'timestamp': datetime.now().isoformat(),
                    'type': backup_type,
                    'description': description,
                    'files_count': len(zipf.namelist())
                }
                zipf.writestr('backup_info.json', json.dumps(backup_info, ensure_ascii=False, indent=2))

            # تحديث وقت آخر نسخة
            self.last_backup_time = datetime.now()
            self._save_config()

            # حذف النسخ القديمة
            self._cleanup_old_backups()

            return str(backup_path)

        except Exception as e:
            print(f"Error creating backup: {e}")
            return None

    def restore_backup(self, backup_path: str) -> bool:
        """
        استعادة من نسخة احتياطية

        Args:
            backup_path: مسار ملف النسخة الاحتياطية

        Returns:
            True إذا نجحت العملية، False إذا فشلت
        """
        try:
            backup_path = Path(backup_path)
            if not backup_path.exists():
                print(f"Backup file not found: {backup_path}")
                return False

            # إنشاء نسخة احتياطية قبل الاستعادة (للأمان)
            safety_backup = self.create_backup(backup_type='pre_restore', description='Before restore')

            # استخراج الملفات
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # حذف البيانات الحالية
                if self.data_dir.exists():
                    shutil.rmtree(self.data_dir)

                # استخراج النسخة الاحتياطية
                for member in zipf.namelist():
                    if member != 'backup_info.json':
                        zipf.extract(member, self.data_dir.parent)

            return True

        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False

    def get_backup_list(self) -> List[Dict[str, Any]]:
        """
        الحصول على قائمة النسخ الاحتياطية المتاحة

        Returns:
            قائمة بمعلومات النسخ الاحتياطية
        """
        backups = []

        for backup_file in sorted(self.backup_dir.glob("backup_*.zip"), reverse=True):
            try:
                # قراءة معلومات النسخة
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    if 'backup_info.json' in zipf.namelist():
                        info_data = zipf.read('backup_info.json').decode('utf-8')
                        info = json.loads(info_data)
                    else:
                        # نسخة قديمة بدون معلومات
                        info = {
                            'timestamp': datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat(),
                            'type': 'unknown',
                            'description': '',
                            'files_count': len(zipf.namelist())
                        }

                    backups.append({
                        'filename': backup_file.name,
                        'path': str(backup_file),
                        'size': backup_file.stat().st_size,
                        'size_mb': round(backup_file.stat().st_size / (1024 * 1024), 2),
                        **info
                    })

            except Exception as e:
                print(f"Error reading backup {backup_file}: {e}")
                continue

        return backups

    def _cleanup_old_backups(self):
        """حذف النسخ الاحتياطية القديمة"""
        backups = self.get_backup_list()

        # الاحتفاظ بآخر max_backups نسخة فقط
        if len(backups) > self.max_backups:
            for backup in backups[self.max_backups:]:
                try:
                    Path(backup['path']).unlink()
                except Exception as e:
                    print(f"Error deleting old backup: {e}")

    def _should_auto_backup(self) -> bool:
        """التحقق من الحاجة لإنشاء نسخة تلقائية"""
        if not self.last_backup_time:
            return True

        time_since_last_backup = datetime.now() - self.last_backup_time
        return time_since_last_backup.total_seconds() / 3600 >= self.backup_interval_hours

    def _start_auto_backup(self):
        """بدء عملية النسخ التلقائي"""
        def auto_backup_loop():
            while self.auto_backup_enabled:
                if self._should_auto_backup():
                    self.create_backup(backup_type='auto', description='Automatic backup')

                # الانتظار لساعة واحدة قبل التحقق مرة أخرى
                threading.Event().wait(3600)

        # بدء خيط منفصل للنسخ التلقائي
        backup_thread = threading.Thread(target=auto_backup_loop, daemon=True)
        backup_thread.start()

    def delete_backup(self, backup_path: str) -> bool:
        """
        حذف نسخة احتياطية

        Args:
            backup_path: مسار ملف النسخة الاحتياطية

        Returns:
            True إذا نجحت العملية، False إذا فشلت
        """
        try:
            Path(backup_path).unlink()
            return True
        except Exception as e:
            print(f"Error deleting backup: {e}")
            return False

    def get_backup_info(self, backup_path: str) -> Optional[Dict[str, Any]]:
        """
        الحصول على معلومات نسخة احتياطية معينة

        Args:
            backup_path: مسار ملف النسخة الاحتياطية

        Returns:
            قاموس بمعلومات النسخة أو None
        """
        try:
            backup_path = Path(backup_path)
            if not backup_path.exists():
                return None

            with zipfile.ZipFile(backup_path, 'r') as zipf:
                if 'backup_info.json' in zipf.namelist():
                    info_data = zipf.read('backup_info.json').decode('utf-8')
                    return json.loads(info_data)

            return None

        except Exception as e:
            print(f"Error getting backup info: {e}")
            return None

    def export_backup(self, backup_path: str, destination: str) -> bool:
        """
        تصدير نسخة احتياطية إلى موقع خارجي

        Args:
            backup_path: مسار ملف النسخة الاحتياطية
            destination: المسار المستهدف

        Returns:
            True إذا نجحت العملية، False إذا فشلت
        """
        try:
            shutil.copy2(backup_path, destination)
            return True
        except Exception as e:
            print(f"Error exporting backup: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        إحصائيات النسخ الاحتياطي

        Returns:
            قاموس بالإحصائيات
        """
        backups = self.get_backup_list()

        return {
            'total_backups': len(backups),
            'auto_backups': sum(1 for b in backups if b.get('type') == 'auto'),
            'manual_backups': sum(1 for b in backups if b.get('type') == 'manual'),
            'total_size_mb': round(sum(b['size'] for b in backups) / (1024 * 1024), 2),
            'last_backup_time': self.last_backup_time.isoformat() if self.last_backup_time else None,
            'oldest_backup': backups[-1]['timestamp'] if backups else None,
            'newest_backup': backups[0]['timestamp'] if backups else None
        }


# إنشاء نسخة عامة من المدير
backup_manager = BackupManager()
