#!/usr/bin/env python3
"""
发版前预检查工具

检查内容：
1. 当前版本号是否相对最近 tag 有变化
2. 本次热更新清单中新增/修改/删除了哪些文件
3. 是否存在重命名、删除或未跟踪但会被纳入热更新的文件
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from generate_update_manifest import (
    generate_manifest,
    get_previous_release_tag,
    load_manifest_from_tag,
    read_repo_config,
    read_version,
    run_git_command,
)


def get_latest_tag(base_dir: Path) -> str:
    """获取仓库中最新的版本 tag"""
    try:
        output = run_git_command(base_dir, ['tag', '--list', 'v*', '--sort=-version:refname'])
    except Exception:
        return ""

    for raw_tag in output.splitlines():
        tag = raw_tag.strip()
        if tag:
            return tag

    return ""


def build_file_map(manifest: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """将 manifest 文件列表转换成路径索引"""
    return {entry['path']: entry for entry in manifest.get('files', [])}


def get_manifest_diff(
    current_manifest: Dict[str, Any],
    previous_manifest: Dict[str, Any] | None,
) -> Tuple[List[str], List[str], List[str]]:
    """比较当前 manifest 与上一个版本 manifest 的差异"""
    current_files = build_file_map(current_manifest)
    previous_files = build_file_map(previous_manifest or {})

    new_files = sorted(path for path in current_files if path not in previous_files)
    changed_files = sorted(
        path
        for path, file_info in current_files.items()
        if path in previous_files and previous_files[path].get('md5') != file_info.get('md5')
    )
    previous_deleted = {
        entry['path']
        for entry in (previous_manifest or {}).get('deleted_files', [])
        if entry.get('path')
    }
    current_deleted = {
        entry['path']
        for entry in current_manifest.get('deleted_files', [])
        if entry.get('path')
    }
    deleted_files = sorted(current_deleted - previous_deleted)

    return new_files, changed_files, deleted_files


def get_git_name_status(base_dir: Path, base_ref: str) -> List[Tuple[str, List[str]]]:
    """读取 git diff 的 name-status 结果"""
    if not base_ref:
        return []

    try:
        output = run_git_command(base_dir, ['diff', '--name-status', '--find-renames=90%', base_ref])
    except Exception:
        return []

    results: List[Tuple[str, List[str]]] = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        parts = line.split('\t')
        if not parts:
            continue

        status = parts[0]
        paths = parts[1:]
        results.append((status, paths))

    return results


def get_untracked_files(base_dir: Path) -> List[str]:
    """获取未跟踪文件列表"""
    try:
        output = run_git_command(base_dir, ['ls-files', '--others', '--exclude-standard'])
    except Exception:
        return []

    return sorted(line.strip() for line in output.splitlines() if line.strip())


def print_section(title: str, items: List[str], limit: int = 15):
    """打印列表区块"""
    print(f"\n[{title}] {len(items)}")
    if not items:
        print("  - 无")
        return

    for item in items[:limit]:
        print(f"  - {item}")

    if len(items) > limit:
        print(f"  - ... 还有 {len(items) - limit} 项")


def main() -> int:
    base_dir = Path(__file__).parent
    current_version = read_version(base_dir)
    latest_tag = get_latest_tag(base_dir)
    previous_tag = get_previous_release_tag(base_dir, current_version)
    previous_manifest = load_manifest_from_tag(base_dir, previous_tag)
    owner, repo = read_repo_config()
    current_manifest = generate_manifest(
        base_dir,
        version=current_version,
        owner=owner,
        repo=repo,
        previous_manifest=previous_manifest,
    )

    new_files, changed_files, deleted_files = get_manifest_diff(current_manifest, previous_manifest)
    git_name_status = get_git_name_status(base_dir, latest_tag)
    renamed_files = [
        f"{paths[0]} -> {paths[1]}"
        for status, paths in git_name_status
        if status.startswith('R') and len(paths) == 2
    ]
    removed_files = [paths[0] for status, paths in git_name_status if status == 'D' and paths]
    untracked_files = get_untracked_files(base_dir)
    tracked_paths = set(build_file_map(current_manifest))
    untracked_updatable_files = sorted(path for path in untracked_files if path in tracked_paths)

    version_unchanged = bool(latest_tag and current_version == latest_tag)
    has_manifest_changes = bool(new_files or changed_files or deleted_files)

    print("发版预检查")
    print("=" * 60)
    print(f"当前版本: {current_version}")
    print(f"最新 tag: {latest_tag or '无'}")
    print(f"用于对比的上一版本 tag: {previous_tag or '无'}")
    print(f"本次将纳入热更新的文件数: {len(current_manifest.get('files', []))}")
    print(f"累计待删除文件数: {len(current_manifest.get('deleted_files', []))}")

    print_section('新增热更新文件', new_files)
    print_section('修改的热更新文件', changed_files)
    print_section('待删除的旧文件', deleted_files)
    print_section('git 检测到的重命名', renamed_files)
    print_section('git 检测到的删除', removed_files)
    print_section('未跟踪但会纳入热更新的文件', untracked_updatable_files)

    warnings: List[str] = []
    blocked: List[str] = []

    if version_unchanged and has_manifest_changes:
        blocked.append(
            f"检测到可热更新内容发生变化，但 static/version.txt 仍是 {current_version}。"
        )

    if renamed_files:
        warnings.append("存在重命名文件。热更新虽然可新增新文件，但旧文件清理仍需确认。")

    if deleted_files:
        warnings.append("存在待删除文件。请确认本次删除符合预期。")

    if untracked_updatable_files:
        warnings.append("存在未跟踪但会纳入热更新规则的文件。若不提交到 Git，Action 不会包含它们。")

    print("\n[结论]")
    if blocked:
        for item in blocked:
            print(f"  - 阻塞: {item}")
    if warnings:
        for item in warnings:
            print(f"  - 提示: {item}")
    if not blocked and not warnings:
        print("  - 可以直接发版")

    return 1 if blocked else 0


if __name__ == '__main__':
    sys.exit(main())
