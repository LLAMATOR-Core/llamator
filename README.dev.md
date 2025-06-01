# LLAMATOR development instructions

# Setup developer environment

## Setup venv

Run from project root directory:

```bash
. ./setup_dev_env.sh
```
```bash
source venv/bin/activate
```

This will create a new venv and run `pip install -r requirements-dev.txt`.

Last line shows how to activate the environment.

## Install pre-commit

To ensure code quality we use pre-commit hook with several checks. Setup it by:

```bash
pre-commit install
```

All updated files will be reformatted and linted before the commit.

Reformat and lint all files in the project:

```bash
pre-commit run --all-files
```

The used linters are configured in `.pre-commit-config.yaml`. You can use `pre-commit autoupdate` to bump tools to the latest versions.

## Autoreload within notebooks

When you install project's package add below code (before imports) in your notebook:
```
# Load the "autoreload" extension
%load_ext autoreload
# Change mode to always reload modules: you change code in src, it gets loaded
%autoreload 2
```
Read more about different modes in [documentation](https://ipython.org/ipython-doc/3/config/extensions/autoreload.html).

All code should be in `src/` to make reusability and review straightforward, keep notebooks simple for exploratory data analysis.
See also [Cookiecutter Data Science opinion](https://drivendata.github.io/cookiecutter-data-science/#notebooks-are-for-exploration-and-communication).

# Project documentation

In `docs/` directory are Sphinx RST/Markdown files.

Build documentation locally:

```bash
./build_docs.sh
```

Then open `public/index.html` file.

Please read the official [Sphinx documentation](https://www.sphinx-doc.org/en/master/) for more details.


### Github Actions Documentation

**Github Actions** pipelines have `documentation` workflow which will build sphinx documentation automatically on release branch - and it will push it to a branch - it can be hosted on **Github Pages** if you enable it.

To access it, you need to enable it, on **Github repository -> Settings -> Pages** page select **Deploy from a branch** and select **gh-pages**. Link will appear here after deployment.

Please read more about it [here](https://docs.github.com/en/pages/quickstart).

# Semantic version bump

To bump version of the library please use `bump2version` which will update all version strings.

NOTE: Configuration is in `.bumpversion.cfg` and **this is a main file defining version which should be updated only with bump2version**.

For convenience there is bash script which will create commit, to use it call:

```bash
./bump_version.sh minor
```
```bash
./bump_version.sh major
```
```bash
./bump_version.sh patch
```

<img src="assets/img.png" alt="img" width="250"/>

to see what is going to change run:

```bash
./bump_version.sh --dry-run major
```

Script updates **VERSION** file and setup.cfg automatically uses that version.

## Publishing a New Version to PyPI

Follow these steps to build your Python package and upload a new version to PyPI:

1. **Commit the latest changes**
   Ensure all your recent changes are committed to your local repository.

2. **Bump the package version**
   Run the version bump script:
   ```bash
   ./bump_version.sh {minor/major/patch}
   ```

3. **Commit the version bump**
   Add and commit the version change to your repository.

4. **Remove the `dist` directory**
   Delete the existing `dist` directory to clean previous builds.

5. **Build the package**
   Create the source and wheel distributions using the `build` package:
   ```bash
   python -m build
   ```

6. **Publish the package**
   Upload the new version to PyPI using Twine:
   ```bash
   twine upload dist/*
   ```

7. **Push to the remote GitHub repository**
   Push all your commits to the remote repository.