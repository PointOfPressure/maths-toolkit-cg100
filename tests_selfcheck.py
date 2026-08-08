# tests_selfcheck.py - proves the tests_*.py discovery hook in tests.py works.
# Each tests_*.py file defines SECTIONS = [(label, function)] and each function
# takes the harness object as its only argument.

def test_hook(h):
    h.check("the extra-test hook runs", 1 + 1, 2)
    h.truthy("the harness carries the engine modules", h.caseng is not None)
    # drive() must share the same input queue the tools read from, which is the
    # whole reason the harness is passed in rather than re-imported
    out = h.drive(h.casui.cas_section, ["2x"], [4, -1, -1])
    h.has("drive works from an extra module", out, "2*x")

SECTIONS = [("extra-test hook", test_hook)]
