"""Data ingestion entry point.

CLI cho P4 — B1: subcommand "comments" (nut "Cap nhat du lieu moi": batch
comments -> LLM extract -> engine -> runs/queue.jsonl).

Chay tu goc repo:
    python backend/scripts/ingest_data.py comments data/fixtures/comments_batch_1.json --provider gemini
"""

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    """Diem vao CLI ingest du lieu.

    Args:
        argv (list[str] | None): Tham so dong lenh; None de argparse
            tu doc sys.argv.

    Returns:
        int: 0 khi thanh cong, 1 khi loi (file thieu, KG da freeze,
            provider fail).
    """
    parser = argparse.ArgumentParser(description="Ingest du lieu: comments -> queue")
    subparsers = parser.add_subparsers(dest="command", required=True)

    comments_parser = subparsers.add_parser("comments", help="Cap nhat du lieu moi -> queue.jsonl")
    comments_parser.add_argument("batch_path", help="Duong dan file comments_batch_N.json")
    comments_parser.add_argument("--provider", choices=["gemini", "groq", "openrouter"], default="gemini")
    comments_parser.add_argument("--queue", default="runs/queue.jsonl")

    args = parser.parse_args(argv)

    from backend.legal_radar.pipeline import CommentIngestor
    from backend.legal_radar.providers import GeminiProvider, GroqProvider, OpenRouterProvider

    if args.provider == "gemini":
        provider = GeminiProvider()
    elif args.provider == "groq":
        provider = GroqProvider()
    else:
        provider = OpenRouterProvider()

    try:
        appended = CommentIngestor(provider, args.queue).run_batch(args.batch_path)
    except FileNotFoundError as exc:
        print(f"LOI: {exc}", file=sys.stderr)
        return 1
    print(f"Da them {appended} item moi vao {args.queue}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
