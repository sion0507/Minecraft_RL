"""Tiny CUDA Driver API arithmetic probe; no toolkit or model download needed."""

import ctypes as ct
import sys

# PTX is our own kernel: sum 0..4 on the GPU, then copy the integer to the CPU.
PTX = b"""
.version 8.0
.target sm_75
.address_size 64
.visible .entry sum(.param .u64 output) {
    .reg .u64 ptr;
    .reg .u32 total, index;
    .reg .pred more;
    ld.param.u64 ptr, [output];
    mov.u32 total, 0;
    mov.u32 index, 0;
loop:
    add.u32 total, total, index;
    add.u32 index, index, 1;
    setp.lt.u32 more, index, 5;
    @more bra loop;
    st.global.u32 [ptr], total;
    ret;
}
"""


def compute() -> int:
    driver = ct.CDLL("libcuda.so.1")

    def call(name: str, *args: object) -> None:
        code = getattr(driver, name)(*args)
        if code:
            raise RuntimeError(f"{name} failed with CUDA status {code}")

    device = ct.c_int()
    context, module, kernel = ct.c_void_p(), ct.c_void_p(), ct.c_void_p()
    memory = ct.c_uint64()
    call("cuInit", 0)
    call("cuDeviceGet", ct.byref(device), 0)
    call("cuCtxCreate_v2", ct.byref(context), 0, device)
    try:
        call("cuModuleLoadData", ct.byref(module), ct.create_string_buffer(PTX))
        call("cuModuleGetFunction", ct.byref(kernel), module, ct.c_char_p(b"sum"))
        call("cuMemAlloc_v2", ct.byref(memory), ct.c_size_t(ct.sizeof(ct.c_int)))
        try:
            parameters = (ct.c_void_p * 1)(ct.addressof(memory))
            call("cuLaunchKernel", kernel, 1, 1, 1, 1, 1, 1, 0, ct.c_void_p(), parameters, ct.c_void_p())
            call("cuCtxSynchronize")
            actual = ct.c_int()
            call("cuMemcpyDtoH_v2", ct.byref(actual), memory, ct.c_size_t(ct.sizeof(actual)))
            return actual.value
        finally:
            call("cuMemFree_v2", memory)
    finally:
        call("cuCtxDestroy_v2", context)


if __name__ == "__main__":
    try:
        print(compute())
    except (OSError, RuntimeError) as failure:
        print(str(failure), file=sys.stderr)
        sys.exit(1)
