import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import streamlit as st
import db_helpers
import transactions_page  # Replace with the actual import path for transactions_page


class TestTransactionsPage(unittest.TestCase):

    @patch('db_helpers.fetch_transactions')
    @patch('db_helpers.fetch_assets')
    @patch('db_helpers.fetch_asset_id')
    @patch('db_helpers.insert_transaction')
    @patch('db_helpers.delete_transaction')
    def test_show_transactions_page(self, mock_delete_transaction, mock_insert_transaction, mock_fetch_asset_id, mock_fetch_assets, mock_fetch_transactions):
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

        # Mocking Streamlit's rerun function with a side effect
        mock_insert_transaction.side_effect = st.experimental_rerun
        mock_delete_transaction.side_effect = st.experimental_rerun

        # Run the transactions page function with a mocked connection object
        conn = MagicMock()
        try:
            transactions_page.show_transactions_page(conn)
        except st.StreamlitAPIException:
            pass

        # Check if Streamlit displays the transactions table
        mock_fetch_transactions.assert_called_once()
        self.assertEqual(mock_fetch_transactions.call_count, 1)

        # Check if the assets dropdown is populated
        mock_fetch_assets.assert_called_once()
        self.assertEqual(mock_fetch_assets.call_count, 1)

        # Test insert transaction on form submission
        st.session_state['add_form'] = True
        try:
            transactions_page.show_transactions_page(conn)
        except st.StreamlitAPIException:
            pass
        mock_insert_transaction.assert_called_once_with(conn, '2023-01-01', 1, 10)

        # Test delete transaction on form submission
        st.session_state['delete_form'] = True
        try:
            transactions_page.show_transactions_page(conn)
        except st.StreamlitAPIException:
            pass
        mock_delete_transaction.assert_called_once_with(conn, 1)


if __name__ == '__main__':
    unittest.main()
