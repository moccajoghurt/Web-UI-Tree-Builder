#!/usr/bin/env python3
import os
import sys
import argparse
import shutil


def is_probably_binary(path, sample_size=2048):
    try:
        with open(path, "rb") as f:
            chunk = f.read(sample_size)
        if b"\x00" in chunk:
            return True
    except Exception:
        return True
    return False


def replace_in_file(path, old, new, encoding_list, dry_run, make_backup):
    if is_probably_binary(path):
        return 0, "binary-skip"
    original = None
    for enc in encoding_list:
        try:
            with open(path, "r", encoding=enc, errors="strict") as f:
                original = f.read()
            encoding_used = enc
            break
        except Exception:
            continue
    if original is None:
        return 0, "decode-fail"
    if old not in original:
        return 0, "no-change"
    updated = original.replace(old, new)
    if dry_run:
        return original.count(old), "would-change"
    if make_backup:
        backup_path = path + ".bak"
        if not os.path.exists(backup_path):
            try:
                shutil.copy2(path, backup_path)
            except Exception:
                pass
    try:
        with open(path, "w", encoding=encoding_used, errors="strict") as f:
            f.write(updated)
    except Exception:
        return 0, "write-fail"
    return original.count(old), "changed"


def safe_rename(old_path, new_path, dry_run):
    if old_path == new_path:
        return False, "same"
    if os.path.exists(new_path):
        return False, "target-exists"
    if dry_run:
        return True, "would-rename"
    try:
        os.rename(old_path, new_path)
        return True, "renamed"
    except Exception as e:
        return False, f"error:{e.__class__.__name__}"


