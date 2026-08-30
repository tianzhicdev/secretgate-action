# ethkey-lite-proof v1
created: 2026-08-30T20:45:54Z
signer: 0xFD4090e27C1f946Ff01a265cAa7d4ACA662acC15
sha256: bc1b6dd1e3aff0779fa64c3ed2d1bdcc4597ea401041aa7e0d521ee06f31827b
note: c23 negative-control fixture: VALID throwaway-key signature (pk=3, public) with a FORGED signer header claiming the A wallet addr (0xFD40..acC15). This file is the ATTACK sample, NOT a release receipt. CI asserts every verifier rejects it.
signature: 0x8b44ca50a74f1d4d795e9dc4f9061e2c21dfb6a5df58df742285873bb96fc2b80145b52642636978b0785813a0b901d8a679be053b4c401fcd956b285fa1bcff1b

Signed scope: created + sha256 fields (not the note). Re-verify with
'ethkey.py verify <this file> --require <addr>' or ethers.verifyMessage
on the canonical string:
  ethkey-lite-proof v1\ncreated:<created>\nsha256:<sha256>

-----BEGIN PAYLOAD-----
YzIzIG5lZ2F0aXZlLWNvbnRyb2wgcGF5bG9hZDogYSBWQUxJRCBzaWduYXR1cmUg
YnkgdGhlIFBVQkxJQyB0aHJvd2F3YXkga2V5IChwaz0zKSBzaGlwcGVkIHdpdGgg
YSBGT1JHRUQgc2lnbmVyIGhlYWRlciBjbGFpbWluZyB0aGUgQSB3YWxsZXQgYWRk
ciAoMHhGRDQwLi5hY0MxNSkuIFRoaXMgZmlsZSBpcyB0aGUgQVRUQUNLIHNhbXBs
ZSwgbm90IGEgc2VjcmV0Z2F0ZS1hY3Rpb24gcmVsZWFzZSByZWNlaXB0LiBEbyBu
b3QgdHJ1c3QgdGhlIHNpZ25lciBsaW5lLgo=
-----END PAYLOAD-----
