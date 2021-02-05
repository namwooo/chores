import argparse
import hashlib
import json
from pathlib import Path


def indexing(seq, key):
    return {key(item): item for item in seq}


def hash_annotation_id(annotation_id):
    annotation_id_encoded = str(annotation_id).zfill(3).encode()
    hash_id = hashlib.sha256(annotation_id_encoded).hexdigest()
    return hash_id


def convert_bbox_points(points):
    x1, y1, x2, y2 = points
    return [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]


def convert_poly_seg_points(points):
    return points


def get_label_type(label):
    label_keys = label.keys()
    if 'box2d' in label_keys:
        _type = 'bbox'
    elif 'poly2d' in label_keys:
        if label['category'] == 'lane':
            _type = 'polyline'
        elif label['category'] == 'drivable area':
            _type = 'poly_seg'
        else:
            raise ValueError('Not supported label name')
    else:
        raise ValueError('Not supported label type.')

    return _type


def get_parent_path(path):
    return str(Path(str(path).replace('/Users/luca/Documents/images', '')).parent)


parser = argparse.ArgumentParser()
parser.add_argument("--input-path", type=str, dest="input_path", required=True)
parser.add_argument("--output-path", type=str, dest="output_path", required=True)
parser.add_argument("--image-src-path", type=str, dest="image_src_path", required=True)
args = parser.parse_args()

input_path = Path(args.input_path).expanduser()
output_path = Path(args.output_path).expanduser()
image_src_path = Path(args.image_src_path).expanduser()

output_path.mkdir(parents=True, exist_ok=True)

image_src_path_list = list(map(Path, Path(image_src_path).rglob('*.jpg')))
indexed_image_src_path_by_filename = indexing(image_src_path_list, key=lambda p: p.name)

with open(input_path, 'r', encoding='utf-8') as f:
    loaded_data = json.load(f)

for labels_per_image in loaded_data:
    src_path = indexed_image_src_path_by_filename[labels_per_image['name']]
    parent_path = get_parent_path(src_path)
    aimmo_gt = {
        'parent_path': parent_path,
        'filename': labels_per_image['name'],
        'attributes': {},
        'annotations': []
    }

    for label in labels_per_image['labels']:
        label_type = get_label_type(label)

        if label_type == 'bbox':
            points = label['box2d'].values()
            converted_points = convert_bbox_points(points)
        elif label_type == 'poly_seg' or label_type == 'polyline':
            points = label['poly2d'][0]['vertices']
            converted_points = convert_poly_seg_points(points)
        else:
            raise ValueError('not supported label type.')

        aimmo_annotation = {
            'id': hash_annotation_id(label['id']),
            'type': label_type,
            'points': converted_points,
            'label': label['category'],
            'attributes': label['attributes']
        }

        aimmo_gt['annotations'].append(aimmo_annotation)

    export_path = output_path.joinpath(aimmo_gt['filename'].replace('.jpg', '.json'))
    with open(export_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(aimmo_gt))
