"""Serial JSONL RPC. Administrator requests use a separate inherited pipe."""

import os
import selectors
import subprocess
import time
from types import TracebackType
from typing import Protocol

from pydantic import JsonValue, ValidationError

from .schema import Candidate, ErrorInfo, Observation, RpcRequest, RpcResponse, StepResult

MAX_FRAME_BYTES = 1_048_576


class EpisodeError(Exception):
    def __init__(self, error: ErrorInfo) -> None:
        super().__init__(error.message)
        self.error = error


class PolicyEnvironment(Protocol):
    def observe(self) -> Observation: ...
    def step(self, candidate: Candidate) -> StepResult: ...


class RpcSession:
    def __init__(self, command: list[str], timeout: float) -> None:
        self.timeout = timeout
        self.sequence = 0
        self.buffer = b""
        admin_read, self.admin_write = os.pipe()
        try:
            self.process = subprocess.Popen(
                [*command, "--admin-fd", str(admin_read)], stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=None, pass_fds=(admin_read,), bufsize=0,
            )
        except OSError:
            os.close(self.admin_write)
            raise EpisodeError(ErrorInfo(code="backend_error", message="Cannot start backend")) from None
        finally:
            os.close(admin_read)
        assert self.process.stdin is not None and self.process.stdout is not None
        self.reader = selectors.DefaultSelector()
        self.reader.register(self.process.stdout, selectors.EVENT_READ)

    def __enter__(self) -> "RpcSession":
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None,
                 traceback: TracebackType | None) -> None:
        self.reader.close()
        os.close(self.admin_write)
        if self.process.stdin:
            self.process.stdin.close()
        if self.process.poll() is None:
            self.process.terminate()
        try:
            self.process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
        if self.process.stdout:
            self.process.stdout.close()

    def _call(self, method: str, payload: dict[str, JsonValue], *, admin: bool = False) -> dict[str, JsonValue]:
        self.sequence += 1
        request = RpcRequest.model_validate({
            "request_id": str(self.sequence), "method": method, "payload": payload,
        })
        assert self.process.stdin is not None and self.process.stdout is not None
        try:
            fd = self.admin_write if admin else self.process.stdin.fileno()
            data = (request.model_dump_json() + "\n").encode()
            os.write(fd, data)
            deadline = time.monotonic() + self.timeout
            while b"\n" not in self.buffer:
                remaining = deadline - time.monotonic()
                if remaining <= 0 or not self.reader.select(remaining):
                    raise EpisodeError(ErrorInfo(code="timeout", message="RPC response timeout"))
                chunk = os.read(self.process.stdout.fileno(), 65536)
                if not chunk:
                    raise EpisodeError(ErrorInfo(code="backend_error", message="Backend exited before response"))
                self.buffer += chunk
                if len(self.buffer) > MAX_FRAME_BYTES:
                    raise EpisodeError(ErrorInfo(code="protocol_error", message="RPC frame too large"))
            line, self.buffer = self.buffer.split(b"\n", 1)
            response = RpcResponse.model_validate_json(line)
            if response.request_id != request.request_id:
                raise EpisodeError(ErrorInfo(code="protocol_error", message="RPC request ID mismatch"))
            if response.error is not None:
                # Only known error codes escape the trust boundary; remote text may contain secrets.
                raise EpisodeError(ErrorInfo(code=response.error.code, message="Backend rejected request",
                                             retryable=response.error.retryable))
            assert response.result is not None
            return response.result
        except (OSError, ValidationError):
            raise EpisodeError(ErrorInfo(code="protocol_error", message="Invalid RPC response")) from None

    def reset(self, episode_id: str, attempt_id: str) -> Observation:
        return Observation.model_validate(self._call("reset", {
            "episode_id": episode_id, "attempt_id": attempt_id,
        }, admin=True))

    def policy(self) -> "RpcPolicy":
        return RpcPolicy(self)


class RpcPolicy:
    def __init__(self, session: RpcSession) -> None:
        self._session = session

    def observe(self) -> Observation:
        return Observation.model_validate(self._session._call("observe", {}))

    def step(self, candidate: Candidate) -> StepResult:
        return StepResult.model_validate(self._session._call("step", {"candidate": candidate.model_dump(mode="json")}))
