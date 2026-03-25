"""Shared fixtures for the AAkar test suite."""

import pytest
import pandas as pd


@pytest.fixture
def sample_voters_df():
    """A minimal voters DataFrame for testing."""
    return pd.DataFrame(
        {
            "epic": ["ABC1234567", "DEF7654321"],
            "name": ["Test User One", "Test User Two"],
            "age": [30, 45],
            "gender": ["Male", "Female"],
            "relation_name": ["Father Name", "Husband Name"],
            "relation_type": ["Father", "Husband"],
            "house_no": ["101", "202"],
            "assembly": ["TestAssembly", "TestAssembly"],
            "section": ["SectionA", "SectionB"],
            "booth_id": ["MH_123_001", "MH_123_002"],
        }
    )


@pytest.fixture
def sample_complaints_df():
    """A minimal complaints DataFrame for testing."""
    return pd.DataFrame(
        {
            "complaint_id": [1001, 1002],
            "epic": ["ABC1234567", "DEF7654321"],
            "issue_type": ["Water", "Electricity"],
            "timestamp": ["2025-01-01", "2025-01-02"],
            "status": ["Open", "Resolved"],
        }
    )
