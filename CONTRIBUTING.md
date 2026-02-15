# Contributing to Glanced Reader

Thank you for considering contributing! This document provides guidelines for contributing to Glanced Reader.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Commit Messages](#commit-messages)
- [Submitting Changes](#submitting-changes)

## Getting Started

### Prerequisites

- **Frontend**: Node.js 24+, npm
- **Backend**: Python 3.13+, PostgreSQL 17+, Redis
- **Development**: `make`, Docker (optional but recommended)

### Setup

```bash
# Clone your fork
git clone https://github.com/your-username/reader.git
cd reader

# Install dependencies
make setup

# Start all services
make dev
```

See [README.md](README.md#development) for detailed setup instructions.

## Development Workflow

1. **Create a branch** from `main`

   ```bash
   git checkout -b feature/your-feature-name
   # or: git checkout -b fix/your-bug-name
   ```

2. **Make changes** following [coding standards](#coding-standards)

3. **Test your changes**

   ```bash
   # Frontend
   cd app && npm run lint && npm run prettier && npx tsc --noEmit

   # Backend
   cd server && ruff check . && ruff format --check . && mypy backend/
   ```

4. **Commit** following [commit message conventions](#commit-messages)

5. **Push and create pull request**

## Coding Standards

### Frontend (TypeScript/Next.js)

- Use TypeScript strictly (no `any` without justification)
- Follow ESLint and Prettier configurations
- Use existing UI components from `@/components/ui/`
- Keep components small and focused
- Use SWR for data fetching, Zustand for state

### Backend (Python/FastAPI)

- Follow type hinting requirements (mypy must pass)
- Use clean architecture layers: routers → application → domain/infrastructure
- Write async/await code for database operations
- Follow PEP 8 via ruff formatting

### General

- Write clear, self-documenting code
- Add tests for new functionality
- Update documentation as needed
- Keep pull requests focused and reasonably sized

## Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `revert`

**Examples:**

```
feat(auth): add password strength indicator

fix(feed): prevent duplicate feed subscriptions

docs(readme): update docker setup instructions

refactor(user): simplify user creation flow
```

## Submitting Changes

### Pull Request Checklist

- [ ] Code follows project standards
- [ ] Tests pass locally (`make test`)
- [ ] Linting passes (`make lint`)
- [ ] Commit messages follow conventions
- [ ] PR description clearly explains changes
- [ ] Documentation is updated if needed

### Pull Request Process

1. Ensure CI checks pass (automated)
2. Request review from maintainers
3. Address feedback promptly
4. Keep conversation focused on the PR

### What We're Looking For

- Bug fixes and improvements
- New features that align with project goals
- Performance optimizations
- Documentation improvements
- Test coverage improvements

### What We're Less Likely To Accept

- Major architectural changes without prior discussion
- Features that significantly increase complexity
- Breaking changes without migration path
- Large refactorings without clear benefit

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for architectural changes
- Join us in GitHub Discussions

Thank you for contributing! 🎉
