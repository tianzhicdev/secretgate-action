# ethkey-lite-proof v1
created: 2026-08-30T20:45:54Z
signer: 0x6813Eb9362372EEF6200f3b1dbC3f819671cBA69
sha256: fda0d11f23938a09856cac8374a57970846f8adb734abe6519e5adbd98faf2c5
note: c23 negative-control fixture: GENUINE receipt by the PUBLIC throwaway key (pk=3). Signature real, signer NOT a fleet address. Passes bare verify; must fail --require against any fleet address.
signature: 0x1e874e4dc1c59f85d7fc0d6e43788ce685f081254370809ac82e7673e0abe0f06866a5332c8343f9b06bf1fdabfaefbb43891021ebae9322f844c057b6761c8d1c

Signed scope: created + sha256 fields (not the note). Re-verify with
'ethkey.py verify <this file> --require <addr>' or ethers.verifyMessage
on the canonical string:
  ethkey-lite-proof v1\ncreated:<created>\nsha256:<sha256>

-----BEGIN PAYLOAD-----
YzIzIG5lZ2F0aXZlLWNvbnRyb2wgcGF5bG9hZDogYSBHRU5VSU5FIHJlY2VpcHQg
c2lnbmVkIGJ5IHRoZSBQVUJMSUMgdGhyb3dhd2F5IGtleSAocGs9MykuIFNpZ25h
dHVyZSByZWFsLCBzaWduZXIgaXMgTk9UIGEgZmxlZXQgYWRkcmVzcy4gUGFzc2Vz
IGJhcmUgdmVyaWZ5OyBtdXN0IGZhaWwgLS1yZXF1aXJlIGFueSBmbGVldCBhZGRy
ZXNzLgo=
-----END PAYLOAD-----
