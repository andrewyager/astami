"""Tests for AMIResponse parsing."""

import pytest
from astami import AMIResponse


class TestAMIResponse:
    """Test cases for AMIResponse parsing."""

    def test_parse_success_response(self):
        """Test parsing a successful response."""
        raw = "Response: Success\r\nActionID: 123\r\nMessage: Authentication accepted\r\n\r\n"
        response = AMIResponse.from_raw(raw)

        assert response.success is True
        assert response.response == "Success"
        assert response.action_id == "123"
        assert response.message == "Authentication accepted"

    def test_parse_error_response(self):
        """Test parsing an error response."""
        raw = "Response: Error\r\nActionID: 456\r\nMessage: Authentication failed\r\n\r\n"
        response = AMIResponse.from_raw(raw)

        assert response.success is False
        assert response.response == "Error"
        assert response.action_id == "456"
        assert response.message == "Authentication failed"

    def test_parse_command_output(self):
        """Test parsing command output."""
        raw = (
            "Response: Success\r\n"
            "ActionID: 789\r\n"
            "Message: Command output follows\r\n"
            "Output: Asterisk 18.0.0\r\n"
            "Output: Built on 2024-01-01\r\n"
            "\r\n"
        )
        response = AMIResponse.from_raw(raw)

        assert response.success is True
        assert len(response.output) == 2
        assert response.output[0] == "Asterisk 18.0.0"
        assert response.output[1] == "Built on 2024-01-01"

    def test_parse_data_fields(self):
        """Test that all fields are captured in data dict."""
        raw = (
            "Response: Success\r\n"
            "ActionID: test\r\n"
            "Channel: SIP/1000\r\n"
            "State: Up\r\n"
            "\r\n"
        )
        response = AMIResponse.from_raw(raw)

        assert response.data["Response"] == "Success"
        assert response.data["ActionID"] == "test"
        assert response.data["Channel"] == "SIP/1000"
        assert response.data["State"] == "Up"

    def test_success_property_case_insensitive(self):
        """Test that success property handles different cases."""
        raw1 = "Response: Success\r\nActionID: 1\r\n\r\n"
        raw2 = "Response: success\r\nActionID: 2\r\n\r\n"
        raw3 = "Response: SUCCESS\r\nActionID: 3\r\n\r\n"

        assert AMIResponse.from_raw(raw1).success is True
        assert AMIResponse.from_raw(raw2).success is True
        assert AMIResponse.from_raw(raw3).success is True

    def test_empty_response(self):
        """Test parsing an empty response."""
        raw = "\r\n\r\n"
        response = AMIResponse.from_raw(raw)

        assert response.success is False
        assert response.response == ""
        assert response.action_id == ""
