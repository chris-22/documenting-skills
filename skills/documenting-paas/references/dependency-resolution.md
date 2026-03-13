# Dependency Resolution Guide

Step-by-step workflow for resolving external dependency JARs whose source code is not in the workspace. Used during Phase 1 (Discovery) step 11.

## Table of Contents

- [Overview](#overview)
- [Step A — Detect external dependencies](#step-a--detect-external-dependencies)
- [Step B — Ask the user if they want Maven resolution](#step-b--ask-the-user-if-they-want-maven-resolution)
- [Step C — Ask the user for dependency scope](#step-c--ask-the-user-for-dependency-scope)
- [Step D — Resolve dependency source code](#step-d--resolve-dependency-source-code)
- [Step E — Analyze JAR contents](#step-e--analyze-jar-contents)
- [Step F — Document gaps](#step-f--document-gaps)

---

## Overview

When analyzing the project, you will encounter types referenced in BPMN `itemDefinition[@structureRef]`, Service Task interfaces, or Java imports that belong to external dependency JARs (e.g., Service Task JARs, backend client JARs, OpenAPI-generated DTOs). Their source code is NOT in the workspace.

## Step A — Detect external dependencies

- Identify all dependencies in `pom.xml` whose packages appear in BPMN variables, Service Task interfaces, DTO types, or Java imports but have NO corresponding source files in `src/main/java`.
- Build a list of these "external dependency artifacts" with their `groupId:artifactId:version`.

## Step B — Ask the user if they want Maven resolution

- Present the list of detected external dependencies to the user.
- **Ask the user**: _"I found N dependency JARs whose source code is not in the workspace. Do you want me to use Maven to download and inspect their contents?"_
  - **Yes**: Proceed to Step C.
  - **No**: Skip to Step F (document gaps) and infer DTOs from BPMN definitions, WireMock mocks, and available context.

## Step C — Ask the user for dependency scope

- If the user said Yes, **ask**: _"Which dependencies should I analyze?"_
  - **Direct dependencies only (default)**: Analyze only the JARs declared directly in the project's `pom.xml` (e.g., Service Task JARs, backend client JARs). Do NOT descend into their transitive dependencies.
  - **All dependencies (transitive)**: Also analyze dependencies of those dependencies (e.g., the OpenAPI-generated DTOs inside backend JARs, shared model libraries, etc.). This is deeper but takes longer.
- Respect the user's choice throughout the entire analysis.

## Step D — Resolve dependency source code

Resolution methods ordered by priority:

> **CRITICAL**: The version used MUST be the exact version declared in the project's `pom.xml` (or resolved from the parent POM / BOM). This ensures the documentation matches the actual runtime behavior. A cloned repo on disk may be on a different branch or version — Maven resolution from Nexus/JFrog guarantees version accuracy.

### D.1 — Download from Nexus/JFrog via Maven (HIGHEST PRIORITY)

This is the preferred method because it downloads the **exact version declared in the pom.xml**, matching what runs in production.

- First, attempt to download the **sources JAR** (contains readable `.java` files):
  `mvn dependency:copy -Dartifact={groupId}:{artifactId}:{version}:jar:sources -DoutputDirectory=target/deps`
- If sources JAR is not available, download the compiled JAR:
  `mvn dependency:copy -Dartifact={groupId}:{artifactId}:{version} -DoutputDirectory=target/deps`
- Extract the sources JAR and read `.java` files directly for full access to annotations, Javadoc, field types, and method signatures.
- If only the compiled JAR is available, use `jar tf` + `javap -p` to inspect class signatures.

### D.2 — Fall back to local Maven cache (`~/.m2`)

- If Maven download fails (network issues, authentication error, or Maven not available), search in the local Maven repository for the **exact version from pom.xml**:
  - `~/.m2/repository/{groupId-as-path}/{artifactId}/{version}/` for the JAR and `-sources.jar`.
  - On Windows: `%USERPROFILE%\.m2\repository\{groupId-as-path}\{artifactId}\{version}\`.
- The dependency may have been compiled and installed locally with `mvn install`.

### D.3 — Search for cloned repo on disk (LAST RESORT)

- Only if D.1 and D.2 both fail, search for the dependency's source code repository already cloned on the user's machine.
- Use `find_by_name` to search for a directory matching the `artifactId` pattern in:
  - The parent directory of the current project (sibling repos, e.g., `../cib-nysere-fundonbdgsvctsk/`)
  - Common workspace roots: the user's GitHub/repos directories (look at the current project's path to infer the workspace structure)
- **WARNING**: The cloned repo may be on a different branch or version than the one declared in `pom.xml`. If found, verify the version in the repo's `pom.xml` matches the dependency version. If versions differ, document the discrepancy: _"Source code read from local clone at version X.Y.Z, but pom.xml declares version A.B.C"_.
- If found and version matches, read the `.java` source files directly from `src/main/java/`.

### D.4 — Transitive dependencies (if user chose "All dependencies")

- Run `mvn dependency:copy-dependencies -DoutputDirectory=target/deps` to download the full transitive tree, then filter to the relevant artifacts.

## Step E — Analyze JAR contents

Once a JAR is located (either downloaded or from local repo):

- **Prefer sources JAR**: If a `-sources.jar` is available, extract it and read the `.java` files directly. This gives full access to annotations, Javadoc, field types, and method signatures.
- **Otherwise, use the compiled JAR**: List its contents with `jar tf {jar-file}` to identify packages and classes. Decompile relevant classes with `javap -p {class}` for method signatures and field types.
- Focus on: public API classes (REST client interfaces, DTOs, Service Task classes, model objects), method signatures, field types, annotations (`@JsonProperty`, `@Path`, `@GET`, `@POST`, etc.).

## Step F — Document gaps

- If a JAR cannot be resolved by any method (Maven remote + local repo), document it as a gap: _"Could not access {groupId}:{artifactId}:{version}. DTOs for this system are inferred from BPMN dataInputAssociation/dataOutputAssociation, WireMock mocks, and available context."_
- This ensures the documentation is transparent about its sources and limitations.
