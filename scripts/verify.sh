#!/usr/bin/env bash
# verify.sh — Consistency check for the repo-health-and-sync-skill repo
#
# Minimal checks for a methodology-only skill repo. No sync infrastructure,
# no reference drift checks, no script duplication checks.
set -euo pipefail

PASS=0
FAIL=0

check() {
    local label="$1"; shift
    local out rc
    out=$("$@" 2>&1) && rc=0 || rc=$?
    if [ "$rc" -eq 0 ]; then
        echo "  PASS  $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL  $label"
        echo "    command: $*"
        if [ -n "$out" ]; then
            echo "    output (first 5 lines):"
            echo "$out" | head -5 | sed 's/^/      /'
        fi
        FAIL=$((FAIL + 1))
    fi
}

status_is_clean() {
    [ -z "$1" ]
}

# Called indirectly by check(), so ShellCheck cannot resolve the call site.
# shellcheck disable=SC2317,SC2329
tree_is_clean() {
    local status
    status=$(git status --porcelain) || return
    if ! status_is_clean "$status"; then
        printf '%s\n' "$status"
        return 1
    fi
}

# --- Self-test mode ---
if [ "${1:-}" = "--self-test" ]; then
    echo "=== verify.sh --self-test ==="
    echo ""
    errors=0

    if bash -n "$0" 2>/dev/null; then
        echo "  PASS  bash syntax"
    else
        echo "  FAIL  bash syntax"
        errors=$((errors + 1))
    fi

    if status_is_clean "" && ! status_is_clean " M README.md"; then
        echo "  PASS  dirty-tree predicate"
    else
        echo "  FAIL  dirty-tree predicate"
        errors=$((errors + 1))
    fi

    # Required files (new architecture)
    for f in AGENTS.md docs/doc-standards.json README.md docs/maintaining.md \
             evals/cases/repo-health-scan.json \
             scripts/check-trust.py \
             skills/repo-health-scan/SKILL.md; do
        if [ -f "$f" ]; then
            echo "  PASS  $f exists"
        else
            echo "  FAIL  $f not found"
            errors=$((errors + 1))
        fi
    done

    if command -v shellcheck >/dev/null 2>&1; then
        if shellcheck "$0" >/dev/null 2>&1; then
            echo "  PASS  self shellcheck"
        else
            echo "  INFO  self shellcheck warnings (non-fatal)"
        fi
    else
        echo "  INFO  shellcheck not available, skip"
    fi

    echo ""
    if [ "$errors" -eq 0 ]; then
        echo "  verify.sh: OK"
    else
        echo "  $errors self-test failure(s)"
    fi
    exit "$errors"
fi

echo "=== verify.sh: self-consistency check ==="
echo ""

check "Tree is clean" tree_is_clean

check "Self-test: doc audit" python3 scripts/doc-audit.py --self-test
check "Eval contract" python3 scripts/validate-evals.py
check "Security and trust contract" python3 scripts/check-trust.py
check "Version consistency" python3 scripts/check-version-consistency.py

# Shellcheck on all .sh files
sh_count=$(find . -name '*.sh' -not -path './.git/*' | wc -l)
if [ "$sh_count" -gt 0 ]; then
    err=0
    while IFS= read -r -d '' f; do
        if ! shellcheck "$f" >/dev/null 2>&1; then
            echo "  SC_FAIL $f"
            err=$((err + 1))
        fi
    done < <(find . -name '*.sh' -not -path './.git/*' -print0)
    if [ "$err" -eq 0 ]; then
        echo "  PASS  shellcheck: $sh_count file(s) clean"
        PASS=$((PASS + 1))
    else
        echo "  FAIL  shellcheck: $err file(s) with issues"
        FAIL=$((FAIL + 1))
    fi
else
    echo "  PASS  shellcheck: no .sh files to check"
    PASS=$((PASS + 1))
fi

# No stale refs to deleted doc files
stale=0
for old in PLAN PROPOSALS REPORT USER-SUGGESTIONS; do
    if grep -rn --include='*.md' "${old}\\.md" . 2>/dev/null \
        | grep -v '.git/' \
        | grep -v 'docs/decisions.md' \
        | grep -v 'docs/research.md' \
        | grep -q .; then
        echo "  STALE  reference to ${old}.md found"
        stale=$((stale + 1))
    fi
done
if [ "$stale" -eq 0 ]; then
    echo "  PASS  No stale refs to deleted docs"
    PASS=$((PASS + 1))
else
    echo "  FAIL  $stale stale reference(s)"
    FAIL=$((FAIL + stale))
fi

# Documentation audit
echo ""
echo "=== Documentation audit ==="
echo ""
python3 scripts/doc-audit.py
doc_exit=$?
if [ "$doc_exit" -eq 0 ]; then
    PASS=$((PASS + 1))
else
    FAIL=$((FAIL + 1))
fi

echo ""
echo "--- Summary: $PASS pass, $FAIL fail ---"
exit "$FAIL"
