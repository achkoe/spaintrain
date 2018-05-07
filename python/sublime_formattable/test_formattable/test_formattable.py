import unittest
import sys
sys.path.append("..")
from formattable import formattable


class Test(unittest.TestCase):

    def read_test_data(self, filename):
        with open(filename, 'r') as fh:
            linelist = fh.read().splitlines()
        testdict = {}
        cnt = 0
        sindex, eindex = None, None
        for index, line in enumerate(linelist):
            if line.startswith("<<DATA"):
                sindex = index
                testdict[cnt] = {}
            elif line.startswith("<<EXPECTED"):
                testdict[cnt]['data'] = '\n'.join(linelist[(sindex + 1):index])
                sindex = index
            elif line.startswith("<<END"):
                testdict[cnt]['expected'] = '\n'.join(linelist[(sindex + 1):index])
                cnt += 1
        return testdict

    def test_format(self):
        testdict = self.read_test_data("data_formattable.txt")
        for key, value in testdict.iteritems():
            status, result = formattable(value["data"])
            self.assertEqual(status, True)
            self.assertEqual(result, value["expected"])

if __name__ == '__main__':
    unittest.main()
