import os
import json
from datetime import datetime
import base64


def process_json_files(folder_path):
    indexers = []
    confs = {}
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            filepath = os.path.join(folder_path, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        indexer_data = {k: v for k, v in data.items() if k != "conf"}
                        indexers.append(indexer_data)
                        if "conf" in data:
                            domain = data["domain"].split("//")[-1].split("/")[0]
                            confs[domain] = data["conf"]
                    else:
                        print(f"Error: {filename} cannot be converted to a dictionary.")
            except UnicodeDecodeError:
                print(f"Warning: {filename} might be encoded with a different encoding than utf-8, attempting with gbk.")
                try:
                    with open(filepath, "r", encoding="gbk") as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            indexer_data = {k: v for k, v in data.items() if k != "conf"}
                            indexers.append(indexer_data)
                            if "conf" in data:
                                domain = data["domain"].split("//")[-1].split("/")[0]
                                confs[domain] = data["conf"]
                        else:
                            print(f"Error: {filename} cannot be converted to a dictionary.")
                except Exception as e:
                    print(f"Error reading {filename}: {str(e)}")
            except Exception as e:
                print(f"Error reading {filename}: {str(e)}")
    return indexers, confs


def save_data_to_json(data, json_path, json_pack_path):
    version = datetime.now().strftime("%Y%m%d%H%M")
    result = {
        "version": version,
        "indexer": data[0],
        "conf": data[1]
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=True, indent=4)

    with open(json_pack_path, "w", encoding="utf-8") as f:
        json.dump(result, f, separators=(',', ':'), ensure_ascii=True)


def save_json_to_dat(json_path, bin_path):
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = f.read()
    base64_data = base64.b64encode(json_data.encode("utf-8")).decode("utf-8")
    with open(bin_path, "w", encoding="utf-8") as f:
        f.write(base64_data)


def format_json_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except UnicodeDecodeError:
        print(f"Warning: {file_path} might be encoded with a different encoding than utf-8, attempting with gbk.")
        try:
            with open(file_path, "r", encoding="gbk") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error decoding JSON in {file_path}: {e}")
            return
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in {file_path}: {e}")
        return

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def format_json_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and filename.lower().endswith(".json"):
            format_json_file(file_path)


def create_or_clear_sites_file(sites_dat_path):
    if os.path.exists(sites_dat_path):
        with open(sites_dat_path, "w") as f:
            f.truncate(0)
    else:
        with open(sites_dat_path, "w") as f:
            pass


def convert_base64_to_json(input_file_path, output_file_path):
    with open(input_file_path, 'r') as input_file, open(output_file_path, 'w') as output_file:
        line_number = 0
        for line in input_file:
            line_number += 1
            try:
                decoded_line = base64.b64decode(line.strip()).decode('utf-8')
                json_data = json.loads(decoded_line)
                json.dump(json_data, output_file)
                output_file.write('\n')
            except Exception as e:
                print(f"Error on line {line_number}: {str(e)}")


if __name__ == "__main__":
    format_json_files_in_folder("sites")
    create_or_clear_sites_file("user.sites.bin")
    create_or_clear_sites_file("user.sites.json")
    create_or_clear_sites_file("user.sites.pack.json")
    indexers, confs = process_json_files("sites")
    data = (indexers, confs)
    save_data_to_json(data, "user.sites.json", "user.sites.pack.json")
    save_json_to_dat("user.sites.pack.json", "user.sites.bin")

    # 旧的json转换方法
    # create_or_clear_sites_file("old/user.sites.old.json")
    # convert_base64_to_json("old/user.sites.dat", "old/user.sites.old.json")
