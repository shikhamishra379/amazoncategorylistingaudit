"""
Amazon Category Listing Auditor
A tool to audit Amazon product listings for completeness and category compliance.
"""

from .auditor import AmazonListingAuditor, AuditIssue, ListingAuditResult

__version__ = "1.0.0"
__author__ = "shikhamishra379"

__all__ = ["AmazonListingAuditor", "AuditIssue", "ListingAuditResult"]
