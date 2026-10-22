# The self test's stage 3 cases (selftest3.py): Statistics, Kinematics,
# Forces, three each. Copies of tests_accept.py cases.
CASES = (
    ('3 jun18 17a', 'stat', ['b(10,0.5)'], 'Test for p', ['2', '7', '10'], ['p(x>=7)=1-p(x<=6)=0.17188', 'x<=1orx>=9', 'donotrejecth0']),
    ('3 jun23 16ai', 'stat', ['n(6.5,0.73^2)'], 'P(X < x)', ['5.2'], ['p(x<5.2)=0.0374']),
    ('3 jun24 16', 'stat', [''], 'PMCC test', ['-0.45', '50', '2.5', '1'], ['0.2787', 'rejecth0']),
    ('2 jun18 10', 'kin', [''], 'SUVAT', ['', '0', '0.0128', '?', '1.8'], ['a=0.00711']),
    ('2 nov20 14a', 'kin', ['r=(t^3-5t^2)i+(8t-t^2)j'], 'At time t', ['2'], ['v(2)=-8i+4j', 'speed=4sqrt(5)']),
    ('2 jun18 12b', 'kin', ['0,4,6,11,12,13,16,20', '0,-2,2,2,0,-4,-4,0'], 'v-t graph', None, ['backatthestartatt=8,14.25']),
    ('2 jun22 19a', 'force', [''], 'Slope or surface', ['20', '25', '230', '0', '?', '1.2', '', ''], ['mu=0.693']),
    ('2 jun24 21c', 'force', [''], 'Pulley', ['50', '60', '1', '80', '', '', 'g'], ['~(11-5sqrt(3))g/26']),
    ('2 jun23 17ai', 'force', [''], 'Moments', ['m*g@3.5', '4g@1.4, y@5', ''], ['m=9.6|m=48/5']),
)
