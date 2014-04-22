import parameterize
import unittest

class Dummy(object):
    pass

env = parameterize.dynamic_environment
# env needs weakref'able keys
a = Dummy()
b = Dummy()

class TestDynamicEnv(unittest.TestCase):
    def test_set_get_del(self):
        with self.assertRaises(KeyError):
            env[a]
        env[a] = 42
        self.assertEqual(env[a], 42)
        del env[a]
        with self.assertRaises(KeyError):
            env[a]
    
    def test_create(self):
        with self.assertRaises(KeyError):
            env[a]
        with env.create({a: 42}):
            self.assertEqual(env[a], 42)
            env[a] = 43
            self.assertEqual(env[a], 43)
        with self.assertRaises(KeyError):
            env[a]
    
    def test_create_set(self):
        with self.assertRaises(KeyError):
            env[a]
        with env.create({b: 42}):
            env[a] = 43
        self.assertEqual(env[a], 43)
        with self.assertRaises(KeyError):
            env[b]
        del env[a]

p1 = parameterize.Parameter(42)
p2 = parameterize.Parameter(42, int)

class TestParameter(unittest.TestCase):
    def test_get_set(self):
        self.assertEqual(p1.get(), 42)
        p1.set(50)
        self.assertEqual(p1.get(), 50)
        self.assertEqual(p2.get(), 42)
        p1.set(42)
    
    def test_get_set_sugar(self):
        with self.assertRaises(TypeError):
            p1(1, 2)
        self.assertEqual(p1(), 42)
        p1(50)
        self.assertEqual(p1(), 50)
        self.assertEqual(p2(), 42)
        p1(42)
    
    def test_converter(self):
        self.assertEqual(p1.get(), 42)
        self.assertEqual(p2.get(), 42)
        p1.set('42')
        p2.set('42')
        self.assertNotEqual(p1.get(), 42)
        self.assertEqual(p2.get(), 42)
        p1.set(42)
    
    def test_parameterize(self):
        self.assertEqual(p1.get(), 42)
        with p1.parameterize(50):
            self.assertEqual(p1.get(), 50)
            p1.set(51)
            self.assertEqual(p1.get(), 51)
        self.assertEqual(p1.get(), 42)

if __name__ == '__main__':
    unittest.main()
