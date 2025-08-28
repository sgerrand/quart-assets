# Changelog

All notable changes to this project will be documented in this file. See [Keep a
CHANGELOG](http://keepachangelog.com/) for how to update this file. This project
adheres to [Semantic Versioning](http://semver.org/).

<!-- %% CHANGELOG_ENTRIES %% -->

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
