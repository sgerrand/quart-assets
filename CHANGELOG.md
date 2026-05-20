# Changelog

All notable changes to this project will be documented in this file. See [Keep a
CHANGELOG](http://keepachangelog.com/) for how to update this file. This project
adheres to [Semantic Versioning](http://semver.org/).

## [0.1.5](https://github.com/sgerrand/quart-assets/compare/v0.1.4...v0.1.5) (2026-05-20)


### Bug Fixes

* correct falsy config check and prevent CLI logger handler leak ([de5999a](https://github.com/sgerrand/quart-assets/commit/de5999a9a8b89f2220f2f08a16bb6609996db1a3))
* **types:** resolve mypy strict and pyright errors ([537314f](https://github.com/sgerrand/quart-assets/commit/537314fc2561f90390c727f4e0f5e6b37eab7746))


### Documentation

* correct tox config location and class name in CLAUDE.md ([7282b30](https://github.com/sgerrand/quart-assets/commit/7282b304313b8406fa7d097d485263cdb9fc12a2))

## [0.1.4](https://github.com/sgerrand/quart-assets/compare/v0.1.3...v0.1.4) (2026-05-20)


### Bug Fixes

* **deps:** Bump idna from 3.11 to 3.15 ([#116](https://github.com/sgerrand/quart-assets/issues/116)) ([9d3882c](https://github.com/sgerrand/quart-assets/commit/9d3882c0dec6658bed3c9a1dba764f3223f9ddc5))
* **deps:** Bump pymdown-extensions from 10.21.2 to 10.21.3 ([#115](https://github.com/sgerrand/quart-assets/issues/115)) ([35649ca](https://github.com/sgerrand/quart-assets/commit/35649cad6ac313471e1e3313c199b31eaa86cc8a))
* **deps:** Bump urllib3 from 2.6.3 to 2.7.0 ([#113](https://github.com/sgerrand/quart-assets/issues/113)) ([1aa672d](https://github.com/sgerrand/quart-assets/commit/1aa672de332535ff4e0312d818cee767cb690a3b))

## [0.1.3](https://github.com/sgerrand/quart-assets/compare/v0.1.2...v0.1.3) (2026-04-12)


### Bug Fixes

* **deps:** bump werkzeug from 3.1.3 to 3.1.4 ([9c6cc10](https://github.com/sgerrand/quart-assets/commit/9c6cc1060191eb041f5f8aa9b9f133308f345010))
* **deps:** bump flask from 3.11 to 3.1.3, werkzeug from 3.1.4 to 3.1.6 ([9c6cc10](https://github.com/sgerrand/quart-assets/commit/d140f924bdcdc2a564432acbac486ca5c8dab885))

## [0.1.2](https://github.com/sgerrand/quart-assets/compare/0.1.1...v0.1.2) (2025-08-28)

### Dependencies

* Bump urllib3 from 2.4.0 to 2.5.0 ([#10](https://github.com/sgerrand/quart-assets/pull/10))
* Bump h2 from 4.2.0 to 4.3.0 ([#28](https://github.com/sgerrand/quart-assets/pull/28))

### Documentation

* use macros to reuse content in documentation ([#5](https://github.com/sgerrand/quart-assets/pull/5))
* add entries for previous releases to changelog ([623ccdc](https://github.com/sgerrand/quart-assets/commit/623ccdcf29ec61915759ab2146702107a5f72dd8), [292ee56](https://github.com/sgerrand/quart-assets/commit/292ee5656a5e7a3c7a1d12707e4e0dfa6c33bf0a))

## 0.1.1.post1 (2025-06-16)

### Fixed

- Fixed CLI tests for Windows.
- Reduced permissions for GitHub Actions workflow jobs.
- Configured automatic building and publishing of package documentation.

## 0.1.1 (2025-06-16)

### Fixed

- Resolved type errors with CLI commands.
- Updated CLI commands to handle Quart's asynchronous app contexts.

## 0.1.0 (2025-06-04)

Initial release, forked from Flask-Assets v2.1.1.
