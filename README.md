# OpenPDF ProjectS

A security-focused Text-to-PDF engine that builds PDF 1.4 documents from scratch and applies 128-bit AES encryption.

## Installation

```bash
pip install openpdf
```

## Usage

You can use it directly from your terminal:

```bash
openpdf --text input.txt --out secure.pdf --password "your-password"
```

## Features
- Standalone PDF object generation.
- AES-128 Encryption support.
- Automatic pagination and text wrapping.
- Zero external font dependencies (uses native Helvetica).