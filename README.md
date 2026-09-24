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

I'm a senior Java engineer with more than ten years of experience across
e-commerce, payments, and document processing. At Ukrposhta, I built a payment
system from the ground up and led Java development for three years, continuing
to write and review code throughout.

I currently work on document conversion and interactive reporting, building
Java 21/Spring Boot services and React/TypeScript interfaces.

[Find me on LinkedIn](https://www.linkedin.com/in/pavlo-putrenkov/)

## Selected work

### 01 · [PDF Text Layer Auditor](https://github.com/lMysticl/pdf-text-layer-auditor)

Some PDFs look fine until you try to search or copy their text. I built a Java
CLI and GitHub Action to catch that early. It points to the pages that need
attention and gives CI a predictable result.

[Source code](https://github.com/lMysticl/pdf-text-layer-auditor) · [GitHub Marketplace](https://github.com/marketplace/actions/pdf-text-layer-audit) · [Latest release](https://github.com/lMysticl/pdf-text-layer-auditor/releases/latest)

### 02 · [User Aggregation Service](https://github.com/lMysticl/user-aggregation-service)

This Spring Boot service reads users from PostgreSQL and MongoDB through one API.
It tells callers where records came from and returns a clear error if one source
times out instead of quietly returning an incomplete answer.

[Source code](https://github.com/lMysticl/user-aggregation-service) · [Latest release](https://github.com/lMysticl/user-aggregation-service/releases/latest)

### 03 · [ArchVerity](https://plugins.jetbrains.com/plugin/34234-archverity)

I wrote this Kotlin plugin for IntelliJ IDEA to inspect Spring architecture and
contracts across repositories.

[JetBrains Marketplace](https://plugins.jetbrains.com/plugin/34234-archverity)

I also build coding-agent workflows for codebase analysis and review. I still
read the diff and run the tests before shipping changes.

## Earlier open-source work

Before this account, I contributed to Broadleaf Commerce as
[`putrenkov`](https://github.com/putrenkov). A few examples:

- [Historical order purge](https://github.com/BroadleafCommerce/BroadleafCommerce/pull/2360) — retention safety and MySQL/PostgreSQL compatibility.
- [Domain equality and serialization invariants](https://github.com/BroadleafCommerce/BroadleafCommerce/pull/2156) — regression coverage across the domain model.
- [Multi-catalog persistence fix](https://github.com/BroadleafCommerce/BroadleafCommerce/pull/2367) — a persistence defect validated through review.
