# Directory Buster Tool

## Overview

The Directory Buster Tool is a command-line utility designed to discover directories and files on a target web server by brute-forcing directories and filenames using a wordlist. It supports multithreading and recursive searching.

## Usage

```python dirBusterTool.py [<OPTIONS>] [<target url>]```


## Options

- `-h, --help`: Display the help message.
- `-v, --verbose`: Make output more verbose.
- `-t [<Number of threads>], --threads`: Define the number of threads (Default: 10).
- `-w [<Path to wordlist>], --wordlist`: Specify the wordlist to use (Default: directory-list-2.3-small.txt).
- `-e [<Extensions list>], --extensions`: Specify file extensions to test (Default: ".txt,.php").
- `-r [<Recursion level>], --recursion-level`: Set the recursion depth level (Default: 1).
- `-o [<Path to output file>], --output`: Save the output to a specified file (Default: None).

## Example

```python dirBusterTool.py -t 20 -w custom-wordlist.txt -e .html,.asp -r 2 -o results.txt http://example.com```


## Requirements

- Python 3.x
- `requests` library

```pip install -r requirements.txt```

## Author

Pranav Arun Prasath

---