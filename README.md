<picture>
  <source media="(prefers-color-scheme: dark) and (max-width: 600px)" srcset="./assets/profile-hero-mobile-dark.svg">
  <source media="(prefers-color-scheme: light) and (max-width: 600px)" srcset="./assets/profile-hero-mobile-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="./assets/profile-hero-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/profile-hero-light.svg">
  <img src="./assets/profile-hero-light.svg" alt="Pavel Putrenkov — Java and Spring backend engineer focused on reliable document-processing systems" width="100%">
</picture>

<p align="center">
  <a href="https://www.linkedin.com/in/pavlo-putrenkov/"><img src="https://img.shields.io/badge/LinkedIn-Connect-0969DA?style=flat-square&amp;logo=linkedin&amp;logoColor=white" alt="Connect with Pavel Putrenkov on LinkedIn"></a>
</p>

I build Java/Spring backend systems where correctness, explicit contracts, and
actionable diagnostics matter—especially document processing, PDF analysis,
and services that integrate multiple data sources.

## Selected systems

<table>
<tr>
<td width="56%" valign="top">

### [PDF Text Layer Auditor](https://github.com/lMysticl/pdf-text-layer-auditor)

A Java 21 CLI that catches missing or suspicious native PDF text layers before
they disrupt search, copy/paste, indexing, accessibility workflows, or
downstream extraction.

**Evidence:** GitHub Marketplace Action · page-level diagnostics · versioned
JSON · signed releases

<p>
  <a href="https://github.com/lMysticl/pdf-text-layer-auditor/actions/workflows/build.yml"><img src="https://github.com/lMysticl/pdf-text-layer-auditor/actions/workflows/build.yml/badge.svg" alt="PDF Text Layer Auditor build status"></a>
  <a href="https://github.com/lMysticl/pdf-text-layer-auditor/actions/workflows/codeql.yml"><img src="https://github.com/lMysticl/pdf-text-layer-auditor/actions/workflows/codeql.yml/badge.svg" alt="PDF Text Layer Auditor CodeQL status"></a>
</p>

[`Repository`](https://github.com/lMysticl/pdf-text-layer-auditor) ·
[`Marketplace`](https://github.com/marketplace/actions/pdf-text-layer-audit) ·
[`Latest release`](https://github.com/lMysticl/pdf-text-layer-auditor/releases/latest)

</td>
<td width="44%" valign="top">

### [User Aggregation Service](https://github.com/lMysticl/user-aggregation-service)

A Java 21 and Spring Boot 3.5 service that exposes one validated REST API over
PostgreSQL and MongoDB user data.

**Evidence:** bounded concurrent aggregation · Caffeine caching · Flyway ·
OpenAPI · Docker Compose

<p>
  <a href="https://github.com/lMysticl/user-aggregation-service/actions/workflows/ci.yml"><img src="https://github.com/lMysticl/user-aggregation-service/actions/workflows/ci.yml/badge.svg" alt="User Aggregation Service CI status"></a>
  <a href="https://github.com/lMysticl/user-aggregation-service/actions/workflows/codeql.yml"><img src="https://github.com/lMysticl/user-aggregation-service/actions/workflows/codeql.yml/badge.svg" alt="User Aggregation Service CodeQL status"></a>
</p>

[`Repository`](https://github.com/lMysticl/user-aggregation-service) ·
[`Latest release`](https://github.com/lMysticl/user-aggregation-service/releases/latest)

</td>
</tr>
</table>

## Core capabilities

<table align="center">
<tr>
<td width="50%" valign="top"><strong>Backend</strong><br><sub>Java 21 · Spring Boot · REST · Hibernate</sub></td>
<td width="50%" valign="top"><strong>Documents</strong><br><sub>PDFBox · text layers · validation · extraction</sub></td>
</tr>
<tr>
<td width="50%" valign="top"><strong>Data</strong><br><sub>PostgreSQL · MongoDB · JPA · caching</sub></td>
<td width="50%" valign="top"><strong>Delivery</strong><br><sub>Maven · Docker · JUnit · GitHub Actions</sub></td>
</tr>
</table>

Selected full-stack work: `React` · `TypeScript`

## Open-source record

<table width="100%">
<tr>
<td width="280" align="center"><h3>77</h3><sub>public pull requests</sub></td>
<td width="280" align="center"><h3>66</h3><sub>merged</sub></td>
<td width="280" align="center"><h3>Broadleaf Commerce</h3><sub>earlier public contributions</sub></td>
</tr>
</table>

Those contributions were made through my former work account,
[`putrenkov`](https://github.com/putrenkov), which is retained for historical
attribution. `lMysticl` is my current GitHub profile.

- [Historical order purge](https://github.com/BroadleafCommerce/BroadleafCommerce/pull/2360) —
  retention safety, extensibility, and MySQL/PostgreSQL compatibility
- [Domain equality and serialization invariants](https://github.com/BroadleafCommerce/BroadleafCommerce/pull/2156) —
  regression coverage across the domain model
- [Multi-catalog persistence fix](https://github.com/BroadleafCommerce/BroadleafCommerce/pull/2367) —
  a major persistence defect validated through review
