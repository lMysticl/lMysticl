<picture>
  <source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark) and (max-width: 600px)" srcset="https://github.com/lMysticl/lMysticl/raw/829de0a5c47a945d99649da610732a845c466995/assets/profile-cover-2026-static-mobile-dark.svg">
  <source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: light) and (max-width: 600px)" srcset="https://github.com/lMysticl/lMysticl/raw/829de0a5c47a945d99649da610732a845c466995/assets/profile-cover-2026-static-mobile-light.svg">
  <source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" srcset="https://github.com/lMysticl/lMysticl/raw/829de0a5c47a945d99649da610732a845c466995/assets/profile-cover-2026-static-dark.svg">
  <source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: light)" srcset="https://github.com/lMysticl/lMysticl/raw/829de0a5c47a945d99649da610732a845c466995/assets/profile-cover-2026-static-light.svg">
  <source media="(prefers-color-scheme: dark) and (max-width: 600px)" srcset="https://github.com/lMysticl/lMysticl/raw/829de0a5c47a945d99649da610732a845c466995/assets/profile-cover-2026-animated-mobile-dark.svg">
  <source media="(prefers-color-scheme: light) and (max-width: 600px)" srcset="https://github.com/lMysticl/lMysticl/raw/829de0a5c47a945d99649da610732a845c466995/assets/profile-cover-2026-animated-mobile-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/lMysticl/lMysticl/raw/829de0a5c47a945d99649da610732a845c466995/assets/profile-cover-2026-animated-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/lMysticl/lMysticl/raw/829de0a5c47a945d99649da610732a845c466995/assets/profile-cover-2026-animated-light.svg">
  <img src="https://github.com/lMysticl/lMysticl/raw/829de0a5c47a945d99649da610732a845c466995/assets/profile-cover-2026-static-light.svg" alt="Pavel Putrenkov, Senior Java Engineer. Complex inputs, clear outcomes." width="100%">
</picture>

I'm Pavel, a Senior Java Engineer with 10+ years of experience in payments,
e-commerce, and document processing. I built a payment system from the ground
up and led Java delivery for three years while staying hands-on in design,
implementation, and review. Today I deliver document conversion and interactive
reporting across Java 21 / Spring Boot and React / TypeScript.

I focus on the boundaries that make complex systems dependable: clear API and
data contracts, faithful document processing, measured performance, and failures
that point to their cause. I back those decisions with automated tests and
observability.

[Explore my work](#selected-work) · [Connect on LinkedIn](https://www.linkedin.com/in/pavlo-putrenkov/)

## Selected work

### 01 · [PDF Text Layer Auditor](https://github.com/lMysticl/pdf-text-layer-auditor)

A PDF can look perfect while its text layer is missing. This Java 21 CLI and
GitHub Action catch suspicious pages before they disrupt search, extraction, or
accessibility workflows. Versioned JSON and deterministic exit codes make the
findings usable in CI.

[Source code](https://github.com/lMysticl/pdf-text-layer-auditor) · [GitHub Marketplace](https://github.com/marketplace/actions/pdf-text-layer-audit) · [Latest release](https://github.com/lMysticl/pdf-text-layer-auditor/releases/latest)

### 02 · [User Aggregation Service](https://github.com/lMysticl/user-aggregation-service)

One validated REST API brings PostgreSQL and MongoDB user records together
without exposing their source as an integration burden. The Java 21 / Spring
Boot service uses bounded concurrency, source-aware responses, caching, and
deterministic failure handling.

[Source code](https://github.com/lMysticl/user-aggregation-service) · [Latest release](https://github.com/lMysticl/user-aggregation-service/releases/latest)

### 03 · [ArchVerity](https://plugins.jetbrains.com/plugin/34234-archverity)

A Kotlin IntelliJ IDEA plugin for analyzing Spring architecture and contracts
across repositories.

[JetBrains Marketplace](https://plugins.jetbrains.com/plugin/34234-archverity)

## Engineering practice

I use unit, integration, contract, and browser tests to validate changes across
service and UI boundaries. I measure processing with Micrometer and Prometheus,
and use AI-assisted workflows for analysis and review while retaining ownership
of design decisions and final verification.

## Open-source history

My earlier Broadleaf Commerce contributions were made through my former work
account, [`putrenkov`](https://github.com/putrenkov):

- [Historical order purge](https://github.com/BroadleafCommerce/BroadleafCommerce/pull/2360) — retention safety and MySQL/PostgreSQL compatibility.
- [Domain equality and serialization invariants](https://github.com/BroadleafCommerce/BroadleafCommerce/pull/2156) — regression coverage across the domain model.
- [Multi-catalog persistence fix](https://github.com/BroadleafCommerce/BroadleafCommerce/pull/2367) — a persistence defect validated through review.
