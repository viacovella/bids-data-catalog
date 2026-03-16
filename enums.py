import enum

# Enums

class LicenseType(str, enum.Enum):
    CC_BY = "CC-BY"
    CC0 = "CC0"
    CC_BY_SA = "CC-BY-SA"
    CC_BY_NC = "CC-BY-NC"
    PDDL = "PDDL"
    ODBL = "ODBL"
    UNKNOWN = "UNKNOWN"

class ModalityType(str, enum.Enum):
    MRI = "MRI"
    EEG = "EEG"
    MEG = "MEG"
    FMRI = "fMRI"
    DTI = "DTI"
    UNKNOWN = "UNKNOWN"
