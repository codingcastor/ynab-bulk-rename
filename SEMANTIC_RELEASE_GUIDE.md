# 🤖 Semantic Release Guide

This guide explains how to use Semantic Release for automated version management and releases.

## 🚀 **How It Works**

Semantic Release automatically:
1. **Analyzes commit messages** to determine version bump type
2. **Generates changelog** from commit messages
3. **Updates version** in `ynab_bulk_rename.py` and `pyproject.toml`
4. **Creates Git tag** and **GitHub release**
5. **Publishes to PyPI** automatically

## 📝 **Conventional Commit Format**

Use this format for ALL commit messages:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### **Commit Types**

| Type | Description | Version Bump | Example |
|------|-------------|--------------|---------|
| `feat` | New feature | **Minor** (0.1.0 → 0.2.0) | `feat: add custom regex patterns` |
| `fix` | Bug fix | **Patch** (0.1.0 → 0.1.1) | `fix: handle empty payee names` |
| `perf` | Performance improvement | **Patch** | `perf: optimize API calls` |
| `refactor` | Code refactoring | **Patch** | `refactor: simplify error handling` |
| `revert` | Revert previous commit | **Patch** | `revert: remove faulty feature` |
| `docs` | Documentation only | **No release** | `docs: update README examples` |
| `style` | Code style changes | **No release** | `style: fix formatting` |
| `test` | Add/update tests | **No release** | `test: add rate limiting tests` |
| `chore` | Maintenance tasks | **No release** | `chore: update dependencies` |
| `ci` | CI/CD changes | **No release** | `ci: update GitHub Actions` |
| `build` | Build system changes | **No release** | `build: update pyproject.toml` |

### **Breaking Changes (Major Version)**

For breaking changes, use `!` or `BREAKING CHANGE:` footer:

```bash
# Method 1: Using !
feat!: change CLI argument structure

# Method 2: Using footer
feat: add new authentication method

BREAKING CHANGE: API token now required in environment variable
```

Both trigger a **major version bump** (0.1.0 → 1.0.0).

## ✅ **Commit Message Examples**

### **Good Examples:**

```bash
# Features (minor version bumps)
feat: add support for multiple budgets
feat: implement retry logic for API calls
feat(cli): add --verbose flag for debugging

# Bug fixes (patch version bumps)
fix: handle network timeouts gracefully
fix: prevent duplicate payee names
fix(api): correct rate limiting calculation

# Performance improvements (patch version bumps)
perf: cache API responses for better performance
perf: optimize regex pattern matching

# Breaking changes (major version bumps)
feat!: change default pattern to more generic format
feat: redesign CLI interface

BREAKING CHANGE: --pattern argument now required
```

### **Examples that WON'T trigger releases:**

```bash
docs: update installation instructions
style: fix code formatting
test: add unit tests for error handling
chore: update dependencies
ci: improve GitHub Actions workflow
build: update build configuration
```

## 🎯 **Workflow**

1. **Make your changes** in a feature branch
2. **Write conventional commit messages**:
   ```bash
   git commit -m "feat: add support for custom date formats"
   ```
3. **Push to main branch** (or merge PR to main)
4. **Semantic Release runs automatically** and:
   - Analyzes commits since last release
   - Determines version bump type
   - Generates changelog
   - Creates release and publishes to PyPI

## 📋 **Version Bump Rules**

| Commits Since Last Release | Version Bump | Example |
|----------------------------|--------------|---------|
| Only `fix:`, `perf:`, `refactor:`, `revert:` | **Patch** | 1.0.0 → 1.0.1 |
| At least one `feat:` | **Minor** | 1.0.0 → 1.1.0 |
| Any `BREAKING CHANGE` or `feat!:` | **Major** | 1.0.0 → 2.0.0 |
| Only `docs:`, `style:`, `test:`, `chore:` | **No release** | - |

## 🛠️ **Setup Requirements**

### 1. **Workflow Configuration**
The `.github/workflows/release.yml` workflow is already configured and will:
- Run on every push to `main`
- Only create releases when commits warrant them
- Generate beautiful changelogs with emojis

### 2. **GitHub Repository Settings**
- **Actions enabled**: ✅ (already done)
- **Trusted publishing**: ✅ (already configured)
- **Main branch protection**: Recommended but optional

### 3. **PyPI Configuration**
- **Trusted publishing**: ✅ (already configured)
- **Environment**: `release` environment configured in workflow

## 🔧 **Advanced Features**

### **Scoped Commits**
Add scope for better organization:
```bash
feat(cli): add new --format option
fix(api): handle rate limiting errors
docs(readme): add troubleshooting section
```

### **Skip Release**
To skip release for specific commits:
```bash
feat: add new feature

This commit adds a new feature but we don't want to release yet.
```

Or use `[skip ci]` in commit message to skip CI entirely.

### **Pre-release Versions**
On feature branches, you can create pre-releases:
```bash
# On feature branch
feat: add experimental feature
# Could create: 1.1.0-beta.1
```

## 📊 **Generated Changelog Example**

Semantic Release will generate changelogs like this:

```markdown
# Changelog

## [1.2.0](https://github.com/user/repo/compare/v1.1.0...v1.2.0) (2024-01-15)

### 🚀 Features

* add support for multiple budgets ([abc123](https://github.com/user/repo/commit/abc123))
* implement retry logic for API calls ([def456](https://github.com/user/repo/commit/def456))

### 🐛 Bug Fixes

* handle network timeouts gracefully ([ghi789](https://github.com/user/repo/commit/ghi789))
* prevent duplicate payee names ([jkl012](https://github.com/user/repo/commit/jkl012))

### ⚡ Performance

* cache API responses for better performance ([mno345](https://github.com/user/repo/commit/mno345))
```

## 🚨 **Important Notes**

1. **First Release**: Your first semantic release might start from v1.0.0 (or continue from current 0.1.0)
2. **Commit History**: Only commits since the last release are analyzed
3. **Branch Protection**: Consider requiring PR reviews for main branch
4. **Team Education**: Ensure all team members understand conventional commits

## 🎯 **Getting Started**

1. **Start using conventional commits immediately**:
   ```bash
   git commit -m "feat: add your new feature"
   ```

2. **Push to main** (or merge PR):
   ```bash
   git push origin main
   ```

3. **Watch the magic happen** in GitHub Actions! 🎉

## 🔍 **Troubleshooting**

### **No Release Created**
- Check if commits follow conventional format
- Ensure commits are not all `docs:`, `style:`, `test:`, or `chore:`
- Check GitHub Actions logs for errors

### **Wrong Version Bump**
- Verify commit message types
- Check for `BREAKING CHANGE:` or `!` for major versions
- Remember: `feat:` = minor, `fix:` = patch

### **Build Failures**
- Check that `update_version.py` script works correctly
- Verify PyPI trusted publishing is configured
- Check workflow permissions

---

**Ready to start?** Just make your next commit with conventional format and push to main! 🚀 