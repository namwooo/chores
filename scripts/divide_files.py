import argparse
import shutil
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--input-path", type=str, dest="input_path", required=True)
parser.add_argument("--output-path", type=str, dest="output_path", required=True)
parser.add_argument("--divide-file-num", type=int, dest="divide_file_num", required=True)
args = parser.parse_args()

input_path = Path(args.input_path).expanduser()
output_path = Path(args.output_path).expanduser()
divide_file_num = args.divide_file_num

output_path.mkdir(parents=True, exist_ok=True)

file_path_list = list(map(Path, Path(input_path).rglob('*.*')))

iteration = 1
file_count = 0
for file_path in file_path_list:
    dest_dir = str(output_path) + f'/{iteration}'
    Path(dest_dir).mkdir(parents=True, exist_ok=True)
    dest_path = str(file_path).replace(str(input_path), dest_dir)

    shutil.copy(file_path, dest_path)
    file_count += 1

    if file_count % divide_file_num == 0:
        iteration += 1


