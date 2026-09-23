import unittest
import uuid

from app.instance import InstanceLock


class InstanceTests(unittest.TestCase):
    def test_only_one_owner_per_session(self):
        name = f"BrightnessControlTest-{uuid.uuid4()}"
        first = InstanceLock(name)
        second = InstanceLock(name)
        try:
            self.assertTrue(first.acquired)
            self.assertFalse(second.acquired)
        finally:
            second.close()
            first.close()
        third = InstanceLock(name)
        try:
            self.assertTrue(third.acquired)
        finally:
            third.close()


if __name__ == "__main__":
    unittest.main()
