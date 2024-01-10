import hashlib
import sys

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def write_sha256_file(file_path, sha256sum):
    output_file = file_path + '.sha256sum'
    with open(output_file, 'w', newline='\n') as file:
        file.write(sha256sum + '  ' + file_path)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"usage: {__file__} <file_to_hash>")
        sys.exit(1)

    file_path = sys.argv[1]
    sha256sum = calculate_sha256(file_path)
    write_sha256_file(file_path, sha256sum)
