from __future__ import annotations

import argparse
import json
import os
import random
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
OUT_PATH = DATA_DIR / "github_pr_metrics.csv"


def parse_github_pr_url(html_url: str) -> tuple[str, str, int] | None:
    parsed = urlparse(str(html_url))
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if parsed.netloc.lower() != "github.com" or len(parts) < 4 or parts[2] != "pull":
        return None
    try:
        return parts[0], parts[1], int(parts[3])
    except ValueError:
        return None


def load_candidates(sample: str, seed: int) -> pd.DataFrame:
    pr = pd.read_parquet(
        DATA_DIR / "pull_request.parquet",
        columns=["id", "number", "agent", "user", "user_id", "repo_id", "html_url", "created_at", "merged_at"],
    )
    pr["merged"] = pr["merged_at"].notna()

    pair_path = BASE_DIR / "results" / "author_repo_pair_volume.csv"
    if pair_path.exists():
        pair = pd.read_csv(pair_path, usecols=["user_id", "repo_id", "is_extreme_pair"])
        pair = pair.drop_duplicates(["user_id", "repo_id"])
        pr = pr.merge(pair, on=["user_id", "repo_id"], how="left")
        pr["is_extreme_pair"] = pr["is_extreme_pair"].fillna(False).astype(bool)
    else:
        pr["is_extreme_pair"] = False

    if sample == "human_linked":
        pr = pr[~pr["agent"].isin(["Devin", "Copilot"])]
    elif sample == "human_linked_no_extreme":
        pr = pr[(~pr["agent"].isin(["Devin", "Copilot"])) & (~pr["is_extreme_pair"])]
    elif sample == "no_extreme":
        pr = pr[~pr["is_extreme_pair"]]
    elif sample != "all":
        raise ValueError(f"Unknown sample: {sample}")

    return pr.sample(frac=1, random_state=seed).reset_index(drop=True)


def existing_ids(path: Path) -> set[int]:
    if not path.exists():
        return set()
    try:
        existing = pd.read_csv(path, usecols=["id"])
    except pd.errors.EmptyDataError:
        return set()
    return set(existing["id"].dropna().astype(int))


def github_get_json(owner: str, repo: str, number: int, token: str | None) -> tuple[dict, dict]:
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "aidev-research-enrichment",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers)
    with urlopen(request, timeout=30) as response:
        headers_out = dict(response.headers.items())
        payload = json.loads(response.read().decode("utf-8"))
    return payload, headers_out


def header_value(headers: dict, name: str) -> str | None:
    wanted = name.lower()
    for key, value in headers.items():
        if key.lower() == wanted:
            return value
    return None


def append_row(path: Path, row: dict) -> None:
    path.parent.mkdir(exist_ok=True)
    frame = pd.DataFrame([row])
    frame.to_csv(path, mode="a", header=not path.exists(), index=False)


def build_success_row(pr_row: pd.Series, payload: dict, headers: dict) -> dict:
    return {
        "id": int(pr_row["id"]),
        "agent": pr_row["agent"],
        "user": pr_row["user"],
        "user_id": pr_row["user_id"],
        "repo_id": pr_row["repo_id"],
        "html_url": pr_row["html_url"],
        "api_url": payload.get("url"),
        "status": "ok",
        "http_status": 200,
        "additions": payload.get("additions"),
        "deletions": payload.get("deletions"),
        "changed_files": payload.get("changed_files"),
        "commits": payload.get("commits"),
        "author_association": payload.get("author_association"),
        "draft": payload.get("draft"),
        "maintainer_can_modify": payload.get("maintainer_can_modify"),
        "github_merged": payload.get("merged"),
        "github_state": payload.get("state"),
        "rate_limit_remaining": header_value(headers, "x-ratelimit-remaining"),
        "rate_limit_reset": header_value(headers, "x-ratelimit-reset"),
        "fetched_at": pd.Timestamp.now("UTC").isoformat(),
        "error": "",
    }


def build_error_row(pr_row: pd.Series, status: str, http_status: int | None, error: str) -> dict:
    return {
        "id": int(pr_row["id"]),
        "agent": pr_row["agent"],
        "user": pr_row["user"],
        "user_id": pr_row["user_id"],
        "repo_id": pr_row["repo_id"],
        "html_url": pr_row["html_url"],
        "api_url": "",
        "status": status,
        "http_status": http_status,
        "additions": None,
        "deletions": None,
        "changed_files": None,
        "commits": None,
        "author_association": "",
        "draft": None,
        "maintainer_can_modify": None,
        "github_merged": None,
        "github_state": "",
        "rate_limit_remaining": "",
        "rate_limit_reset": "",
        "fetched_at": pd.Timestamp.now("UTC").isoformat(),
        "error": error[:500],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch GitHub PR churn metrics for AIDev PRs.")
    parser.add_argument("--limit", type=int, default=50, help="Maximum new PRs to fetch.")
    parser.add_argument(
        "--sample",
        choices=["all", "human_linked", "no_extreme", "human_linked_no_extreme"],
        default="human_linked_no_extreme",
    )
    parser.add_argument("--seed", type=int, default=404)
    parser.add_argument("--sleep", type=float, default=1.0, help="Seconds to sleep between requests.")
    parser.add_argument("--out", type=Path, default=OUT_PATH)
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    candidates = load_candidates(args.sample, args.seed)
    seen = existing_ids(args.out)
    fetched = 0

    for _, row in candidates.iterrows():
        if fetched >= args.limit:
            break
        pr_ref = parse_github_pr_url(row["html_url"])
        if pr_ref is None:
            append_row(args.out, build_error_row(row, "bad_url", None, "Could not parse GitHub PR URL"))
            fetched += 1
            continue
        if int(row["id"]) in seen:
            continue

        owner, repo, number = pr_ref
        try:
            payload, headers = github_get_json(owner, repo, number, token)
            append_row(args.out, build_success_row(row, payload, headers))
            remaining = header_value(headers, "x-ratelimit-remaining")
            print(f"ok {owner}/{repo}#{number} remaining={remaining}")
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            append_row(args.out, build_error_row(row, "http_error", exc.code, body))
            print(f"http_error {owner}/{repo}#{number} status={exc.code}")
            if exc.code in {403, 429}:
                break
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            append_row(args.out, build_error_row(row, "fetch_error", None, str(exc)))
            print(f"fetch_error {owner}/{repo}#{number}: {exc}")

        fetched += 1
        time.sleep(args.sleep + random.random() * 0.25)

    print(f"wrote {fetched} new rows to {args.out}")


if __name__ == "__main__":
    main()
