"""
Supplemental command-verification tasks for every RHCSA practice topic.

These are deliberately practice-only: they reinforce the current RHEL
operator workflow without taking the place of configuration tasks in a
randomized exam.  Each task asks the candidate to capture a real command's
output, which makes the task independently gradable on minimal VMs.
"""

from tasks.base import BaseTask
from tasks.registry import TaskRegistry
from core.validator import ValidationCheck, ValidationResult
from validators.safe_executor import execute_safe


_TOPICS = {
    "users_groups": ("id", "local account identity and group membership"),
    "permissions": ("umask", "the current default permission mask"),
    "essential_tools": ("tar --version", "archive tooling"),
    "lvm": ("lvs", "logical volume inventory"),
    "filesystems": ("findmnt", "mounted filesystems"),
    "networking": ("ip address", "network addresses"),
    "ssh": ("ssh -V", "the OpenSSH client version"),
    "selinux": ("getenforce", "SELinux enforcement state"),
    "services": ("systemctl list-units --type=service --state=running", "running services"),
    "processes": ("ps -eo pid,comm,%cpu,%mem", "the process table"),
    "time_services": ("timedatectl", "time and synchronization state"),
    "troubleshooting": ("journalctl -p err -b --no-pager", "current-boot errors"),
    "boot": ("systemctl get-default", "the default boot target"),
    "scheduling": ("crontab -l", "the current user's cron schedule"),
    "scripting": ("bash --version", "the installed Bash interpreter"),
    "packages": ("rpm --eval %{_arch}", "the RPM architecture"),
    "partitioning": ("lsblk -f", "block devices and filesystem metadata"),
    "network_storage": ("findmnt -t nfs,nfs4", "NFS mounts"),
    "repos": ("dnf repolist", "enabled package repositories"),
    "flatpak": ("flatpak remotes", "configured Flatpak remotes"),
    "boot_recovery": ("systemctl get-default", "the recovery-relevant boot target"),
    "journalctl": ("journalctl --list-boots --no-pager", "available journal boots"),
    "systemd_timers": ("systemctl list-timers --all --no-pager", "systemd timers"),
    "firewall": ("firewall-cmd --get-active-zones", "active firewalld zones"),
    "swap": ("swapon --show", "active swap devices"),
    "containers": ("podman ps --all", "local containers"),
}


def _make_task_class(category, command, subject):
    """Create one named task class while keeping the catalogue declarative."""
    class TopicVerificationTask(BaseTask):
        exam_eligible = False
        has_setup = True

        def __init__(self):
            super().__init__(
                id=f"verify_{category}_001",
                category=category,
                difficulty="easy",
                points=5,
            )
            self.output_file = f"/tmp/rhcsa_verify_{category}.txt"
            self.tags = ["verification", "current-rhel", category]
            self.exam_tips = [
                "Capture command output with shell redirection, then inspect it.",
                "Use the command shown in the task rather than changing system state.",
            ]

        def setup_environment(self):
            from tasks import env_setup
            return env_setup.remove_paths(self.id, [self.output_file])

        def generate(self, **params):
            self.output_file = params.get(
                "output", f"/tmp/rhcsa_verify_{category}.txt")
            self.description = (
                f"Verify {subject} on this RHEL system.\n"
                f"  - Run: {command}\n"
                f"  - Save the complete output to: {self.output_file}\n"
                "  - Review the saved output and leave it available for grading."
            )
            self.hints = [
                f"{command} > {self.output_file} 2>&1",
                f"Review it with: less {self.output_file}",
            ]
            return self

        def validate(self):
            result = execute_safe(["test", "-s", self.output_file])
            check = ValidationCheck(
                "command_output",
                result.success,
                self.points if result.success else 0,
                f"Saved {subject} output is present"
                if result.success else
                f"Expected non-empty output file: {self.output_file}",
                max_points=self.points,
            )
            return ValidationResult(
                self.id, result.success, check.points, self.points, [check])

    TopicVerificationTask.__name__ = (
        "".join(part.title() for part in category.split("_"))
        + "VerificationTask"
    )
    return TopicVerificationTask


for _category, (_command, _subject) in _TOPICS.items():
    _task_class = _make_task_class(_category, _command, _subject)
    TaskRegistry.register(_category)(_task_class)

