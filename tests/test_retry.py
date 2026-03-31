"""Tests for connection retry behaviour."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from astami import AMIError, AsyncAMIClient


class TestAsyncRetryConnect:
    """Test AsyncAMIClient connection retry logic."""

    @pytest.mark.asyncio
    async def test_no_retry_by_default(self):
        """With default retries=0, connect fails immediately on OSError."""
        client = AsyncAMIClient(
            host="bad.host.invalid", port=5038, username="u", secret="s", timeout=0.1
        )
        with pytest.raises(AMIError, match="Failed to connect"):
            await client.connect()

    @pytest.mark.asyncio
    async def test_retry_succeeds_on_second_attempt(self):
        """Connection succeeds after one transient failure."""
        client = AsyncAMIClient(
            host="localhost",
            port=5038,
            username="u",
            secret="s",
            timeout=1.0,
            retries=2,
            retry_delay=0.01,
        )

        call_count = 0

        async def flaky_open(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise OSError("Connection refused")
            # Return mock reader/writer
            reader = AsyncMock(spec=asyncio.StreamReader)
            writer = AsyncMock(spec=asyncio.StreamWriter)
            reader.readuntil = AsyncMock(
                return_value=b"Asterisk Call Manager/6.0.0\r\n"
            )
            writer.close = AsyncMock()
            writer.wait_closed = AsyncMock(return_value=None)
            return reader, writer

        with patch("astami.client.asyncio.open_connection", side_effect=flaky_open):
            await client.connect()

        assert client.connected is True
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_retry_exhausted_raises_ami_error(self):
        """After all retries exhausted, AMIError is raised."""
        client = AsyncAMIClient(
            host="localhost",
            port=5038,
            username="u",
            secret="s",
            timeout=1.0,
            retries=2,
            retry_delay=0.01,
        )

        async def always_fail(*args, **kwargs):
            raise OSError("Connection refused")

        with patch("astami.client.asyncio.open_connection", side_effect=always_fail):
            with pytest.raises(AMIError, match="Failed to connect"):
                await client.connect()

    @pytest.mark.asyncio
    async def test_retry_exponential_backoff(self):
        """Verify delays double each attempt."""
        client = AsyncAMIClient(
            host="localhost",
            port=5038,
            username="u",
            secret="s",
            timeout=1.0,
            retries=3,
            retry_delay=1.0,
        )
        sleep_calls = []

        async def always_fail(*args, **kwargs):
            raise OSError("Connection refused")

        async def mock_sleep(delay):
            sleep_calls.append(delay)

        with (
            patch("astami.client.asyncio.open_connection", side_effect=always_fail),
            patch("astami.client.asyncio.sleep", side_effect=mock_sleep),
        ):
            with pytest.raises(AMIError):
                await client.connect()

        assert sleep_calls == [1.0, 2.0, 4.0]

    @pytest.mark.asyncio
    async def test_retry_on_timeout(self):
        """Timeout errors also trigger retry."""
        client = AsyncAMIClient(
            host="localhost",
            port=5038,
            username="u",
            secret="s",
            timeout=0.01,
            retries=1,
            retry_delay=0.01,
        )

        call_count = 0

        async def timeout_then_succeed(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise asyncio.TimeoutError()
            reader = AsyncMock(spec=asyncio.StreamReader)
            writer = AsyncMock(spec=asyncio.StreamWriter)
            reader.readuntil = AsyncMock(
                return_value=b"Asterisk Call Manager/6.0.0\r\n"
            )
            writer.close = AsyncMock()
            writer.wait_closed = AsyncMock(return_value=None)
            return reader, writer

        with patch(
            "astami.client.asyncio.open_connection", side_effect=timeout_then_succeed
        ):
            await client.connect()

        assert client.connected is True
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_zero_retries_preserves_original_behaviour(self):
        """retries=0 means no retry attempts — same as v1.0 behaviour."""
        client = AsyncAMIClient(
            host="localhost",
            port=5038,
            username="u",
            secret="s",
            timeout=1.0,
            retries=0,
            retry_delay=0.01,
        )
        call_count = 0

        async def fail_once(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            raise OSError("Connection refused")

        with patch("astami.client.asyncio.open_connection", side_effect=fail_once):
            with pytest.raises(AMIError):
                await client.connect()

        assert call_count == 1  # No retries
