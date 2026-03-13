# Appian Deployment Risks Reference

## Contents
- [Object-specific import risks](#object-specific-import-risks)
- [Import Customization File template](#import-customization-file-template)
- [Deployment checklist](#deployment-checklist)

## Object-specific import risks

Based on Appian official deployment guidelines:

- **Precedence/external dependencies** not included in the package
- **Connected Systems**: duplicate names (different UUID) cause import FAILURE
- **CDTs**: if one CDT fails to import, ALL dependent CDTs and their dependent objects also fail (cascade failure)
- **CDTs from WSDLs**: if not included in export, Appian calls the WSDL at import time; structure mismatches cause warnings
- **Data Stores**: JNDI data source name must exist in target environment; if auto-schema-update is enabled globally AND on the data store, Appian adds missing tables/columns but NEVER removes or alters existing ones
- **Documents/Folders/Knowledge Centers** (`content/`): parent objects MUST exist in target; items are NOT auto-included when exporting a container
- **Groups**: member lists are MERGED on import (not replaced); missing parent groups or group types cause failure; duplicate names with different UUIDs fail for Public/Restricted visibility groups
- **Process Models**: passwords in smart services (Call Web Service, Query Database) are NOT exported; model imports but does NOT publish. Escalation tasks with rule/constant expressions may also fail to publish
- **Record Types (synced)**: deploying to a new environment triggers automatic full sync; deploying precedents without the record type requires `forceSync=true` in customization file
- **Environment-specific constants**: values NOT in export; without Import Customization file, import fails for new constants
- **Integration objects**: username/password are env-specific and NOT exported
- Large `content/` folder (note count of items)

## Import Customization File template

Generate in `docs/appian-import-customization-template.properties` using the official Appian format:

```properties
## Connected System: <name>
#connectedSystem.<UUID>.baseUrl=
#connectedSystem.<UUID>.username=
#connectedSystem.<UUID>.password=

## Constant: <name>
## Type: <type>
#content.<UUID>.VALUE=

## Integration: <name>
#content.<UUID>.username=
#content.<UUID>.password=

## Data Source: <JNDI name>
#dataSource.<UUID>.USERNAME=
#dataSource.<UUID>.PASSWORD=

## Record Type: <name> (force sync after deploy)
#recordType.<UUID>.forceSync=true
```

Populate with actual UUIDs and names from the cross-reference index.

## Import Customization requirements

Compile a **specific list** of values that need Import Customization per environment:
- Connected System base URLs (list each with env values from description)
- Connected System credentials (flag as needing configuration)
- Integration object credentials (username/password are env-specific, NOT exported)
- JDBC data source keys (list all distinct `<dataSourceKey>` values)
- Environment-specific constants (values NOT in export; detect from XML where `<value>` is empty)
- Record types that may need `forceSync=true` after deployment

## Deployment checklist

### Pre-import
- Verify dependencies
- Prepare customization file
- Verify DB schemas exist
- Verify JDBC data sources

### Import
- Order considerations
- Patches (parse `patches.xml` if present)

### Post-import
- Smoke tests: web APIs, site navigation, critical processes, connected system connectivity
