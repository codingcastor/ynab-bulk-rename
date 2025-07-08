# Publishing Checklist for ynab-bulk-rename

This checklist ensures the package is ready for publication to PyPI.

## ✅ Security & Code Quality

- [x] **No hardcoded secrets**: All sensitive data uses environment variables
- [x] **Proper .gitignore**: Excludes .env, __pycache__, build artifacts
- [x] **Clean code review**: No security vulnerabilities found
- [x] **License included**: MIT license file added

## ✅ Package Configuration

- [x] **pyproject.toml updated**: All required fields added
  - [x] Author information (⚠️ **Update placeholders**)
  - [x] License specification
  - [x] Project URLs (⚠️ **Update GitHub username**)
  - [x] Keywords and classifiers
  - [x] Console script entry point
  - [x] Proper version management
- [x] **MANIFEST.in**: Controls what files are included
- [x] **Version consistency**: Version defined in code and referenced in pyproject.toml

## ✅ Documentation

- [x] **README.md updated**: Installation and usage instructions
- [x] **Console command examples**: Uses `ynab-bulk-rename` command
- [x] **Clear setup instructions**: How to get YNAB API token

## ✅ GitHub Actions

- [x] **Test workflow**: Tests package across Python 3.10, 3.11, 3.12
- [x] **Publish workflow**: Automated PyPI publishing on release
- [x] **Trusted publishing**: Uses OIDC for secure publishing

## 📋 Pre-Publication Tasks

### 1. Update Placeholders
- [x] Replace "Your Name" with actual author name in:
  - `pyproject.toml` (authors and maintainers)
  - `LICENSE` (copyright holder)
- [x] Replace "your.email@example.com" with actual email in `pyproject.toml`
- [x] Replace "yourusername" with actual GitHub username in `pyproject.toml` URLs

### 2. Set Up PyPI Account
- [x] Create PyPI account at https://pypi.org/account/register/
- [x] Verify email address
- [x] Enable 2FA (recommended)

### 3. Configure Trusted Publishing
- [x] Go to PyPI → Account Settings → Publishing
- [x] Add a new "pending publisher" with:
  - **PyPI Project Name**: `ynab-bulk-rename`
  - **Owner**: `yourusername` (your GitHub username)
  - **Repository name**: `ynab-bulk-rename`
  - **Workflow name**: `publish.yml`
  - **Environment name**: `release`

### 4. Test the Package Locally
```bash
# Install in development mode
pip install -e .

# Test the console command
ynab-bulk-rename --help
ynab-bulk-rename --version

# Test building
pip install build
python -m build

# Test installation from wheel
pip install dist/*.whl
```

### 5. Create GitHub Release
- [ ] Commit all changes to main branch
- [ ] Create a new release on GitHub:
  - Tag: `v0.1.0`
  - Title: `v0.1.0 - Initial Release`
  - Description: Release notes
- [ ] GitHub Actions will automatically publish to PyPI

## 🚀 Post-Publication

- [ ] Verify package appears on PyPI: https://pypi.org/project/ynab-bulk-rename/
- [ ] Test installation from PyPI: `pip install ynab-bulk-rename`
- [ ] Update project documentation if needed
- [ ] Consider adding shields/badges to README

## 📝 Notes

- The package uses trusted publishing (OIDC) for security
- No API tokens need to be stored in GitHub secrets
- The publish workflow only runs on GitHub releases
- Tests run on every push and pull request 