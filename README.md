# ASCII Magic

## Fork Notice

This is a fork of [Leandro Barone's](https://github.com/LeandroBarone/python-ascii_magic).

Besides deleting most things (things I think shouldn't appear in a library),
I separated the code into two layers: the transformation layer and the representation layer.
For backwards compatibility (and, for convenience in my code), the `to_terminal` combines both.

P.S. old annotation grammar is mostly eliminated, and Python 3.6 compatibility is disrespected;
Python 3.6 has been dead for more than 4 years anyway (end-of-life on 2021-12-23).

## API 

See original repo for API reference, but take care what I've omitted;
`to_terminal` doesn't automatically prints here.

# Licence

Copyright (c) 2020 Leandro Barone.

Usage is provided under the MIT License. See LICENSE for the full details.
