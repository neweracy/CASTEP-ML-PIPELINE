# Security Policy

## Supported versions

This is a research pipeline under active development. Security-relevant fixes are
applied to the `main` branch.

| Version | Supported |
| ------- | --------- |
| 0.1.x   | ✅        |

## Reporting a vulnerability

If you discover a security issue (for example, unsafe deserialization of a
model file from an untrusted source), please report it privately using GitHub's
[private vulnerability reporting](https://github.com/neweracy/CASTEP-ML-PIPELINE/security/advisories/new)
rather than opening a public issue.

Please include a description, reproduction steps, and the potential impact. We
aim to acknowledge reports within a few days.

## Note on model files

Trained models are serialized with `joblib`/`pickle`. Only load `.pkl` model
files that you produced yourself or obtained from a trusted source, as
unpickling arbitrary files can execute code.
