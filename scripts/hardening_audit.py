#!/usr/bin/env python3
"""Read-only hardening audit for the Ubuntu Security Gateway Lab.

The script intentionally does not change the host. It collects a small,
reviewable snapshot of the system and writes a Markdown report under reports/.
The reports directory is private/ignored by Git in this project.
"""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
REPORT_FILE = PROJECT_DIR / "reports" / "11-hardening-audit-private.md"


def run_command(command: list[str]) -> tuple[int, str, str]:
    """Run one command without a shell and return code/stdout/stderr.

    - shell=False (the default) avoids shell expansion/injection.
    - capture_output=True lets Python inspect the result.
    - text=True decodes stdout/stderr as text.
    - check=False keeps the audit running when one probe is unavailable.
    """

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except FileNotFoundError:
        return 127, "", f"command not found: {command[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", "command timed out"

    return result.returncode, result.stdout.strip(), result.stderr.strip()


def command_section(title: str, command: list[str]) -> str:
    """Return a Markdown section containing the output of one command."""

    code, stdout, stderr = run_command(command)
    output = stdout or stderr or "(no output)"

    return "\n".join(
        [
            f"## {title}",
            "",
            f"Command: `{' '.join(command)}`",
            "",
            f"Exit code: `{code}`",
            "",
            "```text",
            output,
            "```",
            "",
        ]
    )


def uid_zero_section() -> str:
    """List accounts that have UID 0 using /etc/passwd."""

    users: list[str] = []

    with Path("/etc/passwd").open("r", encoding="utf-8") as passwd:
        for line in passwd:
            fields = line.rstrip("\n").split(":")
            if len(fields) >= 3 and fields[2] == "0":
                users.append(fields[0])

    verdict = (
        "PASS: only root has UID 0."
        if users == ["root"]
        else "WARN: one or more additional UID 0 accounts were found."
    )

    return "\n".join(
        [
            "## UID 0 accounts",
            "",
            "```text",
            *(users or ["(none found)"]),
            "```",
            "",
            verdict,
            "",
        ]
    )


def network_hardening_section() -> str:
    """Read the network sysctls used by the gateway hardening profile."""

    parameters = [
        "net.ipv4.ip_forward",
        "net.ipv4.conf.all.rp_filter",
        "net.ipv4.conf.default.rp_filter",
        "net.ipv4.conf.all.accept_redirects",
        "net.ipv4.conf.default.accept_redirects",
        "net.ipv4.conf.all.send_redirects",
        "net.ipv4.conf.default.send_redirects",
        "net.ipv4.conf.all.accept_source_route",
        "net.ipv4.conf.default.accept_source_route",
        "net.ipv4.conf.all.log_martians",
        "net.ipv4.conf.default.log_martians",
        "net.ipv4.tcp_syncookies",
    ]

    lines = ["## Kernel network hardening", "", "```text"]

    for parameter in parameters:
        code, stdout, stderr = run_command(["sysctl", parameter])
        if code == 0:
            lines.append(stdout)
        else:
            lines.append(f"{parameter}: ERROR - {stderr}")

    lines.extend(["```", ""])
    return "\n".join(lines)


def docker_socket_section() -> str:
    """Show Docker socket ownership without trying to change group membership."""

    socket_path = Path("/var/run/docker.sock")
    lines = ["## Docker socket", ""]

    if socket_path.exists():
        _, stdout, stderr = run_command(["ls", "-l", str(socket_path)])
        lines.extend(["```text", stdout or stderr, "```", ""])
    else:
        lines.extend(["Docker socket not found.", ""])

    return "\n".join(lines)


def ssh_section() -> str:
    """Read effective OpenSSH server settings when sshd is installed."""

    sshd_config = Path("/etc/ssh/sshd_config")
    if not sshd_config.exists():
        return "## SSH hardening\n\nsshd_config not found.\n"

    code, stdout, stderr = run_command(["sshd", "-T"])
    interesting = {
        "permitrootlogin",
        "passwordauthentication",
        "pubkeyauthentication",
        "permitemptypasswords",
        "maxauthtries",
        "x11forwarding",
        "allowtcpforwarding",
    }

    lines = ["## SSH hardening", "", "```text"]
    if code == 0:
        for line in stdout.splitlines():
            key = line.split(" ", 1)[0]
            if key in interesting:
                lines.append(line)
    else:
        lines.append(stderr or "unable to read effective sshd configuration")
    lines.extend(["```", ""])
    return "\n".join(lines)


def main() -> None:
    print("[*] Starting hardening audit...")

    report: list[str] = [
        "# 11 - Linux Gateway Hardening Audit",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "> Read-only audit. No configuration is changed.",
        "",
        command_section("Kernel", ["uname", "-a"]),
        command_section("Linux distribution", ["cat", "/etc/os-release"]),
        command_section("Uptime", ["uptime"]),
        command_section("Current identity", ["id"]),
        uid_zero_section(),
        command_section("Network interfaces", ["ip", "-brief", "address"]),
        command_section("Routing", ["ip", "route"]),
        command_section("Listening TCP/UDP sockets", ["ss", "-tulpen"]),
        command_section(
            "Failed systemd units", ["systemctl", "--failed", "--no-pager"]
        ),
        ssh_section(),
        network_hardening_section(),
        command_section("nftables ruleset", ["nft", "list", "ruleset"]),
        docker_socket_section(),
        command_section(
            "Docker containers visible to current user",
            ["docker", "ps", "--format", "table {{.Names}}\\t{{.Ports}}"],
        ),
    ]

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text("\n".join(report), encoding="utf-8")

    print(f"[+] Report written to: {REPORT_FILE}")
    print("[+] Audit complete.")


if __name__ == "__main__":
    main()
