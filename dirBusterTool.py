import sys
import threading
from urllib.parse import urlparse
import requests


def print_help():
    print("Usage: dirBusterTool.py [<OPTIONS>] [<target url>]")
    print("Options:")
    print("-h, --help                                    Display this help message")
    print("-v, --verbose                                 Make output more verbose")
    print("-t [<Number of threads>], --threads           Define number of threads (Default: 10)")
    print("-w [<Path to wordlist>], --wordlist           Change wordlist used (Default: directory-list-2.3-small.txt)")
    print("-e [<Extensions list>], --extensions          Change file extensions (Default: \".txt,.php\")")
    print("-r [<Recursion level>], --recursion-level     Set recursion depth level (Default: 1) - Takes a while")


def validate_url(url: str) -> False:
    try:
        parsed_url = urlparse(url)
        return all([parsed_url.scheme, parsed_url.netloc])
    except ValueError:
        return False


def directory_exists(session, url: str) -> bool:
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = session.get(url, headers=headers, timeout=2)

        if response.status_code == 200:
            return True
    except:
        return False
    return False


def bust_directory_recurse(target_url: str, dir_: str, session, verbose: bool, wordlist_path: str, extensions: list[str], recursion_level: int) -> list[str]:
    if recursion_level == 0:
        return []

    dirs_found = []

    with open(wordlist_path, "r") as wordlist_file:
        for sub_dir in wordlist_file:
            sub_dir = sub_dir.strip()

            if "#" in sub_dir or " " in sub_dir or not sub_dir:
                continue

            for extension in extensions:
                if directory_exists(session, target_url + '/' + dir_ + '/' + sub_dir + extension):
                    dirs_found.append('/' + dir_ + '/' + sub_dir + extension)
                    print("EXISTS:", target_url + '/' + dir_ + '/' + sub_dir + extension)
                elif verbose:
                    print("DOES NOT EXISTS:", target_url + '/' + dir_ + '/' + sub_dir + extension)

            if f"/{dir_}/{sub_dir}" in dirs_found:
                dirs_found.extend(bust_directory_recurse(target_url, dir_ + '/' + sub_dir, session, verbose, wordlist_path, extensions, recursion_level - 1))

    return dirs_found


def thread_operation(target_url: str, wordlist_file_main, file_lock: threading.Lock, result_lock: threading.Lock, result_list: list[str], session, verbose: bool, wordlist_path: str, extensions: list[str], recursion_level: int):
    while True:
        with file_lock:
            word = wordlist_file_main.readline().strip()

        if not word:
            break

        if "#" in word or " " in word or not word:
            continue

        if verbose:
            print(threading.current_thread().name, "busting /" + word, "upto level", recursion_level)

        dirs_found = []
        for extension in extensions:
            if directory_exists(session, target_url + '/' + word + extension):
                dirs_found.append('/' + word + extension)
                print("EXISTS:", target_url + '/' + word + extension)
            elif verbose:
                print("DOES NOT EXIST:", target_url + '/' + word + extension)

        if f"/{word}" in dirs_found:
            dirs_found.extend(bust_directory_recurse(target_url, word, session, verbose, wordlist_path, extensions, recursion_level - 1))

        with result_lock:
            result_list.extend(dirs_found)


def main():
    args = sys.argv  # parse CLI arguments
    print("Directory Buster Tool by Pranav Arun Prasath\n")

    # Set default values for arguments
    num_threads = 10
    wordlist_path = "directory-list-2.3-small.txt"
    extensions = [".txt", ".php"]
    recursion_level = 1
    verbose = False
    target_url = None

    # Check if arguments were given and exit if not
    if len(args) == 1:
        print("Error: Invalid Usage")
        print_help()
        sys.exit(1)  # Exit abnormally

    args.pop(0)  # Pop file argument

    if "-h" in args or "--help" in args:  # Handle help argument and exit
        print_help()
        sys.exit(0)

    # Parse all arguments
    # Check if target URL argument is given
    # Exit abnormally if none or too many are given
    skip = False
    for i, arg in enumerate(args):
        # Skip past already parsed arguments
        if skip:
            skip = False
            continue

        # Check if argument is target url and parse
        if "http" in arg:
            if target_url is not None:
                print("Error: Too many [<target_url>] arguments")
                sys.exit(1)
            target_url = arg
            continue

        # Handle Verbose argument
        if arg in ("-v", "--verbose"):
            verbose = True
            print("Verbose mode")
            continue

        # Split arguments given in full-form (--arg)
        arg = arg.split("=")

        # If arg is in shorthand (-a) take the value and append
        if len(arg) == 1:
            if i >= len(args) - 1:
                print(f"Error: Invalid or incomplete argument {arg[0]}")
                sys.exit(1)
            arg.append(args[i + 1])
            skip = True  # Skip next iteration as it is a value

        # Parse all different arg types and set values
        if arg[0] in ("-t", "--threads"):
            try:
                num_threads = int(arg[1].strip())
            except ValueError:
                print(f"Error: Invalid number of threads {arg[1]}")
                sys.exit(1)
            continue

        if arg[0] in ("-w", "--wordlist"):
            wordlist_path = arg[1].strip()
            continue

        if arg[0] in ("-e", "--extensions"):
            extensions = [extension.strip() for extension in arg[1].strip().split(",")]
            continue

        if arg[0] in ("-r", "--recursion-level"):
            try:
                recursion_level = int(arg[1].strip())
            except ValueError:
                print(f"Error: Invalid recursion level {arg[1]}")
                sys.exit(1)
            continue

        # If none of the above, arg is invalid
        print(f"Error: Invalid argument {arg[0]}")
        sys.exit(1)


    if not target_url:
        print("Error: No target url specified")
        sys.exit(1)

    # Validate the URL format
    if not validate_url(target_url):
        print("Error: Invalid target URL")
        sys.exit(1)

    extensions.insert(0, "")

    target_url = target_url.rstrip("/")

    print(f"Busting {target_url} upto level {recursion_level} using {wordlist_path} wordlist...")

    session = requests.Session()

    if directory_exists(session, target_url):
        print("EXISTS:", target_url)
    else:
        print("DOES NOT EXISTS:", target_url)
        sys.exit(1)

    if verbose:
        print("Creating threads...")

    thread_list = []

    file_lock = threading.Lock()
    result_lock = threading.Lock()
    result_list = [target_url]

    with open(wordlist_path) as wordlist_file:
        for i in range(num_threads):
            if verbose:
                print(f"Starting thread {i}...")
            thread = threading.Thread(name=f"thread {i}", target=thread_operation, args=(target_url, wordlist_file, file_lock, result_lock, result_list, session, verbose, wordlist_path, extensions, recursion_level))
            thread_list.append(thread)
            thread.start()

        for thread in thread_list:
            thread.join()

        if verbose:
            print("Final Result List: ")

            for dir_ in result_list:
                print(target_url + '/' + dir_)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)

