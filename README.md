# Pavel Putrenkov

Java/Spring backend engineer focused on document-processing systems, PDF
analysis, reliable APIs, and maintainable service design. I also use React and
TypeScript for selected full-stack work.

## Selected projects

### [PDF Text Layer Auditor](https://github.com/lMysticl/pdf-text-layer-auditor)

A Java 21 CLI for diagnosing missing or suspicious native text layers before
they disrupt search, copy/paste, indexing, accessibility workflows, or
downstream text extraction.

- page-by-page diagnostics and versioned JSON reports
- CI-friendly exit codes and documented resource limits
- automated tests, CodeQL analysis, dependency updates, and releases
- explicit scope: it does not run OCR or modify source PDFs

### [User Aggregation Service](https://github.com/lMysticl/Aggregation_Service)

A Spring Boot service that aggregates user data from PostgreSQL and MongoDB,
with caching, OpenAPI documentation, and Docker support.

## Core stack

`Java 21` · `Spring Boot` · `REST APIs` · `PDFBox` · `PostgreSQL` ·
`MongoDB` · `Hibernate` · `Maven` · `Docker` · `JUnit` · `GitHub Actions`

Selected full-stack work: `React` · `TypeScript`

## Open-source history

Earlier public contributions to Broadleaf Commerce were made through my former
work account, [`putrenkov`](https://github.com/putrenkov): **77 public pull
requests, 66 merged**. That account is retained for historical attribution;
`lMysticl` is my current GitHub profile.

Selected contributions:

- [Historical order purge](https://github.com/BroadleafCommerce/BroadleafCommerce/pull/2360) —
  a team change involving retention safety, extensibility, and
  MySQL/PostgreSQL compatibility
- [Domain equality and serialization invariants](https://github.com/BroadleafCommerce/BroadleafCommerce/pull/2156) —
  regression coverage and review-driven changes across the domain model
- [Multi-catalog persistence fix](https://github.com/BroadleafCommerce/BroadleafCommerce/pull/2367) —
  a major persistence defect discussed and validated through review

## Engineering priorities

- tests that protect behavior and important invariants
- reproducible builds and CI that verifies documented workflows
- explicit API and data contracts
- actionable diagnostics and honest limitations
- small, reviewable changes with clear trade-offs
