from bids import BIDSLayout
from requests import post

import sys, os


dirname = sys.argv[1]
layout = BIDSLayout(dirname, validate=False)

mod = layout.get_modalities()

mydataset = {
    "name": layout.get_dataset_description().get("Name"), 
    "description": "An example BIDS dataset",
    "participants": len(layout.get_subjects()),
    "modalities": ["MRI"],
    "license": layout.get_dataset_description().get("License"),
    "uri": os.path.abspath(dirname)
}
print(mydataset)
response = post("http://127.0.0.1:8000/datasets/", json=mydataset)
print(response.status_code)
print(response.json())