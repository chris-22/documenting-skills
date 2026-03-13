# Analysis Checklist

Exhaustive checklist of items to verify during Phase 1 (Discovery). Organized by project layer.

## Table of Contents

- [1. Build & Dependencies](#1-build--dependencies)
- [2. Application Configuration](#2-application-configuration)
- [3. Domain Model](#3-domain-model)
- [4. API Layer](#4-api-layer)
- [5. Business Logic](#5-business-logic)
- [6. Process Orchestration (BPMN/DMN)](#6-process-orchestration-bpmndmn)
- [7. Persistence](#7-persistence)
- [8. Messaging](#8-messaging)
- [9. Security](#9-security)
- [10. Infrastructure](#10-infrastructure)
- [11. CI/CD](#11-cicd)
- [12. Testing](#12-testing)
- [13. External Systems](#13-external-systems)

---

## 1. Build & Dependencies

- [ ] Read `pom.xml` or `build.gradle`
- [ ] Extract: groupId, artifactId, version
- [ ] Identify parent POM / BOM and its version
- [ ] List direct dependencies, classify by role:
  - **Framework**: quarkus-bom, spring-boot-starter-*, etc.
  - **Persistence**: JDBC, JPA, Hibernate, Flyway, Liquibase
  - **Messaging**: Kafka, AMQP, JMS
  - **REST clients**: quarkus-rest-client, spring-cloud-openfeign, OpenAPI backend JARs
  - **Security**: OIDC, JWT, OAuth2
  - **Testing**: JUnit, Mockito, WireMock, RestAssured, Testcontainers
  - **Code generation**: MapStruct, Lombok, OpenAPI Generator
  - **Observability**: Micrometer, OpenTelemetry, SmallRye Health
- [ ] Identify build plugins: compiler, surefire, failsafe, OpenAPI generator, jib/docker
- [ ] Identify Maven/Gradle profiles (dev, test, native, etc.)
- [ ] Identify annotation processors (MapStruct, Lombok, Kogito)

## 2. Application Configuration

- [ ] Read `application.properties` / `application.yml`
- [ ] Read `application-{profile}.yml` for each profile (dev, test, cert, pre, pro)
- [ ] Read `bootstrap.yml` / `bootstrap.properties` if present
- [ ] Extract application name
- [ ] List REST clients with configKey and URL per environment
- [ ] List datasources: DB type, JDBC URL, schema, pool config
- [ ] List messaging configuration: bootstrap servers, topics, group IDs, serializers, SSL
- [ ] List cache configuration: engine (Caffeine, Redis), names, TTLs
- [ ] List security configuration: OIDC provider, client-id, TLS
- [ ] List logging configuration: categories, levels, format
- [ ] Identify feature flags or toggles
- [ ] Identify health check / readiness / liveness configuration

## 3. Domain Model

- [ ] List all DTOs / models in packages `model`, `dto`, `domain`
- [ ] For each model: fields, Java types, validation annotations (`@NotNull`, `@Valid`, `@Size`)
- [ ] Serialization annotations: `@JsonProperty`, `@JsonIgnore`, `@JsonFormat`
- [ ] Custom framework annotations: `@VariableInfo`, `@UserTask`, etc.
- [ ] Enums: possible values and their meaning
- [ ] Inheritance / composition between models
- [ ] JPA entities: `@Entity`, `@Table`, relationships, column mappings

## 4. API Layer

- [ ] List all Resources / Controllers
- [ ] For each endpoint: HTTP method, full path, media types
- [ ] Request body: DTO type, required fields
- [ ] Response body: DTO type, possible status codes
- [ ] Path parameters and query parameters
- [ ] Required headers
- [ ] Global exception handlers / error mappers
- [ ] Existing OpenAPI documentation (`@Operation`, `@ApiResponse`)

## 5. Business Logic

- [ ] List all service classes (`@ApplicationScoped`, `@Service`, `@Component`)
- [ ] For each service: public methods, parameters, return type, exceptions
- [ ] Identify Service Task implementations (classes implementing BPMN task interfaces)
- [ ] Mappers (MapStruct `@Mapper`): source → target, custom methods
- [ ] Configuration classes: providers, producers, interceptors
- [ ] Decision logic: conditions, branching, validations

## 6. Process Orchestration (BPMN/DMN)

> Skip this section if the project contains no `.bpmn` or `.dmn` files.

- [ ] List all `.bpmn` and `.dmn` files
- [ ] For each BPMN process:
  - [ ] Process name and process ID
  - [ ] Process variables: name, full Java type (from `itemDefinition[@structureRef]`), tags (input/output/internal)
  - [ ] Service Tasks: Java interface (`bpmn2:interface`), method (`bpmn2:operation`)
  - [ ] Inputs of each Service Task (from `dataInputAssociation`: source → target)
  - [ ] Outputs of each Service Task (from `dataOutputAssociation`: source → target)
  - [ ] Gateways: type (exclusive, inclusive, parallel), conditions on sequence flows
  - [ ] Error definitions: errorCode of each `bpmn2:error`
  - [ ] Boundary error events: which Service Task they catch, where they redirect
  - [ ] Script Tasks: language, inline code (from `bpmn2:script`)
  - [ ] Subprocesses: hierarchical structure, embedded vs call activity
  - [ ] Timer events: duration, cycle
  - [ ] Signal / Message events
- [ ] For each DMN table:
  - [ ] Decision name and ID
  - [ ] Input columns: name, type, expression
  - [ ] Output columns: name, type
  - [ ] Rules: conditions → results

## 7. Persistence

- [ ] Configured datasources: name, DB type, JDBC URL
- [ ] Schemas / databases used
- [ ] Migrations: Flyway (`db/migration/V*.sql`) or Liquibase (`db/changelog/`)
- [ ] Named queries or custom repositories
- [ ] Pool configuration: min/max size, timeout

## 8. Messaging

- [ ] Broker(s): Kafka, RabbitMQ, ActiveMQ
- [ ] Topics / queues: names, partition configuration
- [ ] Producers: classes, target topics, serializers
- [ ] Consumers: classes, source topics, deserializers, group IDs
- [ ] SSL/TLS configuration for brokers
- [ ] Dead letter topics / retry policies

## 9. Security

- [ ] OAuth2/OIDC provider: URLs, client credentials
- [ ] Token management: classes, cache, TTL
- [ ] TLS/mTLS: certificates, truststores
- [ ] Authorization: roles, permissions, annotations (`@RolesAllowed`, `@Authenticated`)
- [ ] API keys / client IDs
- [ ] Referenced secrets (names, not values)

## 10. Infrastructure

- [ ] `Dockerfile`: base image, JDK version, build stages, entrypoint
- [ ] `deployment.yaml`: replicas, resources, probes, env vars
- [ ] `.chart/values*.yaml`: Helm configuration per environment
- [ ] Referenced ConfigMaps and Secrets
- [ ] Ingress / Service configuration
- [ ] HPA (Horizontal Pod Autoscaler) if present
- [ ] Network policies

## 11. CI/CD

- [ ] List all workflows in `.github/workflows/`
- [ ] For each workflow: trigger, main jobs, key steps
- [ ] Build: compilation, tests, static analysis
- [ ] Publish: Docker image build & push, registries
- [ ] Deploy: strategy (rolling, blue-green, canary), environments
- [ ] Secrets used in pipelines
- [ ] Release management: tagging, branching strategy

## 12. Testing

- [ ] Unit tests: classes, frameworks (JUnit 5, Mockito)
- [ ] Integration tests: `@QuarkusTest`, `@SpringBootTest`, profiles
- [ ] WireMock mocks: mappings directory, available stubs
- [ ] Test profiles: `application-test.properties`
- [ ] Coverage: configured plugins (JaCoCo, etc.)

## 13. External Systems

For each detected external integration:

- [ ] System name
- [ ] REST client configKey
- [ ] Base URL per environment
- [ ] Java client interface
- [ ] Endpoints: HTTP method, path, path params, query params
- [ ] Request DTO: fields, types, annotations
- [ ] Response DTO: fields, types, annotations
- [ ] Error handling: expected HTTP codes, exceptions
- [ ] Example JSON (from WireMock mocks or inferred)
- [ ] Dependencies with other systems (execution order, shared data)
