"""
Amazon Category Listing Auditor
Audits Amazon listings for completeness and category-specific compliance.
Supports: Seller Central CSV, Amazon Flat Files (.xlsx/.txt), ASIN lists
"""

import pandas as pd
import json
import os
import re
from dataclasses import dataclass, field
from typing import Optional


CATEGORY_RULES = {
    "health_and_beauty": {
        "required_fields": ["item_name", "brand_name", "bullet_point1", "bullet_point2",
                            "bullet_point3", "product_description", "main_image_url",
                            "ingredients", "directions", "warnings"],
        "title_max_chars": 200,
        "bullet_max_chars": 255,
        "min_images": 3,
        "a_plus_recommended": True,
    },
    "grocery": {
        "required_fields": ["item_name", "brand_name", "bullet_point1", "bullet_point2",
                            "product_description", "main_image_url", "ingredients",
                            "allergen_information", "net_content"],
        "title_max_chars": 200,
        "bullet_max_chars": 255,
        "min_images": 1,
        "a_plus_recommended": True,
    },
    "electronics": {
        "required_fields": ["item_name", "brand_name", "bullet_point1", "bullet_point2",
                            "bullet_point3", "product_description", "main_image_url",
                            "wattage", "batteries_required"],
        "title_max_chars": 200,
        "bullet_max_chars": 255,
        "min_images": 4,
        "a_plus_recommended": True,
    },
    "home_and_kitchen": {
        "required_fields": ["item_name", "brand_name", "bullet_point1", "bullet_point2",
                            "bullet_point3", "product_description", "main_image_url",
                            "material_type", "item_dimensions"],
        "title_max_chars": 200,
        "bullet_max_chars": 255,
        "min_images": 3,
        "a_plus_recommended": False,
    },
    "sporting_goods": {
        "required_fields": ["item_name", "brand_name", "bullet_point1", "bullet_point2",
                            "product_description", "main_image_url", "material_type"],
        "title_max_chars": 200,
        "bullet_max_chars": 255,
        "min_images": 2,
        "a_plus_recommended": False,
    },
    "generic": {
        "required_fields": ["item_name", "brand_name", "bullet_point1",
                            "product_description", "main_image_url"],
        "title_max_chars": 200,
        "bullet_max_chars": 255,
        "min_images": 1,
        "a_plus_recommended": False,
    },
}

COLUMN_ALIASES = {
    "title": "item_name",
    "product-name": "item_name",
    "product_title": "item_name",
    "brand": "brand_name",
    "bullet_point_1": "bullet_point1",
    "bullet_point_2": "bullet_point2",
    "bullet_point_3": "bullet_point3",
    "bullet_point_4": "bullet_point4",
    "bullet_point_5": "bullet_point5",
    "feature-bullets": "bullet_point1",
    "description": "product_description",
    "image_url": "main_image_url",
    "main-image-url": "main_image_url",
    "asin-1": "asin",
}


@dataclass
class AuditIssue:
    asin: str
    field: str
    severity: str
    message: str
    category: str = ""


@dataclass
class ListingAuditResult:
    asin: str
    title: str
    category: str
    score: int
    issues: list = field(default_factory=list)
    passed: bool = False


