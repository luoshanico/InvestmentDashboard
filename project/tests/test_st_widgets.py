import unittest
from unittest.mock import patch
import streamlit as st

class TestStreamlitWidgets(unittest.TestCase):

    @patch('streamlit.date_input')
    @patch('streamlit.selectbox')
    @patch('streamlit.number_input')
    def test_mock_streamlit_inputs(self, mock_number_input, mock_selectbox, mock_date_input):
        # Set return values
        mock_date_input.return_value = '2023-01-01'
        mock_selectbox.return_value = 'AAPL'
        mock_number_input.return_value = 10.0

        # Simulate calls
        date = st.date_input('Transaction Date')
        asset = st.selectbox('Choose an asset', ['AAPL', 'MSFT'])
        units = st.number_input('Units', min_value=0.0, step=0.1)

        # Assertions
        self.assertEqual(date, '2023-01-01')
        self.assertEqual(asset, 'AAPL')
        self.assertEqual(units, 10.0)

if __name__ == '__main__':
    unittest.main()
