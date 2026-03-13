# sequenceDiagram — Appian Conventions

## When to use
- Web API flows (request -> validation -> process -> response)
- Interactions between external systems and the Appian application

## Appian participant conventions

| Appian component | Participant type | Suggested alias |
|-------------------|-------------------|----------------|
| Web API | `participant` | `WA as Web API` |
| Process Model | `participant` | `PM as Process Model` |
| Data Store | `participant` (database) | `DS as Data Store` |
| User/Role | `actor` | `User as User` |
| External system | `participant` | `Ext as External System` |

## Box colors (Appian vs External)
```
box rgba(45,156,219,0.1) Appian
box rgba(242,201,76,0.1) Externo
box rgba(111,207,151,0.1) highlight (rect)
```

## Appian Web API flow style template
```
sequenceDiagram
    autonumber
    box rgba(235,87,87,0.1) External
        actor Client as External Client
    end
    box rgba(45,156,219,0.1) Appian
        participant WA as Web API
        participant Val as Validation
        participant PM as Process Model
        participant DS as Data Store
    end

    Client->>+WA: POST /endpoint (JSON)
    WA->>+Val: Validate input

    alt Validation fails
        Val-->>WA: Errors
        WA-->>Client: 400 Bad Request
    else Validation OK
        Val-->>-WA: OK
        WA->>+PM: startProcess()
        PM->>+DS: Write data
        DS-->>-PM: OK
        PM-->>-WA: Process result
        WA-->>-Client: 200 OK + response
    end
```