class AmazonListingAuditor:
    def __init__(self, category: str = "generic"):
        self.category = category.lower().replace(" ", "_").replace("&", "and")
        self.rules = CATEGORY_RULES.get(self.category, CATEGORY_RULES["generic"])

    def load_file(self, filepath: str) -> pd.DataFrame:
        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".csv":
            df = pd.read_csv(filepath, dtype=str)
        elif ext in [".xlsx", ".xls"]:
            df = self._load_flat_file_excel(filepath)
        elif ext == ".txt":
            df = pd.read_csv(filepath, sep="\t", dtype=str)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
        return self._normalize_columns(df)

    def load_asin_list(self, asins: list) -> pd.DataFrame:
        return pd.DataFrame({"asin": asins})

    def _load_flat_file_excel(self, filepath: str) -> pd.DataFrame:
        for skip in [0, 1, 2, 3]:
            try:
                df = pd.read_excel(filepath, skiprows=skip, dtype=str)
                if "item_name" in df.columns or "title" in df.columns or "asin" in df.columns:
                    return df
            except Exception:
                continue
        return pd.read_excel(filepath, dtype=str)

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = [c.strip().lower().replace(" ", "_").replace("-", "_")
                      for c in df.columns]
        rename_map = {k: v for k, v in COLUMN_ALIASES.items() if k in df.columns}
        return df.rename(columns=rename_map)

    def audit_dataframe(self, df: pd.DataFrame) -> list:
        results = []
        for _, row in df.iterrows():
            results.append(self._audit_row(row))
        return results

    def _audit_row(self, row: pd.Series) -> ListingAuditResult:
        asin = str(row.get("asin", "UNKNOWN")).strip()
        title = str(row.get("item_name", "")).strip()
        issues = []

        for field_name in self.rules["required_fields"]:
            val = str(row.get(field_name, "")).strip()
            if not val or val.lower() in ["nan", "none", ""]:
                issues.append(AuditIssue(asin=asin, field=field_name, severity="critical",
                    message=f"Missing required field: '{field_name}'", category=self.category))

        if title:
            max_chars = self.rules["title_max_chars"]
            if len(title) > max_chars:
                issues.append(AuditIssue(asin=asin, field="item_name", severity="warning",
                    message=f"Title too long ({len(title)} chars, max {max_chars})", category=self.category))
            if len(title) < 30:
                issues.append(AuditIssue(asin=asin, field="item_name", severity="warning",
                    message=f"Title too short ({len(title)} chars) - aim for 80-150", category=self.category))
            if re.search(r"[!@#$%^*=]", title):
                issues.append(AuditIssue(asin=asin, field="item_name", severity="warning",
                    message="Title contains special characters", category=self.category))

        for i in range(1, 6):
            bp_val = str(row.get(f"bullet_point{i}", "")).strip()
            if bp_val and bp_val.lower() not in ["nan", "none"]:
                if len(bp_val) > self.rules["bullet_max_chars"]:
                    issues.append(AuditIssue(asin=asin, field=f"bullet_point{i}", severity="warning",
                        message=f"Bullet {i} too long ({len(bp_val)} chars)", category=self.category))

        image_cols = [c for c in row.index if "image" in c]
        image_count = sum(1 for c in image_cols if str(row.get(c, "")).strip() not in ["", "nan", "none"])
        if image_count < self.rules["min_images"]:
            issues.append(AuditIssue(asin=asin, field="images", severity="critical",
                message=f"Only {image_count} image(s), minimum {self.rules['min_images']} required",
                category=self.category))

        if self.rules.get("a_plus_recommended"):
            aplus = str(row.get("aplus_content", row.get("enhanced_brand_content", ""))).strip()
            if not aplus or aplus.lower() in ["nan", "none", ""]:
                issues.append(AuditIssue(asin=asin, field="aplus_content", severity="info",
                    message="A+ Content not detected - recommended for this category", category=self.category))

        critical_count = sum(1 for i in issues if i.severity == "critical")
        warning_count = sum(1 for i in issues if i.severity == "warning")
        score = max(0, 100 - (critical_count * 20) - (warning_count * 5))

        return ListingAuditResult(asin=asin, title=title or "N/A", category=self.category,
            score=score, issues=issues, passed=(critical_count == 0))

    def to_dataframe(self, results: list) -> pd.DataFrame:
        rows = []
        for r in results:
            rows.append({
                "ASIN": r.asin, "Title": r.title, "Category": r.category,
                "Score": r.score, "Pass/Fail": "PASS" if r.passed else "FAIL",
                "Critical Issues": " | ".join(i.message for i in r.issues if i.severity == "critical"),
                "Warnings": " | ".join(i.message for i in r.issues if i.severity == "warning"),
                "Info": " | ".join(i.message for i in r.issues if i.severity == "info"),
                "Total Issues": len(r.issues),
            })
        return pd.DataFrame(rows)

    def export_excel(self, results: list, output_path: str):
        df = self.to_dataframe(results)
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Audit Results", index=False)
            summary = pd.DataFrame({
                "Metric": ["Total ASINs", "Passed", "Failed", "Avg Score", "Critical Issues Total"],
                "Value": [len(results), sum(1 for r in results if r.passed),
                          sum(1 for r in results if not r.passed),
                          round(sum(r.score for r in results) / max(len(results), 1), 1),
                          sum(len([i for i in r.issues if i.severity == "critical"]) for r in results)]
            })
            summary.to_excel(writer, sheet_name="Summary", index=False)
        print(f"Report saved to: {output_path}")

    def export_csv(self, results: list, output_path: str):
        self.to_dataframe(results).to_csv(output_path, index=False)
        print(f"CSV saved to: {output_path}")
