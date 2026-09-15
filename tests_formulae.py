"""Checks for formulae.py. Run with: python3 tests_formulae.py"""

import formulae

SHEETS = formulae.SHEETS

SPOT = [
    'n(n+1)(2n+1)/6',
    'cosh^2 x - sinh^2 x = 1',
    'v = u + at',
    'np(1-p)',
    'sqrt(b^2 - 4ac)',
    'R cos(theta - alpha)',
    'sin(A+B) = sin A cos B + cos A sin B',
    'trapezium rule',
    '(1/2) h ((y0 + yn)',
    "x_(n+1) = x_n - f(x_n) / f'(x_n)",
    'a(1 - r^n) / (1 - r)',
    'for |x| < 1',
    'for -1 < x <= 1',
    'arsinh x = ln(x + sqrt(x^2 + 1))',
    '[cos theta  -sin theta; sin theta  cos theta]',
    'e^(-lambda) lambda^x / x!',
    '~ t_(n-1)',
    'sum (O - E)^2 / E',
    '3r/8 from centre',
    'Improved Euler method',
    'r = a + s b + t c',
    'A = (1/2) int r^2 d theta',
    's = int sqrt((dx/dt)^2 + (dy/dt)^2) dt',
    'ln|sec x + tan x| + c',
    'nCr = n! / (r! (n-r)!)',
]


def main():
    assert isinstance(SHEETS, list), 'SHEETS must be a list'
    assert len(SHEETS) >= 20, 'need >= 20 sheets, got ' + str(len(SHEETS))

    titles = []
    total = 0
    for item in SHEETS:
        assert isinstance(item, tuple) and len(item) == 2, 'sheet must be (title, lines)'
        title, lines = item
        assert isinstance(title, str), 'title must be a string'
        assert 0 < len(title) <= 22, 'title too long: ' + title
        assert title not in titles, 'duplicate title: ' + title
        titles.append(title)
        assert isinstance(lines, list) and lines, 'lines must be a non-empty list'
        assert len(lines) <= 24, 'sheet too long, split it: ' + title
        for line in lines:
            assert isinstance(line, str), 'line must be a string in ' + title
            assert len(line) <= 52, 'line too long in ' + title + ': ' + line
            assert line == line.rstrip(), 'trailing space in ' + title + ': ' + line
            total += 1

    blob = '\n'.join(titles)
    for title, lines in SHEETS:
        blob += '\n' + '\n'.join(lines)
    for ch in blob:
        assert ord(ch) < 128, 'non-ASCII character: ' + repr(ch)

    for needle in SPOT:
        assert needle in blob, 'missing formula: ' + needle

    print('tests_formulae: OK - ' + str(len(SHEETS)) + ' sheets, ' +
          str(total) + ' lines, ' + str(len(SPOT)) + ' spot-checks')


main()
