#!/usr/bin/env bash
#
# Deploy pipeline: lint, test, ingest, and publish the skill.
# Usage: ./scripts/deploy.sh [--target local|staging|prod]
#

set -euo pipefail

TARGET="${1:-local}"
SKILL_NAME="${SKILL_NAME:-unknown}"

echo "=== AI Skill Deployment ==="
echo "Skill: $SKILL_NAME | Target: $TARGET"
echo ""

# ── Lint ──────────────────────────────────────────
echo "[1/4] Linting Python sources ..."
ruff check scripts/ tests/ --quiet && echo "  OK" || echo "  WARN"

# ── Test ──────────────────────────────────────────
echo "[2/4] Running regression suite ..."
python scripts/evaluate_output.py && echo "  OK" || {
    echo "  FAIL – aborting deployment."
    exit 1
}

# ── Ingest docs ───────────────────────────────────
echo "[3/4] Re-indexing knowledge base ..."
python scripts/ingest_docs.py && echo "  OK" || {
    echo "  FAIL – aborting deployment."
    exit 1
}

# ── Publish ───────────────────────────────────────
echo "[4/4] Publishing to $TARGET ..."
case "$TARGET" in
    local)
        echo "  No remote push required (local)."
        ;;
    staging|prod)
        DEPLOY_ENDPOINT="${DEPLOY_ENDPOINT:-http://localhost:8000}"
        echo "  Deploying to $DEPLOY_ENDPOINT ..."
        # curl -X POST "$DEPLOY_ENDPOINT/deploy" -H "Content-Type: application/json" -d "{...}"
        echo "  OK (dry-run – uncomment curl line for real deployment)"
        ;;
    *)
        echo "  ERROR: unknown target '$TARGET'"
        exit 1
        ;;
esac

echo ""
echo "=== Deployment complete ==="
