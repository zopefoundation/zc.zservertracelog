import StringIO
import string
import unittest


def fseek(f, size, search, getkey=string.strip):
    # Check first line
    key = getkey(f.readline())
    if key >= search:
        f.seek(0)
        return 0

    seen = 0
    position = 0
    seek = chunk = size / 2
    while chunk > 0:
        f.seek(seek)
        line = f.readline() # maybe incomplete
        position = f.tell()
        line = f.readline() # complete
        key = getkey(line)

        chunk /= 2

        if key >= search:
            seek -= chunk
            seen = position
        else:
            seek += chunk

    if seen and key < search:
        position = seen

    f.seek(position)
    return position


def _get_btree_args(*lines):
    content = '\n'.join(lines)
    f = StringIO.StringIO(content)
    size = len(content)
    return (f, size)


def _get_colon_key(line):
    key, x = line.split(':', 1)
    return key.strip()


class FSeekTest(unittest.TestCase):
    def test_1(self):
        f, size = _get_btree_args(
            '0',
            '1',
            '2',
            '3',
            '4',
        )

        p = fseek(f, size, '0')
        self.assertEqual(p, 0)

        f.seek(0) ; p = fseek(f, size, '1')
        self.assertEqual(p, 2)

        f.seek(0) ; p = fseek(f, size, '2')
        self.assertEqual(p, 4)

        f.seek(0) ; p = fseek(f, size, '3')
        self.assertEqual(p, 6)

        f.seek(0) ; p = fseek(f, size, '4')
        self.assertEqual(p, 8)

    def test_2(self):
        f, size = _get_btree_args(
            '0',
            '0',
            '0',
            '1',
            '1',
            '1',
            '2',
            '2',
            '2',
        )

        p = fseek(f, size, '0')
        self.assertEqual(p, 0)

        f.seek(0) ; p = fseek(f, size, '1')
        self.assertEqual(p, 6)

        f.seek(0) ; p = fseek(f, size, '2')
        self.assertEqual(p, 12)

    def test_3(self):
        f, size = _get_btree_args(
            '0: sdf asdfasd ',
            '1: dffwef',
            '2: afwefwfaf adfa sdf wef aefasdfa sdfae',
            '3: afefw',
            '4:',
        )

        p = fseek(f, size, '0')
        self.assertEqual(p, 0)

        f.seek(0) ; p = fseek(f, size, '1', _get_colon_key)
        self.assertEqual(p, 16)

        f.seek(0) ; p = fseek(f, size, '2', _get_colon_key)
        self.assertEqual(p, 26)

        f.seek(0) ; p = fseek(f, size, '3', _get_colon_key)
        self.assertEqual(p, 67)

        f.seek(0) ; p = fseek(f, size, '4', _get_colon_key)
        self.assertEqual(p, 76)


if __name__ == '__main__':
    unittest.main()
