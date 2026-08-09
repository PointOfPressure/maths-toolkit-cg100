def test_hook(h):
    h.check("the extra-test hook runs", 1 + 1, 2)
    h.truthy("the harness carries the engine modules", h.caseng is not None)
    out = h.drive(h.casui.cas_section, ["2x"], [4, -1, -1])
    h.has("drive works from an extra module", out, "2*x")

SECTIONS = [("extra-test hook", test_hook)]
