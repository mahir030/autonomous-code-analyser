import os
from analyzers.entry_detector import detect_entry
from analyzers.sandbox import SandboxExecutor


class RuntimeExecutor:

    def __init__(self):
        self.executor = SandboxExecutor(timeout=3)  # 3 second hard limit

    def run_file(self, filepath):

        if not detect_entry(filepath):
            return {
                "skipped": True,
                "success": False,
                "exit_code": None,
                "runtime": 0,
                "stdout": "",
                "stderr": "No executable entry point"
            }

        ext = filepath.split(".")[-1].lower()

        if ext == "py":
            return self.executor.execute(["python3", "-I", filepath])

        elif ext == "js":
            return self.executor.execute(["node", filepath])

        elif ext == "java":
            return self._run_java(filepath)

        elif ext in ["c", "cpp"]:
            return self._run_c_cpp(filepath)

        else:
            return {
                "success": False,
                "exit_code": -1,
                "runtime": 0,
                "stdout": "",
                "stderr": "Unsupported language"
            }

    def _run_java(self, filepath):
        directory = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        classname = filename.replace(".java", "")

        compile_result = self.executor.execute(
            ["javac", filename],
            cwd=directory
        )

        if not compile_result["success"]:
            return compile_result

        return self.executor.execute(
            ["java", classname],
            cwd=directory
        )

    def _run_c_cpp(self, filepath):
        directory = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        binary_name = "temp_exec"

        compiler = "gcc" if filepath.endswith(".c") else "g++"

        compile_result = self.executor.execute(
            [compiler, filename, "-o", binary_name],
            cwd=directory
        )

        if not compile_result["success"]:
            return compile_result

        run_result = self.executor.execute(
            [f"./{binary_name}"],
            cwd=directory
        )

        try:
            os.remove(os.path.join(directory, binary_name))
        except:
            pass

        return run_result

