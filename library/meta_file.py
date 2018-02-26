import yaml


def write_data(path, data):
    with open(path, 'w') as stream:
        yaml.dump(data, stream)


def read_data(path):
    data = {}
    with open(path, 'r') as stream:
        data = yaml.load(stream)
    return data
