#!/usr/bin/env python3
"""
amazon-listing-audit CLI
Usage:
  python main.py --file inventory.csv --category health_and_beauty --output report.xlsx
  python main.py --asins B01N5IB20Q,B07XJ8C8F5 --category electronics
"""

import argparse
import sys
from src.auditor import AmazonListingAuditor


def main():
    parser = argparse.ArgumentParser(
        description="Amazon Category Listing Auditor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --file my_inventory.csv --category health_and_beauty
  python main.py --file flat_file.xlsx --category grocery --output results.xlsx
  python main.py --asins B01N5IB20Q,B07XJ8C8F5 --category electronics
        """
    )
    parser.add_argument("--file",     help="Path to CSV, XLSX, or TXT flat file")
    parser.add_argument("--asins",    help="Comma-separated list of ASINs")
    parser.add_argument("--category", default="generic",
                        help="Amazon category (e.g. health_and_beauty, grocery, electronics)")
    parser.add_argument("--output",   default="audit_report.xlsx",
                        help="Output file path (.xlsx or .csv)")
    parser.add_argument("--format",   choices=["xlsx", "csv"], default="xlsx")

    args = parser.parse_args()

    if not args.file and not args.asins:
        parser.print_help()
        sys.exit(1)

    auditor = AmazonListingAuditor(category=args.category)

    if args.file:
        print(f"📂 Loading file: {args.file}")
        df = auditor.load_file(args.file)
        print(f"   Found {len(df)} rows")
    else:
        asins = [a.strip() for a in args.asins.split(",")]
        print(f"🔍 Auditing {len(asins)} ASINs")
        df = auditor.load_asin_list(asins)

    print(f"🔎 Running audit for category: {args.category}")
    results = auditor.audit_dataframe(df)

    passed = sum(1 for r in results if r.passed)
    print(f"\n📊 Results: {passed}/{len(results)} listings passed")

    avg_score = sum(r.score for r in results) / max(len(results), 1)
    print(f"   Average score: {avg_score:.1f}/100")

    if args.format == "csv" or args.output.endswith(".csv"):
        auditor.export_csv(results, args.output)
    else:
        auditor.export_excel(results, args.output)


if __name__ == "__main__":
    main()
