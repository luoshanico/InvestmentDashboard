import unittest
from unittest.mock import MagicMock, patch
import streamlit as st
import project.transactions_page as transactions_page 
import project.db_helpers as db_helpers



class TestTransactionsPage(unittest.TestCase):

    @patch('project.db_helpers.fetch_transactions')
    @patch('project.db_helpers.fetch_assets')
    @patch('streamlit.selectbox')
    def test_fetch_transactions(
            self,
            mock_selectbox,
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
        
        # print("Transaction Page File Path: ", transactions_page.__file__)

        # Run the transactions page function with mocked connection and inputs
        conn = MagicMock()
        try:
            transactions_page.show_transactions_page(conn)
        except:
            pass

        # Check if fetch_transactions is called once
        mock_fetch_transactions.assert_called_once()
        self.assertEqual(mock_fetch_transactions.call_count, 1)

        # Check if fetch_assets is called once
        mock_fetch_assets.assert_called_once()
        self.assertEqual(mock_fetch_assets.call_count, 1)

        # Assert that the selectbox was called with the correct options
        self.assertEqual(mock_selectbox.call_args[0][1][0], 'AAPL')
        self.assertEqual(mock_selectbox.call_args[0][1][1], 'MSFT')
        
        

    @patch('project.db_helpers.insert_transaction')
    @patch('project.db_helpers.fetch_asset_id')
    @patch('streamlit.success')
    @patch('streamlit.form_submit_button')  # Mock the button press
    def test_insert_transaction(
            self,
            mock_form_submit_button,
            mock_success,
            mock_fetch_asset_id,
            mock_insert_transaction,
            ):
        
        # Simulate the form submit button being pressed
        mock_form_submit_button.side_effect = [True, False]  # False for add, True for delete

        # Mock form inputs
        tx_date = '2023-01-01'
        num_units = 10.0
        mock_fetch_asset_id.return_value = 1
        
        # Run the transactions page function with mocked connection and inputs
        conn = MagicMock()
        try:
            transactions_page.show_transactions_page(conn, tx_date=tx_date, asset_id=None, num_units=num_units)
        except:
            pass
        
        # Test insert transactions is called once with correct arguments
        mock_insert_transaction.assert_called_once_with(conn, '2023-01-01', 1, 10.0)

        # Assert success message is displayed
        mock_success.assert_called_once_with('Transaction added successfully!')

        print("Session state: ", st.session_state)

        

    @patch('project.db_helpers.delete_transaction')
    @patch('streamlit.success')
    @patch('streamlit.form_submit_button')
    def test_delete_transaction(
            self,
            mock_form_submit_button,
            mock_success,
            mock_delete_transaction,
            ):
        
        mock_form_submit_button.side_effect = [False, True]  # False for add, True for delete

        # Run the transactions page function with mocked connection and inputs
        conn = MagicMock()
        try:
            transactions_page.show_transactions_page(conn)
        except:
            pass
        
        # Test delete transaction on form submission        
        mock_delete_transaction.assert_called_once_with(conn, 1)

        # Assert success message is displayed
        mock_success.assert_called_once_with('Transaction with ID 1 deleted successfully!')
     



if __name__ == '__main__':
    unittest.main()
