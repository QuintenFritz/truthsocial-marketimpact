#!/usr/bin/env bash
# init_repo.sh — initialiseer git repo, doe initial commit, en (optioneel)
# maak een GitHub repo aan via gh CLI en push.
#
# Usage:
#   ./scripts/init_repo.sh                              # alleen lokaal
#   ./scripts/init_repo.sh --remote                     # private repo aanmaken op GitHub
#   ./scripts/init_repo.sh --remote --public            # public repo
#   ./scripts/init_repo.sh --remote --name custom-name  # custom repo naam
#
# Prerequisites:
#   - git geïnstalleerd
#   - voor --remote: gh CLI (https://cli.github.com/) ingelogd via `gh auth login`

set -euo pipefail

# ----- defaults --------------------------------------------------------------
REMOTE=false
VISIBILITY="--private"
REPO_NAME=""
DEFAULT_BRANCH="main"
COMMIT_MSG="chore: initial project skeleton"

# ----- argument parsing ------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --remote)   REMOTE=true; shift ;;
        --public)   VISIBILITY="--public"; shift ;;
        --private)  VISIBILITY="--private"; shift ;;
        --name)     REPO_NAME="$2"; shift 2 ;;
        --branch)   DEFAULT_BRANCH="$2"; shift 2 ;;
        -h|--help)
            sed -n '2,13p' "$0"
            exit 0
            ;;
        *)
            echo "Onbekende flag: $1" >&2
            exit 1
            ;;
    esac
done

# ----- locate project root ---------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

if [[ -z "${REPO_NAME}" ]]; then
    REPO_NAME="$(basename "${PROJECT_ROOT}")"
fi

echo "==> Project root: ${PROJECT_ROOT}"
echo "==> Repo name:    ${REPO_NAME}"
echo "==> Branch:       ${DEFAULT_BRANCH}"
echo "==> Remote:       ${REMOTE} (${VISIBILITY/--/})"
echo

# ----- check git installed ---------------------------------------------------
if ! command -v git >/dev/null 2>&1; then
    echo "ERROR: git is niet geïnstalleerd." >&2
    exit 1
fi

# ----- git init --------------------------------------------------------------
if [[ -d .git ]]; then
    echo "==> .git bestaat al — sla 'git init' over."
else
    echo "==> git init -b ${DEFAULT_BRANCH}"
    git init -b "${DEFAULT_BRANCH}"
fi

# ----- check user.email / user.name configured -------------------------------
if [[ -z "$(git config user.email || true)" ]]; then
    echo "WARNING: git user.email is niet gezet. Set met:"
    echo "  git config --global user.email \"jou@example.com\""
fi
if [[ -z "$(git config user.name || true)" ]]; then
    echo "WARNING: git user.name is niet gezet. Set met:"
    echo "  git config --global user.name \"Jouw Naam\""
fi

# ----- initial commit --------------------------------------------------------
if git rev-parse HEAD >/dev/null 2>&1; then
    echo "==> Repo heeft al commits — sla initial commit over."
else
    echo "==> git add + commit"
    git add .
    git commit -m "${COMMIT_MSG}" || {
        echo "ERROR: commit mislukt. Check git status." >&2
        exit 1
    }
fi

# ----- GitHub remote ---------------------------------------------------------
if [[ "${REMOTE}" == "true" ]]; then
    if ! command -v gh >/dev/null 2>&1; then
        echo "ERROR: gh CLI niet gevonden. Installeer via https://cli.github.com/" >&2
        echo "       Of skip --remote en push later handmatig met 'git remote add origin <url>'." >&2
        exit 1
    fi

    if ! gh auth status >/dev/null 2>&1; then
        echo "ERROR: gh CLI niet ingelogd. Run eerst: gh auth login" >&2
        exit 1
    fi

    if git remote get-url origin >/dev/null 2>&1; then
        echo "==> origin remote bestaat al — sla 'gh repo create' over."
    else
        echo "==> gh repo create ${REPO_NAME} ${VISIBILITY} --source=. --remote=origin --push"
        gh repo create "${REPO_NAME}" \
            "${VISIBILITY}" \
            --source=. \
            --remote=origin \
            --description "Eindwerk Data Science — Truth Social posts vs S&P 500 / WTI olieprijs (Random Forest + SHAP)" \
            --push
    fi

    echo
    echo "==> Repo URL:"
    gh repo view --json url --jq .url
else
    echo "==> Skip remote setup (geen --remote flag)."
    echo "    Push later met:"
    echo "      git remote add origin git@github.com:<USER>/${REPO_NAME}.git"
    echo "      git push -u origin ${DEFAULT_BRANCH}"
fi

echo
echo "==> KLAAR. Volgende stappen:"
echo "    1. python -m venv .venv && source .venv/bin/activate"
echo "    2. pip install -e \".[dev]\""
echo "    3. pre-commit install   # als je pre-commit hooks wil"
echo "    4. pytest tests/        # smoke tests"
