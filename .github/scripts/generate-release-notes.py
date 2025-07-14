#!/usr/bin/env python3
"""Generate release notes from git commits and pull requests."""

import os
import re
import subprocess
import sys
from datetime import datetime


def get_commits_since_last_tag():
    """Get all commits since the last tag."""
    try:
        # Get the last tag
        last_tag = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0", "HEAD^"],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
    except subprocess.CalledProcessError:
        # No previous tags, get all commits
        last_tag = ""
    
    if last_tag:
        commit_range = f"{last_tag}..HEAD"
    else:
        commit_range = "HEAD"
    
    # Get commits
    commits = subprocess.check_output(
        ["git", "log", commit_range, "--pretty=format:%H|%s|%b"],
        text=True
    ).strip().split('\n')
    
    return commits if commits != [''] else []


def categorize_commits(commits):
    """Categorize commits based on conventional commit format."""
    categories = {
        'breaking': [],
        'features': [],
        'fixes': [],
        'docs': [],
        'style': [],
        'refactor': [],
        'perf': [],
        'test': [],
        'build': [],
        'ci': [],
        'chore': [],
        'other': []
    }
    
    for commit in commits:
        if not commit:
            continue
            
        parts = commit.split('|', 2)
        if len(parts) < 2:
            continue
            
        commit_hash = parts[0][:7]
        subject = parts[1]
        body = parts[2] if len(parts) > 2 else ""
        
        # Check for breaking changes
        if 'BREAKING CHANGE' in body or 'BREAKING-CHANGE' in body:
            categories['breaking'].append(f"{subject} ({commit_hash})")
            continue
        
        # Categorize by conventional commit type
        if subject.startswith('feat:') or subject.startswith('feature:'):
            categories['features'].append(f"{subject[5:].strip()} ({commit_hash})")
        elif subject.startswith('fix:'):
            categories['fixes'].append(f"{subject[4:].strip()} ({commit_hash})")
        elif subject.startswith('docs:'):
            categories['docs'].append(f"{subject[5:].strip()} ({commit_hash})")
        elif subject.startswith('style:'):
            categories['style'].append(f"{subject[6:].strip()} ({commit_hash})")
        elif subject.startswith('refactor:'):
            categories['refactor'].append(f"{subject[9:].strip()} ({commit_hash})")
        elif subject.startswith('perf:'):
            categories['perf'].append(f"{subject[5:].strip()} ({commit_hash})")
        elif subject.startswith('test:'):
            categories['test'].append(f"{subject[5:].strip()} ({commit_hash})")
        elif subject.startswith('build:'):
            categories['build'].append(f"{subject[6:].strip()} ({commit_hash})")
        elif subject.startswith('ci:'):
            categories['ci'].append(f"{subject[3:].strip()} ({commit_hash})")
        elif subject.startswith('chore:'):
            categories['chore'].append(f"{subject[6:].strip()} ({commit_hash})")
        else:
            categories['other'].append(f"{subject} ({commit_hash})")
    
    return categories


def generate_release_notes():
    """Generate release notes."""
    # Get current version from tag
    current_tag = os.environ.get('GITHUB_REF_NAME', 'v0.1.0')
    version = current_tag.lstrip('v')
    date = datetime.now().strftime('%Y-%m-%d')
    
    commits = get_commits_since_last_tag()
    categories = categorize_commits(commits)
    
    # Generate release notes
    notes = [f"## {version} - {date}\n"]
    
    if categories['breaking']:
        notes.append("### ⚠️ BREAKING CHANGES\n")
        for item in categories['breaking']:
            notes.append(f"* {item}")
        notes.append("")
    
    if categories['features']:
        notes.append("### ✨ Features\n")
        for item in categories['features']:
            notes.append(f"* {item}")
        notes.append("")
    
    if categories['fixes']:
        notes.append("### 🐛 Bug Fixes\n")
        for item in categories['fixes']:
            notes.append(f"* {item}")
        notes.append("")
    
    if categories['perf']:
        notes.append("### ⚡ Performance Improvements\n")
        for item in categories['perf']:
            notes.append(f"* {item}")
        notes.append("")
    
    if categories['docs']:
        notes.append("### 📚 Documentation\n")
        for item in categories['docs']:
            notes.append(f"* {item}")
        notes.append("")
    
    # Add other categories if they have items
    other_sections = []
    for cat in ['refactor', 'test', 'build', 'ci', 'style', 'chore', 'other']:
        if categories[cat]:
            other_sections.extend(categories[cat])
    
    if other_sections:
        notes.append("### 🔧 Other Changes\n")
        for item in other_sections:
            notes.append(f"* {item}")
        notes.append("")
    
    # Add links
    notes.append(f"\n**Full Changelog**: https://github.com/yourusername/coda-mcp-server/compare/...{current_tag}")
    
    return '\n'.join(notes)


if __name__ == "__main__":
    print(generate_release_notes())