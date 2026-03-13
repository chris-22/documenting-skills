# stateDiagram-v2 — Appian Conventions

## When to use
- Business entity lifecycle (e.g. tickets, requests, cases)
- Approval flows with clear states
- Infer from: `Estado`, `Status`, `Phase` fields in CDTs; branching in Process Models

## Styling with classDef
```
classDef active fill:#6FCF97,color:#fff
classDef terminal fill:#EB5757,color:#fff
classDef pending fill:#F2994A,color:#fff

class Draft,Submitted active
class Closed,Rejected terminal
class Returned pending
```

**Limitation**: classDef CANNOT be applied to `[*]` (start/end) or composite states.

## Entity lifecycle style template
```
stateDiagram-v2
    direction LR

    [*] --> Draft
    Draft --> Submitted : Creator completes
    Submitted --> Validated : Coordinator validates
    Validated --> InReview : Reviewer checks

    state decision_review <<choice>>
    InReview --> decision_review
    decision_review --> Closed : Approved
    decision_review --> Returned : Rejected

    Returned --> Submitted : Fix and resubmit
    Submitted --> Discarded : Discard
    Closed --> [*]
    Discarded --> [*]

    note right of Draft : Initial state on creation via Web API or UI
    note right of Returned : Requires rejection reason

    classDef active fill:#6FCF97,color:#fff
    classDef terminal fill:#EB5757,color:#fff
    classDef warning fill:#F2994A,color:#fff
    class Draft,Submitted,Validated,InReview active
    class Closed,Discarded terminal
    class Returned warning
```
