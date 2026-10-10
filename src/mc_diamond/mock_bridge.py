"""Scripted RPC backend, explicitly mock; no game or model performance claims."""

import argparse
import json
import os
import selectors
import sys

from pydantic import TypeAdapter, ValidationError

from .rpc import MAX_FRAME_BYTES
from .schema import Candidate, ErrorInfo, Identifier, Observation, RpcRequest, RpcResponse, StepResult

REQUEST_ID = TypeAdapter(Identifier)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--admin-fd", type=int, required=True)
    args = parser.parse_args()
    try:
        with open(args.fixture, encoding="utf-8") as handle:
            fixture = json.load(handle)
        initial = Observation.model_validate(fixture["initial"])
        steps = [StepResult.model_validate(step) for step in fixture["steps"]]
        if any(step.clock_mode != "mock" or any(event.source != "mock" for event in step.events) for step in steps):
            raise ValueError("mock fixture must retain mock provenance")
    except (OSError, ValueError, KeyError, TypeError):
        print("Invalid mock fixture", file=sys.stderr)
        return
    observation: Observation | None = None
    index = 0
    reader = selectors.DefaultSelector()
    reader.register(sys.stdin.fileno(), selectors.EVENT_READ, "policy")
    reader.register(args.admin_fd, selectors.EVENT_READ, "admin")
    buffers: dict[int, bytes] = {sys.stdin.fileno(): b"", args.admin_fd: b""}
    print("Mock backend; Minecraft physics and model behavior are unverified", file=sys.stderr)
    while reader.get_map():
        for key, _ in reader.select():
            chunk = os.read(key.fd, 65536)
            if not chunk:
                if key.data == "policy":
                    reader.close()
                    return
                reader.unregister(key.fd)
                continue
            buffers[key.fd] += chunk
            if len(buffers[key.fd]) > MAX_FRAME_BYTES:
                print("RPC frame too large", file=sys.stderr)
                return
            while b"\n" in buffers[key.fd]:
                line, buffers[key.fd] = buffers[key.fd].split(b"\n", 1)
                request_id = "invalid"
                try:
                    raw = json.loads(line)
                    if isinstance(raw, dict):
                        request_id = REQUEST_ID.validate_python(raw.get("request_id"), strict=True)
                    request = RpcRequest.model_validate(raw)
                    request_id = request.request_id
                    permitted = {"reset"} if key.data == "admin" else {"observe", "step"}
                    if request.method not in permitted:
                        response = RpcResponse(request_id=request_id, error=ErrorInfo(
                            code="permission_denied", message="Method forbidden on this channel"))
                    elif request.method == "reset":
                        if set(request.payload) != {"episode_id", "attempt_id"}:
                            raise ValueError("invalid reset")
                        observation = Observation.model_validate({**initial.model_dump(), **request.payload})
                        index = 0
                        response = RpcResponse(request_id=request_id, result=observation.model_dump(mode="json"))
                    elif observation is None:
                        response = RpcResponse(request_id=request_id, error=ErrorInfo(
                            code="backend_error", message="Reset required"))
                    elif request.method == "observe":
                        if request.payload:
                            raise ValueError("invalid observe")
                        response = RpcResponse(request_id=request_id, result=observation.model_dump(mode="json"))
                    else:
                        if set(request.payload) != {"candidate"}:
                            raise ValueError("invalid step")
                        candidate = Candidate.model_validate(request.payload["candidate"])
                        if candidate.source_obs_id != observation.obs_id or index >= len(steps):
                            raise ValueError("stale candidate or exhausted fixture")
                        step = steps[index].model_copy(update={"observation": steps[index].observation.model_copy(update={
                            "episode_id": observation.episode_id, "attempt_id": observation.attempt_id,
                        })})
                        observation = step.observation
                        index += 1
                        response = RpcResponse(request_id=request_id, result=step.model_dump(mode="json"))
                except (ValidationError, ValueError, TypeError):
                    response = RpcResponse(request_id=request_id, error=ErrorInfo(
                        code="invalid_request", message="Invalid request"))
                print(response.model_dump_json(), flush=True)


if __name__ == "__main__":
    main()
