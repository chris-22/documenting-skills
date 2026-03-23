# Appian Export Format Reference

## Contents
- [Known folder names](#known-folder-names-verified-from-real-appian-exports)
- [Additional object types](#additional-object-types-that-may-appear-in-other-exports)
- [Critical file format notes](#critical-file-format-notes)
- [Official Appian documentation references](#official-appian-documentation-references)

## Known folder names (verified from real Appian exports)

**IMPORTANT**: The folder names inside the export are NOT officially documented by Appian. The list below is based on verified observations from real exports. Always start by **listing the actual directories** present in the project root rather than assuming a fixed structure.

- `application/` -- application metadata/definitions (main app manifest with full object list)
- `connectedSystem/` -- Connected Systems (HTTP, SOAP, etc.)
- `content/` -- document management objects (documents/folders/knowledge centers)
- `dataStore/` -- Data Stores (with entity-to-CDT mappings and JDBC data source keys)
- `datatype/` -- Custom Data Types (CDTs) -- **these are `.xsd` files with URL-encoded names**, not `.xml`
- `group/` -- Groups (with member/admin hierarchy)
- `META-INF/` -- package/export metadata
- `processModel/` -- Process Models (BPMN-like XML)
- `processModelFolder/` -- hierarchical folders of process models
- `recordType/` -- Record Types (data fabric / service-backed)
- `site/` -- Sites (with page-to-object navigation mapping)
- `tempoFeed/` -- Tempo Feeds
- `tempoReport/` -- Tempo Reports
- `translationSet/` -- Translation Sets
- `translationString/` -- Translation Strings
- `webApi/` -- Web APIs (with expression code and sample payloads)
- `patches.xml` -- package patch metadata (if present)

## Additional object types that MAY appear in other exports

Per Appian official docs (design-objects.html), these object types exist and can be exported, but their **exact folder names in the ZIP are unverified** -- discover them dynamically:
- Expression Rules (stored expressions, like custom functions)
- Constants (single values or object references; env-specific ones have NO value in export)
- Interfaces (SAIL UI definitions)
- Decisions (business rule objects)
- Integration objects (outbound calls to external systems via connected systems)
- Portals (public-facing web apps with service accounts)
- Group Types

**Discovery rule**: in Phase A, always list ALL directories under the project root and treat any unrecognized folder as a new object type to document. Do NOT skip unknown folders.

## Critical file format notes

- **CDTs** in `datatype/` are `.xsd` (XML Schema) files, NOT `.xml`. Their filenames are URL-encoded (e.g., `%7Burn%3Acom%3Aappian%3Atypes%3ARC%7DRC_CDT_Incidencia.xsd`). Decode `%7B` to `{`, `%3A` to `:`, `%7D` to `}` to get the type namespace + name.
- **All other objects** are `.xml` files named by UUID or Appian internal ID.
- **Opaque Appian references** appear throughout expressions as `#"_a-XXXX-..._NNNNN"` or `#"urn:appian:record-type:v1:UUID"`. These MUST be resolved via the cross-reference index (Phase A).
- **Environment-specific constants**: per Appian official docs, constants marked as environment-specific have their **values stripped from the export XML**. They require an Import Customization file to set values during import.
- **Passwords in smart services** (e.g., Call Web Service, Query Database) are **NOT exported**. Process models containing them are imported but NOT published until credentials are provided.

## Content folder structure

In Appian exports, interfaces (and many other rule-based objects) are NOT in a separate `interfaceObject/` folder. They are inside `content/` as `<contentHaul>` XML files with different child elements:

| Child element in `<contentHaul>` | Object type | Typical count |
|---|---|---|
| `<interface>` | **Interface (SAIL UI)** | Dozens to hundreds |
| `<rule>` | Expression Rule | Hundreds |
| `<constant>` | Constant | Hundreds |
| `<outboundIntegration>` | Integration object | Tens |
| `<decision>` | Decision | Few |
| `<document>` | Document/file | Dozens |
| `<folder>` | Document folder | Few |
| `<rulesFolder>` | Rules folder | Few |
| `<report>` | Report/Dashboard | Few |
| `<communityKnowledgeCenter>` | Knowledge Center | Few |

**Discovery**: scan ALL files in `content/`, parse the root `<contentHaul>`, and classify by the first child element that is not `versionUuid`, `roleMap`, `history`, or `typedValue`.

## Process Model name extraction

The `<pm><meta>` section contains THREE name-related fields, each with a `<string-map>` of locale-specific `<pair>` elements:
- `<name>` -- **design object name** (static, use this for documentation)
- `<desc>` -- description (use for inventory description column)
- `<process-name>` -- **runtime instance name** (may contain dynamic expressions starting with `=` and referencing `pv!` process variables; do NOT use as the primary name, but document the expression pattern if present)

Each `<string-map>` may have 1 to 4 `<pair>` entries with different `<locale>` attributes (e.g., `lang="es"` without country, `lang="en" country="GB"`, etc.). Many entries may be empty (`<value/>`).

**Name extraction algorithm** (apply to `<name>` field):
1. Collect all `<pair>` entries where `<value>` is non-empty (not `<value/>`)
2. Priority order: `lang="es" country=""` (Spanish generic) > `lang="es"` (any country) > `lang="en"` (any) > first non-empty value
3. If all values are identical across locales (common case), just use that value
4. If no `<name>` value found, fall back to `<process-name>` (stripping the `="..."` expression prefix if present)
5. Final fallback: use the XML filename (UUID)

## Official Appian documentation references

When documenting, cross-check behavior against the official Appian docs (latest version):
- **Design Objects**: https://docs.appian.com/suite/help/latest/design-objects.html -- complete list of Appian object types and their purpose
- **Deployment Guidelines**: https://docs.appian.com/suite/help/latest/Application_Deployment_Guidelines.html -- object-specific export/import rules, risks, and cautions
- **Import Customization Files**: https://docs.appian.com/suite/help/latest/Managing_Import_Customization_Files.html -- file format, property syntax, and examples

Do NOT copy content from these docs verbatim. Use them to validate behavior and enrich deployment/risk sections with accurate guidance.
