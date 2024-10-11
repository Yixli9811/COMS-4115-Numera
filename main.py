import sys
import tokenizer.scanner as scanner

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <input_file>")
        sys.exit(1)

    file = sys.argv[1]

    try:
        with open(file, 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File {file} not found.")
        sys.exit(1)

    result = scanner.scan(file)
    for token in result:
        print(token)

if __name__ == "__main__":
    main()
