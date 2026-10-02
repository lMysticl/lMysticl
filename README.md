<picture>
  <source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark) and (max-width: 600px)" srcset="https://github.com/lMysticl/lMysticl/raw/94d3e870ead983b73e0678805b536ca4f51f7b14/assets/profile-cover-2026-static-mobile-dark.svg">
  <source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: light) and (max-width: 600px)" srcset="https://github.com/lMysticl/lMysticl/raw/94d3e870ead983b73e0678805b536ca4f51f7b14/assets/profile-cover-2026-static-mobile-light.svg">
  <source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" srcset="https://github.com/lMysticl/lMysticl/raw/94d3e870ead983b73e0678805b536ca4f51f7b14/assets/profile-cover-2026-static-dark.svg">
  <source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: light)" srcset="https://github.com/lMysticl/lMysticl/raw/94d3e870ead983b73e0678805b536ca4f51f7b14/assets/profile-cover-2026-static-light.svg">
  <source media="(prefers-color-scheme: dark) and (max-width: 600px)" srcset="https://github.com/lMysticl/lMysticl/raw/94d3e870ead983b73e0678805b536ca4f51f7b14/assets/profile-cover-2026-animated-mobile-dark.svg">
  <source media="(prefers-color-scheme: light) and (max-width: 600px)" srcset="https://github.com/lMysticl/lMysticl/raw/94d3e870ead983b73e0678805b536ca4f51f7b14/assets/profile-cover-2026-animated-mobile-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/lMysticl/lMysticl/raw/94d3e870ead983b73e0678805b536ca4f51f7b14/assets/profile-cover-2026-animated-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/lMysticl/lMysticl/raw/94d3e870ead983b73e0678805b536ca4f51f7b14/assets/profile-cover-2026-animated-light.svg">
  <img src="https://github.com/lMysticl/lMysticl/raw/94d3e870ead983b73e0678805b536ca4f51f7b14/assets/profile-cover-2026-static-light.svg" alt="Pavel Putrenkov, Senior Java Engineer. Complex inputs, clear outcomes." width="100%">
</picture>

**Senior Java Developer · Former Java Team Lead · 10+ years of experience**

I build payment systems, e-commerce services and document-processing software
with Java and Spring Boot. At Ukrposhta, I built a payment system from scratch
and led Java development for three years, combining implementation with
architecture, code reviews and technical decisions.

My current work connects Java 21 / Spring Boot 3 services for document
conversion with interactive reporting in React / TypeScript. I focus on clear
API contracts, reliable integrations and automated tests that protect business
workflows.

**Open to remote Senior / Lead Java roles · Kyiv, Ukraine**

[LinkedIn](https://www.linkedin.com/in/pavlo-putrenkov/) · [Hiring enquiries](mailto:putrenkov99@gmail.com)

## Experience

- **Payments and integrations:** custom payment services at Ukrposhta, plus
  PayPal integration and extensions to Stripe workflows in a later role.
- **Document processing and reporting:** conversion across PDF, Word,
  presentations and spreadsheets, with attention to layout, multilingual
  content and the APIs used by reporting interfaces.
- **Hands-on technical leadership:** architecture decisions, code reviews,
  sprint planning and interviews, alongside implementation and collaboration
  with business stakeholders.

## Core stack

Java 21 · Spring Boot 3 · REST APIs · Microservices · Kafka · PostgreSQL · MySQL
· Hibernate / JPA · React · TypeScript

Testing and delivery: JUnit · Mockito · Testcontainers · Playwright ·
GitHub Actions · Docker · Micrometer / Prometheus

## Selected work

### 01 · [PDF Text Layer Auditor](https://github.com/lMysticl/pdf-text-layer-auditor)

A Java CLI and GitHub Action that flags missing or suspicious PDF text layers
before they disrupt search, indexing or text extraction. Page-level findings
and JSON reports make document checks usable in CI.

[Source code](https://github.com/lMysticl/pdf-text-layer-auditor) · [GitHub Marketplace](https://github.com/marketplace/actions/pdf-text-layer-audit) · [Latest release](https://github.com/lMysticl/pdf-text-layer-auditor/releases/latest)

### 02 · [User Aggregation Service](https://github.com/lMysticl/user-aggregation-service)

A portfolio API that combines user records from PostgreSQL and MongoDB using
bounded concurrent requests. It retains source information and returns an
explicit error when a source fails or times out, so consumers can distinguish
complete results from a failed aggregation. Includes integration tests with
real databases through Testcontainers, migrations and observability.

[Source code](https://github.com/lMysticl/user-aggregation-service) · [Latest release](https://github.com/lMysticl/user-aggregation-service/releases/latest)

### 03 · [ArchVerity](https://plugins.jetbrains.com/plugin/34234-archverity)

A Kotlin plugin for IntelliJ IDEA that helps review Spring architecture and
contracts across repositories, bringing these checks into the development
workflow.

[JetBrains Marketplace](https://plugins.jetbrains.com/plugin/34234-archverity)

## Earlier open-source work

Before this account, I contributed to Broadleaf Commerce as
[`putrenkov`](https://github.com/putrenkov). A few examples:

- [Historical order purge](https://github.com/BroadleafCommerce/BroadleafCommerce/pull/2360) — retention safety and MySQL/PostgreSQL compatibility.
- [Domain equality and serialization invariants](https://github.com/BroadleafCommerce/BroadleafCommerce/pull/2156) — regression coverage across the domain model.
- [Multi-catalog persistence fix](https://github.com/BroadleafCommerce/BroadleafCommerce/pull/2367) — a persistence defect validated through review.
