# URI
URI_DEFAULT = "/scral/v1.0/monicora"
URI_GLASSES_REGISTRATION = URI_DEFAULT + "/glasses"
URI_GLASSES_LOCALIZATION = URI_GLASSES_REGISTRATION + "/localization"
URI_GLASSES_INCIDENT = URI_GLASSES_REGISTRATION + "/incident"

# filters
FILTER_VIRTUAL_PROPERTY = "?$filter=startswith(name,'Incident-Notification')"
FILTER_VIRTUAL_SENSOR = "?$filter=startswith(name,'Incident')"

# values
PROPERTY_LOCALIZATION_NAME = "Localization-Smart-Glasses"
PROPERTY_INCIDENT_NAME = "Incident-Reporting"

CATALOG_NAME_GLASSES = "resource_catalog_GLASSES.json"
