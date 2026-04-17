from __future__ import annotations
from urllib.parse import urlparse

TIER_1_GROWW = [
    "https://groww.in/mutual-funds/hdfc-mid-cap-opportunities-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
    "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
]

TIER_2_HDFC_AMC = [
    "https://www.hdfcfund.com/explore/mutual-funds/hdfc-mid-cap-fund/direct",
    "https://www.hdfcfund.com/explore/mutual-funds/hdfc-flexi-cap-fund/direct",
    "https://www.hdfcfund.com/explore/mutual-funds/hdfc-elss-tax-saver/direct",
    "https://www.hdfcfund.com/explore/mutual-funds/hdfc-large-cap-fund/direct",
    "https://www.hdfcfund.com/explore/mutual-funds/hdfc-small-cap-fund/direct",
    "https://www.hdfcfund.com/investor-services/fund-documents/sid",
    "https://www.hdfcfund.com/investor-services/fund-documents/kim",
    "https://www.hdfcfund.com/statutory-disclosure/total-expense-ratio-of-mutual-fund-schemes/notices",
]

TIER_3_AMFI = [
    "https://www.amfiindia.com/investor",
    "https://www.amfiindia.com/investor/knowledge-center-info?zoneName=CategorizationOfMutualFundSchemes",
    "https://www.amfiindia.com/articles/mutual-fund",
    "https://www.amfiindia.com/investor/knowledge-center-info?zoneName=TypesOfMutualFundSchemes",
]

TIER_4_SEBI = [
    "https://www.sebi.gov.in/legal/circulars/oct-2017/categorization-and-rationalization-of-mutual-fund-schemes_36199.html",
    "https://www.sebi.gov.in/legal/circulars/jan-2018/performance-benchmarking-of-mutual-fund-schemes_37415.html",
    "https://www.sebi.gov.in/investors/investor-charter/mutual-funds.html",
]

URLS = TIER_1_GROWW + TIER_2_HDFC_AMC + TIER_3_AMFI + TIER_4_SEBI

ALLOWED_DOMAINS = {
    "groww.in",
    "hdfcfund.com",
    "amfiindia.com",
    "sebi.gov.in",
}

def validate_url(url: str) -> None:
    hostname = urlparse(url).hostname or ""
    domain = hostname.lower().removeprefix("www.")
    if domain not in ALLOWED_DOMAINS:
        raise ValueError(
            f"URL not in allowlist: {url} (domain: {domain})"
        )
