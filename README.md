# 🛒 Amazon Category Listing Auditor

[![Run Audit CI](https://github.com/shikhamishra379/amazoncategorylistingaudit/actions/workflows/audit-ci.yml/badge.svg)](https://github.com/shikhamishra379/amazoncategorylistingaudit/actions/workflows/audit-ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Audit Amazon product listings for field completeness and category-specific compliance. Supports Seller Central CSV exports, Amazon flat files (.xlsx/.txt), and ASIN lists.

---

## 🔍 What It Does

Amazon listings fail for many reasons — missing required fields, titles that are too long or too short, insufficient images, or category-specific attributes left blank. This tool audits your listings row-by-row and produces a scored, actionable report.

**Key capabilities:**
- ✅ Checks all required fields per Amazon category
- ✅ Detects title length violations and special characters
- ✅ Validates bullet point character limits
- ✅ Flags missing A+ Content where category-recommended
- ✅ Scores each listing 0–100 so you can prioritize fixes
- ✅ Exports Excel report with Summary tab and per-ASIN breakdown

---

## 📦 Supported Input Formats

| Format | Description |
|--------|-------------|
| `.csv` | Seller Central inventory/business report export |
| `.xlsx` | Amazon flat file (handles metadata header rows) |
| `.txt` | Tab-delimited flat file |
| ASIN list | Comma-separated ASINs |

---

## 🗂️ Supported Categories

| Category Key | Example Use Case |
|---|---|
| `health_and_beauty` | Supplements, skincare, personal care |
| `grocery` | Food, beverages, snacks |
| `electronics` | Devices, accessories, cables |
| `home_and_kitchen` | Cookware, furniture, décor |
| `sporting_goods` | Fitness equipment, outdoor gear |
| `generic` | Any unlisted category |

---

## 🚀 Quick Start

```bash
pip install -r requirements.txt
python main.py --file my_inventory.csv --category health_and_beauty
python main.py --file flat_file.xlsx --category grocery --output report.xlsx
python main.py --asins B01N5IB20Q,B07XJ8C8F5 --category electronics
```

---

## 📁 Project Structure
