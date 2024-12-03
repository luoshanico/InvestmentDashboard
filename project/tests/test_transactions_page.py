import unittest
import pytest
from unittest.mock import MagicMock, patch, ANY, call
import pandas as pd
import streamlit as st
from pathlib import Path
import sys

# Add your project folder to sys.path
# project_path = Path(r"OneDrive/Documents/Python/InvestmentDashboard")
# sys.path.insert(0, str(project_path))

import project.transactions_page as transactions_page 
import project.db_helpers as db_helpers



class TestTransactionsPage(unittest.TestCase):

    @patch('project.db_helpers.fetch_transactions')
    @patch('project.db_helpers.fetch_assets')
    @patch('project.db_helpers.fetch_asset_id')
    @patch('project.db_helpers.insert_transaction')
    @patch('project.db_helpers.delete_transaction')
    @patch('streamlit.form_submit_button')  # Mock the button press
    def test_show_transactions_page(
            self,
            mock_form_submit_button,
            mock_delete_transaction,
            mock_insert_transaction,
            mock_fetch_asset_id,
            mock_fetch_assets,
            mock_fetch_transactions):

        # Mock database return values
        mock_fetch_transactions.return_value = [
            (1, '2023-01-01', 'AAPL', 'Apple Inc.', 'Equity', 'USD', 10),
            (2, '2023-01-02', 'MSFT', 'Microsoft Corp.', 'Equity', 'USD', 5)
        ]
        mock_fetch_assets.return_value = [
            (1, 'AAPL', 'Apple Inc.', 'Equity', 'USD'),
            (2, 'MSFT', 'Microsoft Corp.', 'Equity', 'USD')
        ]
        mock_fetch_asset_id.return_value = 1

        # Mock form inputs
        tx_date = '2023-01-01'
        num_units = 10.0  # Leave asset_id=None to trigger fetch_assets

        print("Transaction Page File Path: ", transactions_page.__file__)

        # Run the transactions page function with mocked connection and inputs
        conn = MagicMock()
        try:
            transactions_page.show_transactions_page(conn, tx_date=tx_date, asset_id=None, num_units=num_units)
        except:
            pass

        # Check if fetch_transactions is called once
        mock_fetch_transactions.assert_called_once()
        self.assertEqual(mock_fetch_transactions.call_count, 1)
        print("fetch_transactions call count: ", mock_fetch_transactions.call_count)

        # Check if fetch_assets is called once
        mock_fetch_assets.assert_called_once()
        self.assertEqual(mock_fetch_assets.call_count, 1)
        print("fetch_assets call count: ", mock_fetch_assets.call_count)

        # Simulate the form submit button being pressed
        mock_form_submit_button.return_value = True
        
        # Test insert transactions is called once with correct arguments
        mock_insert_transaction.assert_called_once_with(conn, '2023-01-01', 1, 10.0)

        print("Session state: ", st.session_state)

        # Test delete transaction on form submission
        st.session_state['delete_form'] = True
        mock_delete_transaction.assert_called_once_with(conn, 1)


if __name__ == '__main__':
    unittest.main()
