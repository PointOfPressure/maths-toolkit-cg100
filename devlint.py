import ast
import os
import sys

DEVICE_FILES = [
    "maths.py", "casui.py", "casutil.py", "caslex.py", "caseng.py",
    "casrender.py", "cascalc.py", "caspoly.py",
    "vcplx.py", "matrix.py", "vectors.py", "polyroots.py", "series.py",
    "hyper.py", "polar.py", "diffeq.py", "fmmech.py", "fmstat.py",
    "numeric.py", "algos.py", "xpure.py", "fpt.py",
    "pure640.py", "purecalc.py", "stat640.py", "mech640.py", "proof.py",
    "calib_screen.py", "fontmetrics.py", "fontmetrics2.py", "keyprobe.py",
    "hwcheck.py",
]

# measured on device by hwcheck.py 2026-08-09; adding a name claims hardware has it
MATH_OK = set([
    "e", "pi", "sqrt", "pow", "exp", "log", "log10",
    "sin", "cos", "tan", "asin", "acos", "atan", "atan2",
    "sinh", "cosh", "tanh",
    "ceil", "floor", "fabs", "fmod", "modf", "frexp", "ldexp",
])

IMPORT_OK = set(["math", "random", "casioplot"])

BUILTIN_BAD = set([
    "compile", "vars", "breakpoint", "memoryview", "frozenset",
    "classmethod", "staticmethod", "bytearray", "format", "aiter", "anext",
])

METHOD_BAD = set([
    "removeprefix", "removesuffix", "casefold", "format_map", "isascii",
    "expandtabs", "maketrans", "translate", "encode", "decode",
])


class Lint(ast.NodeVisitor):
    def __init__(self, path, mods):
        self.path = path
        self.mods = mods
        self.bad = []

    def flag(self, node, msg):
        self.bad.append((self.path, getattr(node, "lineno", 0), msg))

    def visit_JoinedStr(self, n):
        self.flag(n, "f-string (not supported by MicroPython 1.9.4)")
        self.generic_visit(n)

    def visit_FormattedValue(self, n):
        self.flag(n, "f-string interpolation")
        self.generic_visit(n)

    def visit_NamedExpr(self, n):
        self.flag(n, "walrus operator :=")
        self.generic_visit(n)

    def visit_AnnAssign(self, n):
        self.flag(n, "variable annotation")
        self.generic_visit(n)

    def visit_AsyncFunctionDef(self, n):
        self.flag(n, "async def")
        self.generic_visit(n)

    def visit_Await(self, n):
        self.flag(n, "await")
        self.generic_visit(n)

    def visit_YieldFrom(self, n):
        self.flag(n, "yield from")
        self.generic_visit(n)

    def visit_MatMult(self, n):
        self.flag(n, "@ matrix-multiply operator")
        self.generic_visit(n)

    def visit_FunctionDef(self, n):
        if n.returns is not None:
            self.flag(n, "return annotation on " + n.name)
        for a in list(n.args.args) + list(n.args.kwonlyargs):
            if a.annotation is not None:
                self.flag(n, "argument annotation on " + n.name)
        self.generic_visit(n)

    def visit_Import(self, n):
        for a in n.names:
            root = a.name.split(".")[0]
            if root not in IMPORT_OK and root not in self.mods:
                self.flag(n, "import '" + a.name + "' is not available on the device")
        self.generic_visit(n)

    def visit_ImportFrom(self, n):
        root = (n.module or "").split(".")[0]
        if root not in IMPORT_OK and root not in self.mods:
            self.flag(n, "from '" + str(n.module) + "' import - not available on the device")
        self.generic_visit(n)

    def visit_Attribute(self, n):
        if isinstance(n.value, ast.Name) and n.value.id == "math":
            if n.attr not in MATH_OK:
                self.flag(n, "math." + n.attr + " does not exist in this build")
        if n.attr in METHOD_BAD:
            self.flag(n, "." + n.attr + "() is not in MicroPython 1.9.4")
        self.generic_visit(n)

    def visit_Name(self, n):
        if isinstance(n.ctx, ast.Load) and n.id in BUILTIN_BAD:
            self.flag(n, "builtin '" + n.id + "' is not in MicroPython 1.9.4")
        self.generic_visit(n)


def check_file(path, mods):
    findings = []
    raw = open(path, "rb").read()
    for i in range(len(raw)):
        if raw[i] > 127:
            line = raw[:i].count(b"\n") + 1
            findings.append((path, line, "non-ASCII byte 0x%02x" % raw[i]))
            break
    try:
        tree = ast.parse(raw.decode("ascii", "replace"), path)
    except SyntaxError as e:
        findings.append((path, e.lineno or 0, "syntax error: " + str(e.msg)))
        return findings
    lint = Lint(path, mods)
    lint.visit(tree)
    return findings + lint.bad


def run(root="."):
    mods = set(f[:-3] for f in DEVICE_FILES)
    all_bad = []
    missing = []
    for f in DEVICE_FILES:
        p = os.path.join(root, f)
        if not os.path.exists(p):
            missing.append(f)
            continue
        all_bad.extend(check_file(p, mods))
    for f in missing:
        all_bad.append((f, 0, "device file is missing"))
    return all_bad


if __name__ == "__main__":
    bad = run(os.path.dirname(os.path.abspath(__file__)) or ".")
    for path, line, msg in bad:
        print(os.path.basename(path) + ":" + str(line) + ": " + msg)
    print("devlint: " + str(len(bad)) + " problem(s) in " +
          str(len(DEVICE_FILES)) + " device files")
    sys.exit(1 if bad else 0)
