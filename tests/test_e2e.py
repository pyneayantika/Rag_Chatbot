import pytest
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.guardrails.intent_classifier import (
    is_advisory,
    contains_pii,
)
from src.retrieval.retriever import retrieve


def test_retrieve_expense_ratio():
    chunks = retrieve('expense ratio HDFC Mid Cap')
    assert len(chunks) > 0
    assert all('source_url' in c.metadata for c in chunks)
    assert all('scrape_date' in c.metadata for c in chunks)

def test_retrieve_exit_load():
    chunks = retrieve('exit load HDFC Small Cap')
    assert len(chunks) > 0

def test_retrieve_elss_lockin():
    chunks = retrieve('lock in period ELSS tax saver')
    assert len(chunks) > 0

def test_retrieve_sip_minimum():
    chunks = retrieve('minimum SIP HDFC Flexi Cap')
    assert len(chunks) > 0

def test_retrieve_benchmark():
    chunks = retrieve('benchmark index HDFC Large Cap')
    assert len(chunks) > 0

def test_advisory_invest():
    assert is_advisory(
        'should I invest in HDFC Mid Cap') == True

def test_advisory_better_fund():
    assert is_advisory('which fund is better') == True

def test_advisory_sip_grow():
    assert is_advisory('will my SIP grow') == True

def test_advisory_good_time():
    assert is_advisory(
        'is now a good time to invest') == True

def test_pii_pan_detected():
    assert contains_pii('my PAN is ABCDE1234F') == True