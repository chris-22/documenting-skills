# architecture-beta — Style and Syntax

High-level system architecture view.

## When to use
- High-level system architecture view
- Show layers (API, Data, External) with services inside
- Maximum ~15 services (becomes unreadable with more)

## Available elements
- **group**: visual grouping with icon and title. Supports nesting with `in`
  ```
  group api(cloud)[API Layer]
  group internal(server)[Internal] in api
  ```
- **service**: node with icon and title, optionally inside a group
  ```
  service db(database)[Data Store] in data
  ```
- **edge**: directional connection with T/B/L/R to indicate which side it exits/enters
  ```
  webapi:R --> L:pm
  pm:B --> T:ds
  ```
- **junction**: 4-way branching point
  ```
  junction junc1 in api
  ```

## Default available icons
`cloud`, `database`, `disk`, `internet`, `server`

Additional icons from iconify.design (200k+ icons) can be registered.

## Appian style template
```
architecture-beta
    group ui(internet)[Capa UI]
    group logic(server)[Capa Logica]
    group data(database)[Capa Datos]
    group ext(cloud)[Sistemas Externos]

    service sites(internet)[Sites] in ui
    service webapis(server)[Web APIs] in ui

    service pm(server)[Process Models] in logic
    service rules(disk)[Expression Rules] in logic

    service ds(database)[Data Stores] in data
    service cdt(disk)[CDTs] in data

    service ext1(cloud)[External API] in ext
    service ext2(cloud)[File Service] in ext

    sites:R --> L:pm
    webapis:R --> L:pm
    pm:B --> T:ds
    pm:R --> L:ext1
    pm:R --> L:ext2
```

## Limitations
- Does not support classDef or custom colors (fixed style per element type)
- Does not support edge labels
- groupIds CANNOT be used directly in edges; use `{group}` modifier on services
