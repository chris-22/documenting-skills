# erDiagram — Style and Syntax

Entity-relationship data model.

## When to use
- CDT data model
- Entity relationships (Data Store entities)
- Show fields with types and keys (PK, FK)

## Attributes with keys
```
APP_CDT_Order {
    int Id PK "Auto-generated"
    date CreatedDate
    int StatusId FK "Ref MasterStatus"
    string Title
}
```

## Styling with classDef (supported)
```
classDef master fill:#E0AFF5,stroke:#BB6BD9
classDef transactional fill:#56CCF2,stroke:#2D9CDB
class APP_CDT_MasterStatus master
class APP_CDT_Order transactional
```

## Direction
`erDiagram` supports `TB`, `BT`, `LR`, `RL`. For large models use `LR`.

## Appian data model style
- **Master entities** (lookup/reference tables): lilac `#E0AFF5`
- **Transactional entities** (business data): cyan `#56CCF2`
- **Log/audit entities**: gray `#F2F2F2`
- Use `PK` and `FK` in attributes
- Group: main entities first, then master entities
- Include the real table name (from `@Table`) as comment in PK: `"table: rccdtincidencia"`
