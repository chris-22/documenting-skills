# Diagram Patterns — Mermaid

Proven and validated Mermaid patterns for technical documentation. Each pattern includes a complete example and guidance on when to use it.

> **IMPORTANT**: Validate Mermaid syntax before including in the document. Avoid unescaped special characters in labels. Use double quotes `"label"` for labels with spaces or special characters.

## Table of Contents

- [1. Multi-layer Architecture](#1-multi-layer-architecture)
- [2. BPMN Process Flow](#2-bpmn-process-flow)
- [3. Data Flow Map](#3-data-flow-map)
- [4. Authentication Sequence](#4-authentication-sequence)
- [5. Error Flow (Compact)](#5-error-flow-compact)
- [6. Inclusive / Parallel Gateway (Fork-Join)](#6-inclusive--parallel-gateway-fork-join)
- [General Mermaid Notes](#general-mermaid-notes)

---

## 1. Multi-layer Architecture

**When to use**: Project overview showing how requests flow from the entry point to the final external systems.

```mermaid
flowchart TD
    A["POST /EntryEndpoint\n(requestData)"]
    B["Process Orchestrator\nFramework vX.Y"]
    A --> B

    subgraph SVC["Service Tasks Layer"]
        direction LR
        ST1["Service Tasks\nGroup A"]
        ST2["Service Tasks\nGroup B"]
        ST3["Service Tasks\nGroup C"]
    end
    B --> SVC

    subgraph BE["Backend Clients (REST)"]
        direction LR
        BK1["backend-a\nbackend-b"]
        BK2["backend-c\nbackend-d"]
        BK3["backend-e\nbackend-f"]
    end
    SVC --> BE

    subgraph GW["API Gateway"]
        direction LR
        GW1["Gateway\nEndpoint Group 1"]
        GW2["Gateway\nEndpoint Group 2"]
        GW3["Gateway\nEndpoint Group 3"]
    end
    BE --> GW

    subgraph SYS["External Systems"]
        direction LR
        S1["System A\nSystem B"]
        S2["System C\nSystem D"]
        S3["System E\nSystem F"]
    end
    GW --> SYS
```

**Tips**:
- Use `subgraph` to group components by layer
- `direction LR` inside subgraphs for horizontal layout of components in the same layer
- Labels with `\n` to show additional info (versions, names)
- Keep a maximum of 4-5 vertical layers for readability

---

## 2. BPMN Process Flow

**When to use**: Document the complete flow of a BPMN process with phases, gateways, decisions, and error paths.

```mermaid
flowchart TD
    START(("Start")) --> INIT["Initialize\nVariables"]

    subgraph PHASE1["Phase 1: Validation"]
        INIT --> ST1["Service Task 1\nValidate data"]
        ST1 --> GW1{"Data valid?"}
        GW1 --> |"Yes"| ST2["Service Task 2\nGet entity"]
        GW1 --> |"No"| ERR1["Error:\nInvalid data"]
    end

    subgraph PHASE2["Phase 2: Processing"]
        ST2 --> GW2{"Inclusive Gateway"}
        GW2 --> |"Condition A"| ST3["Service Task 3\nProcess A"]
        GW2 --> |"Condition B"| ST4["Service Task 4\nProcess B"]
        GW2 --> |"Always"| ST5["Service Task 5\nLog event"]
        ST3 --> JOIN(("Join"))
        ST4 --> JOIN
        ST5 --> JOIN
    end

    subgraph PHASE3["Phase 3: Finalization"]
        JOIN --> ST6["Service Task 6\nConsolidate"]
        ST6 --> GW3{"Success?"}
        GW3 --> |"Yes"| EVT_OK["Event OK"]
        GW3 --> |"No"| ERR2["Error:\nConsolidation failed"]
    end

    EVT_OK --> END_OK(("End OK"))
    ERR1 --> END_ERR(("End Error"))
    ERR2 --> END_ERR

    style ERR1 fill:#f96,stroke:#333
    style ERR2 fill:#f96,stroke:#333
    style END_ERR fill:#f66,stroke:#333
    style END_OK fill:#6f6,stroke:#333
```

**Tips**:
- Use `subgraph` per process phase
- Gateways with `{}` (diamond shape) and descriptive labels
- `((""))` for start/end events (circles)
- `style` to color error terminators (red) and success (green)
- Inclusive gateways: show all branches and the join point

---

## 3. Data Flow Map

**When to use**: Show what data flows between systems, what output from one system feeds into which input of another.

```mermaid
flowchart TD
    ENTRY["Entry Point\n(RequestData)"]

    SYS_A["System A"]
    SYS_B["System B"]
    SYS_C["System C"]
    SYS_D["System D"]

    ENTRY --> |"field1, field2"| SYS_A
    SYS_A --> |"entityId, status"| SYS_B
    SYS_A --> |"entityId"| SYS_C
    ENTRY --> |"documentId"| SYS_C
    SYS_B --> |"accountNumber"| SYS_D
    SYS_C --> |"extractedData"| SYS_D

    SYS_D --> |"finalResult"| RESULT["Process Output"]

    style ENTRY fill:#e1f5fe,stroke:#0288d1
    style RESULT fill:#e8f5e9,stroke:#388e3c
```

**Tips**:
- Arrow labels `-->|"data"|` show what data flows
- Color entry (blue) and output (green) for clarity
- Do not include decision logic, only data flow
- Useful for identifying inter-system dependencies

---

## 4. Authentication Sequence

**When to use**: Document the OAuth2/OIDC token retrieval flow with caching.

```mermaid
sequenceDiagram
    participant App as Application
    participant Cache as Token Cache<br/>(Caffeine/Redis)
    participant STS as OAuth Provider<br/>(STS/Keycloak)
    participant API as Target API

    App->>Cache: getToken(clientId)
    alt Token cached and valid
        Cache-->>App: cachedToken
    else Token expired or missing
        App->>STS: POST /oauth/token<br/>grant_type=client_credentials
        STS-->>App: access_token (JWT, exp=3600s)
        App->>Cache: put(clientId, token, TTL=60s)
    end

    App->>API: GET /resource<br/>Authorization: Bearer {token}
    API-->>App: 200 OK + response body

    Note over App,API: Headers: x-client-id, x-b3-traceid, etc.
```

**Tips**:
- `alt`/`else` for conditional branching
- `Note over` for contextual information
- `<br/>` for line breaks in participant labels
- Participants named with short but descriptive aliases

---

## 5. Error Flow (Compact)

**When to use**: Document how an error is handled in a specific Service Task within the BPMN.

```mermaid
flowchart LR
    ST["Service Task\nCall System X"]
    ST -.-> |"Boundary\nError Event"| SCRIPT["Script Task\neventCode = ERR_001"]
    SCRIPT --> NOTIFY["Service Task\nSend error event"]
    NOTIFY --> END_ERR(("End Error"))

    style ST fill:#fff3e0,stroke:#f57c00
    style END_ERR fill:#ffcdd2,stroke:#d32f2f
```

**Tips**:
- `flowchart LR` for horizontal layout (compact)
- `-.->` (dashed line) for boundary events
- One diagram per distinct error pattern
- Keep a maximum of 4-5 nodes for readability

---

## 6. Inclusive / Parallel Gateway (Fork-Join)

**When to use**: Document parallel or conditional execution of multiple branches that then converge.

```mermaid
flowchart TD
    PREV["Previous step"] --> GW_FORK{"Inclusive Gateway\n(fork)"}

    subgraph BRANCH_A["Branch A (if condition A)"]
        GW_FORK --> |"condition A"| TASK_A1["Task A.1"]
        TASK_A1 --> TASK_A2["Task A.2"]
    end

    subgraph BRANCH_B["Branch B (if condition B)"]
        GW_FORK --> |"condition B"| TASK_B1["Task B.1"]
    end

    subgraph BRANCH_C["Branch C (always)"]
        GW_FORK --> |"always"| TASK_C1["Task C.1"]
    end

    TASK_A2 --> GW_JOIN(("Join"))
    TASK_B1 --> GW_JOIN
    TASK_C1 --> GW_JOIN

    GW_JOIN --> NEXT["Next step"]
```

**Tips**:
- `subgraph` per branch for visual grouping
- Label on each fork arrow indicating the condition
- "always" for branches that execute unconditionally
- Join as `((""))` node to indicate convergence

---

## General Mermaid Notes

1. **Escape characters**: Use double quotes for labels with parentheses, brackets, or special characters: `["Label (with parens)"]`
2. **Node IDs**: Use short, descriptive IDs without spaces: `ST1`, `GW_FORK`, `END_OK`
3. **Label length**: Keep labels < 40 characters. Use `\n` to split long lines
4. **Colors**: Use `style` sparingly, only to highlight errors (red), successes (green), or entries (blue)
5. **Size**: Keep diagrams < 30 nodes. If larger, split into sub-diagrams
6. **Validation**: ` ```mermaid ` blocks render in GitHub and in the exported HTML. Verify syntax before including.
