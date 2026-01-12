"""
Audit Logger - سجل التدقيق
يسجل جميع العمليات الحساسة في النظام
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path


class AuditLogger:
    """مدير سجل التدقيق لتسجيل العمليات الحساسة"""

    def __init__(self, log_dir: str = "data/logs"):
        """
        تهيئة مسجل التدقيق

        Args:
            log_dir: مجلد حفظ ملفات السجلات
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_log_file = self.log_dir / f"audit_{datetime.now().strftime('%Y%m')}.json"

    def log(
        self,
        action: str,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success",
        ip_address: Optional[str] = None
    ):
        """
        تسجيل عملية في سجل التدقيق

        Args:
            action: نوع العملية (مثل: login, create_user, delete_course, etc.)
            user_id: معرّف المستخدم
            username: اسم المستخدم
            details: تفاصيل إضافية عن العملية
            status: حالة العملية (success, failed, warning)
            ip_address: عنوان IP (إن وجد)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "user_id": user_id,
            "username": username,
            "status": status,
            "details": details or {},
            "ip_address": ip_address
        }

        # قراءة السجلات الحالية
        logs = self._read_logs()

        # إضافة السجل الجديد
        logs.append(log_entry)

        # حفظ السجلات
        self._write_logs(logs)

    def _read_logs(self) -> List[Dict[str, Any]]:
        """قراءة السجلات من الملف"""
        if not self.current_log_file.exists():
            return []

        try:
            with open(self.current_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_logs(self, logs: List[Dict[str, Any]]):
        """كتابة السجلات إلى الملف"""
        with open(self.current_log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

    def get_logs(
        self,
        action: Optional[str] = None,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        استرجاع السجلات بناءً على معايير البحث

        Args:
            action: تصفية حسب نوع العملية
            user_id: تصفية حسب معرّف المستخدم
            status: تصفية حسب الحالة
            start_date: تاريخ البدء
            end_date: تاريخ النهاية
            limit: الحد الأقصى لعدد النتائج

        Returns:
            قائمة السجلات المطابقة
        """
        logs = self._read_logs()

        # تطبيق التصفية
        filtered_logs = []
        for log in logs:
            # تحويل timestamp إلى datetime للمقارنة
            log_time = datetime.fromisoformat(log['timestamp'])

            # تطبيق المعايير
            if action and log.get('action') != action:
                continue
            if user_id and log.get('user_id') != user_id:
                continue
            if status and log.get('status') != status:
                continue
            if start_date and log_time < start_date:
                continue
            if end_date and log_time > end_date:
                continue

            filtered_logs.append(log)

            # الحد الأقصى للنتائج
            if len(filtered_logs) >= limit:
                break

        return filtered_logs

    def get_recent_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        الحصول على آخر السجلات

        Args:
            limit: عدد السجلات المطلوبة

        Returns:
            قائمة السجلات الأخيرة
        """
        logs = self._read_logs()
        return logs[-limit:] if len(logs) > limit else logs

    def get_user_activity(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        الحصول على نشاط مستخدم معين

        Args:
            user_id: معرّف المستخدم
            limit: عدد السجلات المطلوبة

        Returns:
            قائمة نشاطات المستخدم
        """
        return self.get_logs(user_id=user_id, limit=limit)

    def get_failed_logins(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        الحصول على محاولات تسجيل الدخول الفاشلة

        Args:
            limit: عدد السجلات المطلوبة

        Returns:
            قائمة محاولات تسجيل الدخول الفاشلة
        """
        return self.get_logs(action='login', status='failed', limit=limit)

    def get_statistics(self) -> Dict[str, Any]:
        """
        إحصائيات سجل التدقيق

        Returns:
            قاموس يحتوي على الإحصائيات
        """
        logs = self._read_logs()

        stats = {
            'total_entries': len(logs),
            'successful_operations': sum(1 for log in logs if log.get('status') == 'success'),
            'failed_operations': sum(1 for log in logs if log.get('status') == 'failed'),
            'warning_operations': sum(1 for log in logs if log.get('status') == 'warning'),
            'unique_users': len(set(log.get('user_id') for log in logs if log.get('user_id'))),
            'actions_breakdown': {}
        }

        # تفصيل العمليات حسب النوع
        for log in logs:
            action = log.get('action', 'unknown')
            stats['actions_breakdown'][action] = stats['actions_breakdown'].get(action, 0) + 1

        return stats

    def clear_old_logs(self, days: int = 90):
        """
        حذف السجلات القديمة

        Args:
            days: عدد الأيام للاحتفاظ بالسجلات
        """
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)

        logs = self._read_logs()
        filtered_logs = [
            log for log in logs
            if datetime.fromisoformat(log['timestamp']).timestamp() > cutoff_date
        ]

        self._write_logs(filtered_logs)

        # حذف ملفات السجلات القديمة
        for log_file in self.log_dir.glob("audit_*.json"):
            file_date = datetime.strptime(log_file.stem.split('_')[1], '%Y%m')
            if (datetime.now() - file_date).days > days:
                log_file.unlink()


# إنشاء نسخة عامة من المسجل
audit_logger = AuditLogger()


# دوال مساعدة سريعة
def log_login(username: str, user_id: str, success: bool = True, ip: Optional[str] = None):
    """تسجيل محاولة تسجيل دخول"""
    audit_logger.log(
        action='login',
        user_id=user_id if success else None,
        username=username,
        status='success' if success else 'failed',
        ip_address=ip
    )


def log_logout(username: str, user_id: str):
    """تسجيل تسجيل خروج"""
    audit_logger.log(
        action='logout',
        user_id=user_id,
        username=username,
        status='success'
    )


def log_create_user(admin_username: str, admin_id: str, new_username: str, roles: List[str]):
    """تسجيل إنشاء مستخدم جديد"""
    audit_logger.log(
        action='create_user',
        user_id=admin_id,
        username=admin_username,
        details={
            'new_username': new_username,
            'roles': roles
        },
        status='success'
    )


def log_update_user(admin_username: str, admin_id: str, target_username: str, changes: Dict[str, Any]):
    """تسجيل تحديث بيانات مستخدم"""
    audit_logger.log(
        action='update_user',
        user_id=admin_id,
        username=admin_username,
        details={
            'target_username': target_username,
            'changes': changes
        },
        status='success'
    )


def log_delete_user(admin_username: str, admin_id: str, deleted_username: str):
    """تسجيل حذف مستخدم"""
    audit_logger.log(
        action='delete_user',
        user_id=admin_id,
        username=admin_username,
        details={
            'deleted_username': deleted_username
        },
        status='success'
    )


def log_create_course(username: str, user_id: str, course_name: str, course_code: str):
    """تسجيل إنشاء مقرر"""
    audit_logger.log(
        action='create_course',
        user_id=user_id,
        username=username,
        details={
            'course_name': course_name,
            'course_code': course_code
        },
        status='success'
    )


def log_delete_course(username: str, user_id: str, course_name: str, course_code: str):
    """تسجيل حذف مقرر"""
    audit_logger.log(
        action='delete_course',
        user_id=user_id,
        username=username,
        details={
            'course_name': course_name,
            'course_code': course_code
        },
        status='success'
    )


def log_backup(username: str, user_id: str, backup_type: str = 'manual'):
    """تسجيل عملية نسخ احتياطي"""
    audit_logger.log(
        action='backup',
        user_id=user_id,
        username=username,
        details={
            'type': backup_type
        },
        status='success'
    )


def log_restore(username: str, user_id: str, backup_file: str):
    """تسجيل عملية استعادة"""
    audit_logger.log(
        action='restore',
        user_id=user_id,
        username=username,
        details={
            'backup_file': backup_file
        },
        status='success'
    )
