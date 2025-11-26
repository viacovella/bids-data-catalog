from bids import BIDSLayout
from requests import post

import sys, os

if len(sys.argv) < 2:
    print("Please, specify a BIDS dataset directory.")
    print("Usage: python dspost.py /path/to/bids_dataset")
    sys.exit(1)

dirname = sys.argv[1]

if not os.path.isdir(dirname):
    print(f"Error: The directory '{dirname}' does not exist.")
    sys.exit(1)

try:
    layout = BIDSLayout(dirname, validate=False)
except Exception as e:
    print(f"Error parsing BIDS: {e}")
    sys.exit(1)

# License scanner
def license_scanner(license_str):

    # Normalization logic developed with the help of Google Gemini
    
    if not license_str:
        return "UNKNOWN"

    LICENSE_MAPPING = {
        
        # Long variants
        "Creative Commons Attribution-NonCommercial 4.0 International License": "CC-BY-NC",
        "Creative Commons Attribution-ShareAlike 4.0 International License": "CC-BY-SA",
        "http://www.opendatacommons.org/licenses/pddl/1.0/": "PDDL",
        "https://opendatacommons.org/licenses/odbl/summary/": "ODBL",
        "CC0 1.0 Universal License": "CC0",
        
        # Expression
        "CC-BY-4.0": "CC-BY",
        "CC-BY-SA": "CC-BY-SA",
        "PDDL-1.0": "PDDL",
        "CC BY 4.0": "CC-BY",
        
        # Short Variants
        "CC-BY": "CC-BY",
        "CC BY": "CC-BY",
        "CCO": "CC0",
        "CC0": "CC0",
        "CC-0": "CC0",
        "PDDL": "PDDL",
        "PD": "PDDL",
        "Public Domain": "PDDL",


    }

    target = license_str.lower().strip()
    sorted_keys = sorted(LICENSE_MAPPING.keys(), key=len, reverse=True)


    for key in sorted_keys:
        if key.lower() in target:
            return LICENSE_MAPPING[key]
            
    # License string but no corresponding license
    return "UNKNOWN"


# Modalities

MODALITY_MAPPING = {
    "T1w": "MRI",
    "T2w": "MRI",
    "bold": "fMRI",
    "dwi": "DTI",
    "eeg": "EEG",
    "meg": "MEG"
}

raw_modalities = layout.get_modalities()
api_modalities = []

if raw_modalities:
    for mod in raw_modalities:
        translated = MODALITY_MAPPING.get(mod, "UNKNOWN")
        if translated:
            if translated not in api_modalities:
                api_modalities.append(translated)
else:
    pass




# Prepare dataset info
mydataset = {
    "name": layout.get_dataset_description().get("Name", "NONAME"),
    "description": "An example BIDS dataset",
    "participants": len(layout.get_subjects()),
    "license": license_scanner(layout.get_dataset_description().get("License")),
    "uri": os.path.abspath(dirname),
    "modalities": api_modalities
}

print(mydataset)

try:
    response = post("http://127.0.0.1:8000/datasets/", json=mydataset)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Successo!")
        print(response.json())
    else:
        print("API error:")
        print(response.text) 
except Exception as e:
    print(f"Errore di connessione: {e}")