def main():
    parser = argparse.ArgumentParser(
        description="Recursively replace a string in file contents, file names, and folder names."
    )
    parser.add_argument("old", help="String to replace.")
    parser.add_argument("new", help="Replacement string.")
    parser.add_argument(
        "-r",
        "--root",
        default=".",
        help="Root directory to start (default: current directory).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually perform changes (otherwise dry run).",
    )
    parser.add_argument(
        "--include-ext",
        nargs="*",
        help="Only process file contents for these extensions (e.g. .py .txt).",
    )
    parser.add_argument(
        "--exclude-ext", nargs="*", help="Skip file contents for these extensions."
    )
    parser.add_argument(
        "--no-contents", action="store_true", help="Skip file content replacements."
    )
    parser.add_argument(
        "--no-names", action="store_true", help="Skip renaming files/folders."
    )
    parser.add_argument(
        "--encoding",
        nargs="*",
        default=["utf-8", "utf-16", "latin-1"],
        help="Encodings to try in order.",
    )
    parser.add_argument(
        "--backup", action="store_true", help="Create .bak backups of modified files."
    )
    parser.add_argument(
        "--case-insensitive",
        action="store_true",
        help="Case-insensitive match (for contents & names).",
    )
    parser.add_argument(
        "--follow-links", action="store_true", help="Follow directory symlinks."
    )
    args = parser.parse_args()

    old = args.old
    new = args.new
    dry_run = not args.apply

    if args.case_insensitive:
        # For file contents: we'll do a simple case-insensitive replace by scanning.
        def ci_replace(text, old_ci, repl):
            import re

            pattern = re.compile(re.escape(old_ci), re.IGNORECASE)
            return pattern.sub(repl, text), len(pattern.findall(text))

    else:
        ci_replace = None

    include_ext = set(e.lower() for e in args.include_ext) if args.include_ext else None
    exclude_ext = (
        set(e.lower() for e in args.exclude_ext) if args.exclude_ext else set()
    )

    stats = {
        "files_content_changed": 0,
        "files_content_skipped": 0,
        "occurrences_replaced": 0,
        "file_renames": 0,
        "dir_renames": 0,
        "errors": 0,
    }

    # Collect rename operations separately? We'll do in-place bottom-up for directories to avoid path breakage.
    for root, dirs, files in os.walk(
        args.root, topdown=False, followlinks=args.follow_links
    ):
        # Never touch anything inside a .git directory (skip processing entirely)
        if ".git" in root.split(os.sep):
            continue
        # File contents & file renames
        for fname in files:
            fpath = os.path.join(root, fname)
            ext = os.path.splitext(fname)[1].lower()
            if not args.no_contents:
                if include_ext and ext not in include_ext:
                    stats["files_content_skipped"] += 1
                elif ext in exclude_ext:
                    stats["files_content_skipped"] += 1
                else:
                    if args.case_insensitive:
                        if is_probably_binary(fpath):
                            stats["files_content_skipped"] += 1
                        else:
                            # Manual CI content replace
                            try:
                                with open(fpath, "rb") as fb:
                                    raw = fb.read()
                                # try encodings
                                text = None
                                used_enc = None
                                for enc in args.encoding:
                                    try:
                                        text = raw.decode(enc)
                                        used_enc = enc
                                        break
                                    except Exception:
                                        continue
                                if text is None:
                                    stats["files_content_skipped"] += 1
                                else:
                                    new_text, count = ci_replace(text, old, new)
                                    if count > 0:
                                        if dry_run:
                                            stats["files_content_changed"] += 1
                                            stats["occurrences_replaced"] += count
                                        else:
                                            if args.backup and not os.path.exists(
                                                fpath + ".bak"
                                            ):
                                                try:
                                                    shutil.copy2(fpath, fpath + ".bak")
                                                except Exception:
                                                    pass
                                            with open(
                                                fpath, "w", encoding=used_enc
                                            ) as fw:
                                                fw.write(new_text)
                                            stats["files_content_changed"] += 1
                                            stats["occurrences_replaced"] += count
                                    else:
                                        stats["files_content_skipped"] += 1
                            except Exception:
                                stats["errors"] += 1
                    else:
                        occ, status = replace_in_file(
                            fpath, old, new, args.encoding, dry_run, args.backup
                        )
                        if status in ("changed", "would-change"):
                            stats["files_content_changed"] += 1
                            stats["occurrences_replaced"] += occ
                        else:
                            stats["files_content_skipped"] += 1

            if not args.no_names:
                target_name_source = fname
                if args.case_insensitive:
                    import re

                    pattern = re.compile(re.escape(old), re.IGNORECASE)
                    if pattern.search(target_name_source):
                        new_name = pattern.sub(new, target_name_source)
                    else:
                        new_name = target_name_source
                else:
                    new_name = target_name_source.replace(old, new)
                if new_name != target_name_source:
                    old_full = fpath
                    new_full = os.path.join(root, new_name)
                    ok, reason = safe_rename(old_full, new_full, dry_run)
                    if ok:
                        stats["file_renames"] += 1
                    elif reason.startswith("error"):
                        stats["errors"] += 1

        # Directory renames
        if not args.no_names:
            dname = os.path.basename(root)
            parent = os.path.dirname(root)
            if args.case_insensitive:
                import re

                pattern = re.compile(re.escape(old), re.IGNORECASE)
                if pattern.search(dname):
                    new_dname = pattern.sub(new, dname)
                else:
                    new_dname = dname
            else:
                new_dname = dname.replace(old, new)
            if new_dname != dname and parent:
                old_dir = root
                new_dir = os.path.join(parent, new_dname)
                ok, reason = safe_rename(old_dir, new_dir, dry_run)
                if ok:
                    stats["dir_renames"] += 1
                elif reason.startswith("error"):
                    stats["errors"] += 1

    mode = "DRY-RUN" if dry_run else "APPLIED"
    print(f"=== {mode} SUMMARY ===")
    for k, v in stats.items():
        print(f"{k}: {v}")

    if dry_run:
        print("Re-run with --apply to perform the changes.")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Use -h for help. Example:")
        print("  python rename.py OLD_STRING NEW_STRING --root . --apply")
        sys.exit(1)
    main()
