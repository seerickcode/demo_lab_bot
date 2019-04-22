__all__ = ['LabExists']

class LabExists(Exception):
    pass

class LabTotalExceeded(Exception):
    pass

class LabCloudException(Exception):
    pass

class LabCloudTimeout(Exception):
    pass

class LabConfigMissing(Exception):
    pass
