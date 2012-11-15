from testrunner import VdsmTestCase as TestCaseBase
import supervdsm
import testValidation
import tempfile
from vdsm import utils
import os


def getNeededPythonPath():
    testDir = os.path.dirname(__file__)
    base = os.path.dirname(testDir)
    vdsmPath = os.path.join(base, 'vdsm')
    cliPath = os.path.join(base, 'vdsm_cli')
    yield [base, vdsmPath, cliPath]


class TestSuperVdsm(TestCaseBase):
    def setUp(self):
        supervdsm.extraPythonPathList = getNeededPythonPath().next()
        testValidation.checkSudo(['python', supervdsm.SUPERVDSM])
        self._proxy = supervdsm.getProxy()

        # temporary values to run temporary svdsm
        self.pidfd, pidfile = tempfile.mkstemp()
        self.timefd, timestamp = tempfile.mkstemp()
        self.addfd, address = tempfile.mkstemp()

        self._proxy.setIPCPaths(pidfile, timestamp, address)

    def tearDown(self):
        supervdsm.extraPythonPathList = []
        for fd in (self.pidfd, self.timefd, self.addfd):
            os.close(fd)
        self._proxy.kill()  # cleanning old temp files

    def testIsSuperUp(self):
        self._proxy.ping()  # this call initiate svdsm
        self.assertTrue(self._proxy.isRunning())

    def testKillSuper(self):
        self._proxy.ping()
        self._proxy.kill()
        self.assertFalse(self._proxy.isRunning())
        self._proxy.ping()  # Launching vdsm after kill
        self.assertTrue(self._proxy.isRunning())

    def testNoPidFile(self):
        self._proxy.ping()  # svdsm is up
        self.assertTrue(self._proxy.isRunning())
        utils.rmFile(self._proxy.timestamp)
        self.assertRaises(IOError, self._proxy.isRunning)
