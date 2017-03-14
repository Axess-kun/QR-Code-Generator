# QR Code Generator
`Just for my learning` how to create QR code.

Try to write the code `as simple as possible` to easy to understand.

### Requirements
Python 3 (Developed in Python 3.5.3)

| Plugin | URL |
| --- | --- |
| Pillow (Python Imaging Library) | https://pypi.python.org/pypi/Pillow/ |
| enum34 | https://pypi.python.org/pypi/enum34 |

##### Installation of enum34
```
pip install enum34
```
*Run in `command-line`, NOT python interpreter.

### QR Code Tutorial Documents & References
- `Mainly Tutorial >>` [Thonky] for all entire tutorials.
- [QRCODE layout](http://www.pclviewer.com/rs2/qrtopology.htm) for a little more description of module placement.
- [Reed-Solomon codes for coders](https://en.wikiversity.org/wiki/Reed%E2%80%93Solomon_codes_for_coders)
- Some optimization from [cryptogun](https://github.com/cryptogun) in [lincolnloop/python-qrcode#127](https://github.com/lincolnloop/python-qrcode/pull/127) & [nayuki/QR-Code-generator](https://github.com/nayuki/QR-Code-generator).

### Python References
- [Enum](http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python)
- [isdigit()](http://kk6.hateblo.jp/entry/20110526/1306395713) << This is why I not use isdigit() to check numeric number.
- [Accessing list through index](http://d.hatena.ne.jp/yumimue/20071205/1196839438)
- [Regular Expression #1](http://ja.pymotw.com/2/re/)
- [Regular Expression #2](https://www.tutorialspoint.com/python/python_reg_expressions.htm)

##### Notes
Most of look up table are copied from [Thonky] tables.
Then, edit in Notepad++ and copy to python file.

Each step of debugging, generated QR codes from this project are compare with [Thonky] & [RACO Industries](https://racoindustries.com/barcodegenerator/2d/qr-code/).


[//]: # (Reference links. See more infos @ http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

[Thonky]: <http://www.thonky.com/qr-code-tutorial/>
