"""Tests for connection retry behaviour."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from astami import AMIClient, AMIError, AsyncAMIClient


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

    def test_negative_retries_raises_value_error(self):
        """Negative retries value is rejected at construction time."""
        with pytest.raises(ValueError, match="retries must be >= 0"):
            AsyncAMIClient(
                host="localhost",
                port=5038,
                username="u",
                secret="s",
                retries=-1,
            )

    def test_negative_retry_delay_raises_value_error(self):
        """Negative retry_delay value is rejected at construction time."""
        with pytest.raises(ValueError, match="retry_delay must be >= 0"):
            AsyncAMIClient(
                host="localhost",
                port=5038,
                username="u",
                secret="s",
                retry_delay=-1.0,
            )

    @pytest.mark.asyncio
    async def test_partial_connect_cleanup_on_retry(self):
        """Writer is closed if open_connection succeeds but banner read fails."""
        client = AsyncAMIClient(
            host="localhost",
            port=5038,
            username="u",
            secret="s",
            timeout=1.0,
            retries=1,
            retry_delay=0.01,
        )
        call_count = 0
        mock_writer_first = AsyncMock(spec=asyncio.StreamWriter)
        mock_writer_first.close = AsyncMock()
        mock_writer_first.wait_closed = AsyncMock(return_value=None)

        async def partial_then_succeed(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            reader = AsyncMock(spec=asyncio.StreamReader)
            writer = (
                mock_writer_first if call_count == 1 else AsyncMock(spec=asyncio.StreamWriter)
            )
            if call_count == 1:
                reader.readuntil = AsyncMock(side_effect=asyncio.TimeoutError())
            else:
                reader.readuntil = AsyncMock(
                    return_value=b"Asterisk Call Manager/6.0.0\r\n"
                )
                writer.close = AsyncMock()
                writer.wait_closed = AsyncMock(return_value=None)
            return reader, writer

        with patch("astami.client.asyncio.open_connection", side_effect=partial_then_succeed):
            await client.connect()

        assert client.connected is True
        mock_writer_first.close.assert_called_once()


class TestSyncRetryConnect:
    """Test AMIClient (sync) passes retry params to async client."""

    def test_sync_client_accepts_retry_params(self):
        """AMIClient constructor accepts retries and retry_delay."""
        client = AMIClient(
            host="localhost",
            port=5038,
            username="u",
            secret="s",
            retries=3,
            retry_delay=2.0,
        )
        assert client.retries == 3
        assert client.retry_delay == 2.0

    def test_sync_client_default_no_retry(self):
        """AMIClient defaults to retries=0 (backwards compatible)."""
        client = AMIClient(host="localhost", port=5038, username="u", secret="s")
        assert client.retries == 0
        assert client.retry_delay == 1.0

    def test_sync_client_passes_retry_to_async(self):
        """AMIClient.__enter__ passes retry params to AsyncAMIClient."""
        client = AMIClient(
            host="localhost",
            port=5038,
            username="u",
            secret="s",
            retries=2,
            retry_delay=0.5,
        )

        with patch.object(AsyncAMIClient, "connect", new_callable=AsyncMock) as mock_connect, \
             patch.object(AsyncAMIClient, "login", new_callable=AsyncMock) as mock_login:
            entered = client.__enter__()
            assert client._async_client.retries == 2
            assert client._async_client.retry_delay == 0.5
            client.__exit__(None, None, None)
