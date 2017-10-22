class Error(Exception):
    pass

class CityAlreadyExists(Error):
    pass

class CityNotFound(Error):
    pass

class CityIsDisabled(Error):
    pass

class CityIsEnabled(Error):
    pass

class UnknownProviderSlug(Error):
    pass

class ProviderNotImplemented(Error):
    pass

class ArchiveAlreadyExists(Error):
    pass
