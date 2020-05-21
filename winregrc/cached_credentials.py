# -*- coding: utf-8 -*-
"""Domain cached credentials collector."""

from __future__ import unicode_literals

import codecs
import struct

from cryptography.hazmat import backends
from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.primitives.ciphers import modes
from cryptography.hazmat.primitives import ciphers
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import hmac

from winregrc import hexdump
from winregrc import interface


class CachedCredentialsKeyCollector(interface.WindowsRegistryKeyCollector):
  """Domain cached credentials key collector.

  Attributes:
  """

  _CREDENTIALS_CACHE_KEY_PATH = 'HKEY_LOCAL_MACHINE\\Security\\Cache'

  _NL_KEY_MATERIAL_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\Security\\Policy\\Secrets\\NL$KM\\CurrVal')

  _LSA_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Control\\Lsa')

  _POLICY_ENCRYPTION_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\Security\\Policy\\PolSecretEncryptionKey')

  _ODD_PARITY_TABLE = [
      1, 1, 2, 2, 4, 4, 7, 7, 8, 8, 11, 11, 13, 13, 14, 14, 16, 16, 19, 19, 21,
      21, 22, 22, 25, 25, 26, 26, 28, 28, 31, 31, 32, 32, 35, 35, 37, 37, 38,
      38, 41, 41, 42, 42, 44, 44, 47, 47, 49, 49, 50, 50, 52, 52, 55, 55, 56,
      56, 59, 59, 61, 61, 62, 62, 64, 64, 67, 67, 69, 69, 70, 70, 73, 73, 74,
      74, 76, 76, 79, 79, 81, 81, 82, 82, 84, 84, 87, 87, 88, 88, 91, 91, 93,
      93, 94, 94, 97, 97, 98, 98, 100, 100, 103, 103, 104, 104, 107, 107, 109,
      109, 110, 110, 112, 112, 115, 115, 117, 117, 118, 118, 121, 121, 122, 122,
      124, 124, 127, 127, 128, 128, 131, 131, 133, 133, 134, 134, 137, 137, 138,
      138, 140, 140, 143, 143, 145, 145, 146, 146, 148, 148, 151, 151, 152, 152,
      155, 155, 157, 157, 158, 158, 161, 161, 162, 162, 164, 164, 167, 167, 168,
      168, 171, 171, 173, 173, 174, 174, 176, 176, 179, 179, 181, 181, 182, 182,
      185, 185, 186, 186, 188, 188, 191, 191, 193, 193, 194, 194, 196, 196, 199,
      199, 200, 200, 203, 203, 205, 205, 206, 206, 208, 208, 211, 211, 213, 213,
      214, 214, 217, 217, 218, 218, 220, 220, 223, 223, 224, 224, 227, 227, 229,
      229, 230, 230, 233, 233, 234, 234, 236, 236, 239, 239, 241, 241, 242, 242,
      244, 244, 247, 247, 248, 248, 251, 251, 253, 253, 254, 254]

  def __init__(self, debug=False, output_writer=None):
    """Initializes a system key collector.

    Args:
      debug (Optional[bool]): True if debug information should be printed.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(CachedCredentialsKeyCollector, self).__init__(debug=debug)
    self._output_writer = output_writer

  def _DecryptARC4(self, key, data):
    """Decrypts ARC4 encrypted data.

    Args:
      key (str): key used to decrypt the data.
      data (bytes): data to decrypt.

    Returns:
      bytes: decrypted data.
    """
    algorithm = algorithms.ARC4(key)
    backend = backends.default_backend()
    cipher = ciphers.Cipher(algorithm, mode=None, backend=backend)
    cipher_context = cipher.decryptor()
    return cipher_context.update(data)

  def _DecryptTripleDES(self, key, data):
    """Decrypts Triple DES-ECB encrypted data.

    Args:
      key (str): key used to decrypt the data.
      data (bytes): data to decrypt.

    Returns:
      bytes: decrypted data.
    """
    algorithm = algorithms.TripleDES(key)
    mode = modes.ECB()
    backend = backends.default_backend()
    cipher = ciphers.Cipher(algorithm, mode=mode, backend=backend)
    cipher_context = cipher.decryptor()
    return cipher_context.update(data)

  def _GetBootKey(self, registry):
    """Retrieves the boot key.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.

    Returns:
      bytes: boot key or None if not found.
    """
    try:
      lsa_key = registry.GetKeyByPath(self._LSA_KEY_PATH)
    except RuntimeError:
      lsa_key = None

    if not lsa_key:
      return None

    lsa_jd_key = lsa_key.GetSubkeyByName('JD')
    lsa_skew1_key = lsa_key.GetSubkeyByName('Skew1')
    lsa_gbg_key = lsa_key.GetSubkeyByName('GBG')
    lsa_data_key = lsa_key.GetSubkeyByName('Data')

    if None in (lsa_jd_key, lsa_skew1_key, lsa_gbg_key, lsa_data_key):
      return None

    lsa_jd_class_name = lsa_jd_key.class_name
    lsa_skew1_class_name = lsa_skew1_key.class_name
    lsa_gbg_class_name = lsa_gbg_key.class_name
    lsa_data_class_name = lsa_data_key.class_name

    if None in (
        lsa_jd_class_name, lsa_skew1_class_name, lsa_gbg_class_name,
        lsa_data_class_name):
      return None

    class_name_string = ''.join([
        lsa_jd_class_name, lsa_skew1_class_name, lsa_gbg_class_name,
        lsa_data_class_name])

    scrambled_key = codecs.decode(class_name_string, 'hex')
    key = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for index, scrambled_index in enumerate([
        8, 5, 4, 2, 11, 9, 13, 3, 0, 6, 1, 12, 14, 10, 15, 7]):
      key[index] = scrambled_key[scrambled_index]

    return bytes(key)

  def _GetLSAKey(self, registry, boot_key):
    """Retrieves the LSA key.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      boot_key (bytes): boot key.

    Returns:
      bytes: LSA key or None if not found.
    """
    policy_encryption_key = registry.GetKeyByPath(
        self._POLICY_ENCRYPTION_KEY_PATH)
    if not policy_encryption_key:
      return None

    policy_encryption_value = policy_encryption_key.GetValueByName('')
    if not policy_encryption_value:
      return None

    value_data = policy_encryption_value.data

    algorithm = hashes.MD5()
    backend = backends.default_backend()
    digest_context = hashes.Hash(algorithm, backend=backend)

    digest_context.update(boot_key)

    iteration = 0
    while iteration < 1000:
      digest_context.update(value_data[60:76])
      iteration += 1

    rc4_key = digest_context.finalize()
    decrypted_data = self._DecryptARC4(rc4_key, value_data[12:60])
    return decrypted_data[16:32]

  def _GetNLKey(self, registry, lsa_key):
    """Retrieves the NL key.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      lsa_key (bytes): LSA key.

    Returns:
      bytes: NL key or None if not found.
    """
    nl_key_material_key = registry.GetKeyByPath(
        self._NL_KEY_MATERIAL_KEY_PATH)
    if not nl_key_material_key:
      return None

    nl_key_material_value = nl_key_material_key.GetValueByName('')
    if not nl_key_material_value:
      return None

    key_size = len(lsa_key)
    value_data = nl_key_material_value.data
    value_data_size = len(value_data)

    decrypted_value_data = []
    key_offset = 0
    for value_data_offset in range(12, value_data_size, 8):
      key_end_offset = key_offset + 7
      value_data_end_offset = value_data_offset + 8

      des_key = self._UnpackLSAKey(lsa_key[key_offset:key_end_offset])
      decrypted_data = self._DecryptTripleDES(
          des_key, value_data[value_data_offset:value_data_end_offset])
      decrypted_value_data.append(decrypted_data)

      key_offset = key_end_offset

      available_key_size = key_size - key_offset
      if available_key_size < 7:
        key_offset = available_key_size

    decrypted_value_data = b''.join(decrypted_value_data)
    print(hexdump.Hexdump(decrypted_value_data))

    (data_size, ) = struct.unpack('<L', decrypted_value_data[:4])
    data_size += 8

    return decrypted_value_data[8:data_size]

  def _UnpackLSAKey(self, lsa_key):
    """Unpacks 7 bytes of the LSA key as a 8-byte Triple DES decryption key.

    Args:
      lsa_key (bytes): LSA key.

    Returns:
      bytes: Triple DES decryption key.
    """
    lsa_key = bytearray(lsa_key)
    des_key = [
        lsa_key[0] >> 1,
        (lsa_key[0] & 0x01) << 6 | lsa_key[1] >> 2,
        (lsa_key[1] & 0x03) << 5 | lsa_key[2] >> 3,
        (lsa_key[2] & 0x07) << 4 | lsa_key[3] >> 4,
        (lsa_key[3] & 0x0f) << 3 | lsa_key[4] >> 5,
        (lsa_key[4] & 0x1f) << 2 | lsa_key[5] >> 6,
        (lsa_key[5] & 0x3f) << 1 | lsa_key[6] >> 7,
        lsa_key[6] & 0x7f]

    des_key = bytearray([
        self._ODD_PARITY_TABLE[value << 1] for value in des_key])

    return bytes(des_key)

  def Collect(self, registry):  # pylint: disable=arguments-differ
    """Collects system information.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.

    Returns:
      bool: True if the system key was found, False if not.
    """
    credentials_cache_key = registry.GetKeyByPath(
        self._CREDENTIALS_CACHE_KEY_PATH)
    if not credentials_cache_key:
      return False

    boot_key = self._GetBootKey(registry)
    if not boot_key:
      return False

    lsa_key = self._GetLSAKey(registry, boot_key)
    if not lsa_key:
      return False

    nl_key = self._GetNLKey(registry, lsa_key)
    if not nl_key:
      return False

    for value in credentials_cache_key.GetValues():
      if value.name == 'NL$Control':
        continue

      value_data = value.data

      algorithm = hashes.MD5()
      backend = backends.default_backend()
      hmac_context = hmac.HMAC(nl_key, algorithm, backend=backend)

      ch = value_data[64:80]
      hmac_context.update(ch)

      rc4_key = hmac_context.finalize()
      decrypted_data = self._DecryptARC4(rc4_key, value_data[96:])

      print(value.name)
      print(hexdump.Hexdump(value_data))
      print(hexdump.Hexdump(decrypted_data))

    return True
