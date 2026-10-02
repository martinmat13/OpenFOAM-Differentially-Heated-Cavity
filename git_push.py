#!/usr/bin/env python3
"""
Reusable Git Push Utility Script
Usage: ./git_push.py [commit message]
If no commit message is provided, you will be prompted for one.
"""

import sys
import subprocess
import os
from datetime import datetime

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def run_command(command, show_output=True):
    """Run a shell command and return its exit code and output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        if show_output and result.stdout.strip():
            print(result.stdout)
        return result.returncode, result.stdout
    except Exception as e:
        print(f"{Colors.FAIL}Error executing command '{command}': {e}{Colors.ENDC}")
        return 1, str(e)

def is_git_repo():
    """Check if the current directory is a git repository."""
    code, _ = run_command("git rev-parse --is-inside-work-tree", show_output=False)
    return code == 0

def main():
    print(f"{Colors.HEADER}{Colors.BOLD}--- Git Auto-Push Utility ---{Colors.ENDC}")

    if not is_git_repo():
        print(f"{Colors.FAIL}Error: The current directory is not a Git repository.{Colors.ENDC}")
        sys.exit(1)

    # 1. Check git status
    code, status_out = run_command("git status --porcelain", show_output=False)
    if not status_out.strip():
        print(f"{Colors.OKGREEN}Nothing to commit, working tree clean.{Colors.ENDC}")
        sys.exit(0)
    
    print(f"{Colors.OKCYAN}Changes detected:{Colors.ENDC}")
    run_command("git status -s")

    # 2. Get commit message
    if len(sys.argv) > 1:
        commit_msg = " ".join(sys.argv[1:])
    else:
        try:
            commit_msg = input(f"{Colors.BOLD}Enter commit message (leave blank for default): {Colors.ENDC}").strip()
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Aborted by user.{Colors.ENDC}")
            sys.exit(0)

    if not commit_msg:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"Auto-commit: Update files on {timestamp}"

    # 3. Add files
    print(f"\n{Colors.OKBLUE}Adding files...{Colors.ENDC}")
    code, _ = run_command("git add -A")
    if code != 0:
        print(f"{Colors.FAIL}Failed to add files.{Colors.ENDC}")
        sys.exit(1)

    # 4. Commit
    print(f"{Colors.OKBLUE}Committing with message: '{commit_msg}'...{Colors.ENDC}")
    # Escape single quotes in commit message
    safe_msg = commit_msg.replace("'", "'\\''")
    code, _ = run_command(f"git commit -m '{safe_msg}'")
    if code != 0:
        print(f"{Colors.FAIL}Commit failed.{Colors.ENDC}")
        sys.exit(1)

    # 5. Push
    print(f"{Colors.OKBLUE}Pushing to remote...{Colors.ENDC}")
    code, push_out = run_command("git push")
    
    if code == 0:
        print(f"{Colors.OKGREEN}{Colors.BOLD}Successfully pushed changes!{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}Push failed. You may need to pull first or set upstream.{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
