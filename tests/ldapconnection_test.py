import configparser
import unittest

from pyldap import LDAPDN
from pyldap import LDAPClient
import pyldap.errors

class LDAPConnectionTest(unittest.TestCase):
    """ Test LDAPConnection object. """
    def setUp(self):
        """ Set LDAP URL and open connection. """
        self.cfg = configparser.ConfigParser()
        self.cfg.read('test.ini')
        self.url = "ldap://%s:%s/%s?%s?%s" % (self.cfg["SERVER"]["host"], \
                                        self.cfg["SERVER"]["port"], \
                                        self.cfg["SERVER"]["basedn"], \
                                        self.cfg["SERVER"]["search_attr"], \
                                        self.cfg["SERVER"]["search_scope"])
        self.basedn = self.cfg["SERVER"]["basedn"]
        client = LDAPClient(self.url)
        client.set_credentials("SIMPLE", (self.cfg["SIMPLEAUTH"]["user"],
                                          self.cfg["SIMPLEAUTH"]["password"]))
        self.conn = client.connect()

    def tearDown(self):
        """ Close connection. """
        self.conn.close()
        del self.conn

    def test_bind_digest(self):
        """ Test DIGEST-MD5 connection. """
        if "DIGESTAUTH" not in self.cfg:
            self.skipTest("No digest authentication is set.")
        client = LDAPClient(self.url)
        if self.cfg["DIGESTAUTH"]["realm"] == "None":
            realm = None
        else:
            realm = self.cfg["DIGESTAUTH"]["realm"]
        client.set_credentials("DIGEST-MD5", (self.cfg["DIGESTAUTH"]["user"], \
                                        self.cfg["DIGESTAUTH"]["password"], \
                                        realm))
        try:
            conn = client.connect()
        except (pyldap.errors.ConnectionError, \
                pyldap.errors.AuthenticationError):
            self.fail()
        finally:
            self.assertNotEqual("anonymous", conn.whoami(), "Digest "
            "authentication was unsuccessful.")
            conn.close()

    def test_search(self):
        """ Test searching. """
        obj = self.conn.search(self.basedn, 2)
        self.assertIsNotNone(obj)
        self.assertEqual(obj, self.conn.search())

    def test_search_ldapdn(self):
        """ Test searching with LDAPDN object. """
        ldap_dn = LDAPDN(self.basedn)
        obj = self.conn.search(ldap_dn, 1)
        self.assertIsNotNone(obj)

    def test_search_attr(self):
        """ Test searching with given list of attributes. """
        obj = self.conn.search(self.basedn, 2, "(objectclass=person)",
                               ['cn'])[0]
        self.assertIsNotNone(obj)
        if 'cn' not in obj.keys():
            self.fail()

    def test_add_and_delete(self):
        entry = pyldap.LDAPEntry("cn=example,%s" % self.cfg["SERVER"]["basedn"])
        entry.update({"objectclass" : ["top", "inetorgperson"], "cn" : "example", "sn" : "example"})
        try:
            self.conn.add(entry)
            self.conn.delete("cn=example,%s" % self.cfg["SERVER"]["basedn"])
        except pyldap.LDAPError:
            self.fail("Add and delete new entry is failed.")

    def test_whoami(self):
        """ Test whoami. """
        obj = self.conn.whoami()
        expected_res = "dn:%s" % self.cfg["SIMPLEAUTH"]["user"]
        self.assertEqual(obj, expected_res)

    def test_tls(self):
        """ Test TLS connection. """
        if self.cfg['SERVER']['has_tls'] == 'False':
            self.skipTest("TLS is not set.")
        client = LDAPClient(self.url, True)
        client.set_cert_policy("ALLOW")
        try:
            conn = client.connect()
            conn.close()
        except:
            self.fail("TLS connection is failed")

    def test_connection_error(self):
        """ Test connection error. """
        client = LDAPClient("ldap://invalid")
        self.assertRaises(pyldap.ConnectionError, lambda : client.connect())

    def test_authentication_error(self):
        """ Test authentication error. """
        client = LDAPClient(self.url)
        client.set_credentials("SIMPLE", ("cn=wrong", "wronger"))
        self.assertRaises(pyldap.AuthenticationError, lambda : client.connect())

if __name__ == '__main__':
    unittest.main()
