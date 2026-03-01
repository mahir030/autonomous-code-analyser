import resource
import signal


def set_limits(max_memory_mb=100, max_cpu_seconds=3):
    # Memory limit
    max_memory_bytes = max_memory_mb * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (max_memory_bytes, max_memory_bytes))

    # CPU time limit
    resource.setrlimit(resource.RLIMIT_CPU, (max_cpu_seconds, max_cpu_seconds))

    # Prevent fork bombs
    resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))

    # Disable core dumps
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

