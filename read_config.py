import json
import yaml

def read_config(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
        # config = json.load(file)
        area1_points:list[list[int]] = config["area1_points"]
    return  area1_points


if __name__ == "__main__":
    config_path = 'd:\\code\\blue-net\\Engineering-innovation-competition-vision\\config.yaml'
    config = read_config(config_path)
    print(config)
