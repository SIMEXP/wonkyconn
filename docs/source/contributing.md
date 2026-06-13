# Contributing

## Development environment

Fork the repository from GitHub and clone your fork locally (see [here](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account) to set up your SSH key):

```bash
git clone git@github.com:<your_username>/wonkyconn.git
cd wonkyconn
```

Set up a development environment. We recommend using [pixi](https://pixi.sh):

```bash
pixi install
```

Alternatively, you can use a virtual environment with pip:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,docs]"
```

Install pre-commit hooks to automatically format code and run checks before each commit:

```bash
pre-commit install
```

## Downloading test data

Fetch all test data (this will take a bit of time and 1GB of disk space):

```bash
# From the root of the repository
datalad get .
```

### Demo command

Light-mode demo:

```bash
wonkyconn data/halfpipe test-output group \
    --phenotypes data/halfpipe/participants.tsv \
    --atlas Schaefer2018Combined data/atlases/atlas-Schaefer2018Combined_dseg.nii.gz \
    --light-mode \
    --verbosity 2
```

## Contributing to code

We use a common [feature branch workflow](https://www.python4data.science/en/latest/productive/git/workflows/feature-branches.html) for development.

1. Comment on an existing issue or open a new issue referencing your addition.

    > [!tip]
    > Review and discussion on new code can begin well before the work is complete, and the more discussion the better! The development team may prefer a different path than you’ve outlined, so it’s better to discuss it and get approval at the early stage of your work.

1. Create a new branch from `main`:

    ```bash
    git switch -c my_feature main
    ```

1. Make the changes in your branch.
1. Run the tests locally to confirm your changes don’t break anything. See the [Testing](#running-tests) section below for details.
1. Push your branch to your fork.

    > [!caution]
    > If this is the first commit, you might want to set up the remote tracking.
    >
    > ```bash
    > git push origin HEAD --set-upstream
    > ```

1. Submit a pull request to the `main` branch of the original repository; follow the guidelines in the [Pull requests](#pull-requests-guidelines) section below.
1. Check that all continuous integration checks pass. If not, review the logs to identify and fix the issue.
1. Respond to any review comments and make necessary changes.

(running-tests)=

### Running tests

Default unit tests:

```bash
pixi run unittest
```

Light smoke tests:

```bash
pixi run smoketestlight
```

Full non-smoke selection:

```bash
pixi run fulltest
```

Specific pytest file:

```bash
pytest -v wonkyconn/tests/test_correlation.py
```

Learn more about [specifying which test to run](https://docs.pytest.org/en/stable/how-to/usage.html#select-tests)

### Building the docs

You can build the documentation locally to review your changes before pushing.
The documentation is built at `docs/build/html`.

Using pixi:

```bash
pixi run -e docs sphinx-build docs/source docs/build/html
```

or with a local Python environment:

```bash
cd docs
make html
```

(pull-requests-guidelines)=

## Pull requests guidelines

Keep pull requests focused. Use draft PRs for early design or method review.

PR prefixes:

- **[ENH]** for enhancements
- **[FIX]** for bug fixes
- **[TEST]** for new or updated tests
- **[DOCS]** for documentation changes
- **[STYL]** for stylistic changes
- **[MAINT]** for maintenance or refactoring

## Making a release

This project currently does not publish releases on PyPI. We tag versions on the repository for user reference. Upon pushing a new tag, a GitHub workflow will build and publish a new Docker image.

### Preparing a release

Create a local release branch from `main`:

```bash
git fetch upstream main
git checkout -b REL-x.y.z upstream/main
```

First, update the file `docs/source/changes.md` to make sure all the new features, enhancements, and bug fixes are included in their respective sections.

Finally, change the title from x.y.z.dev to x.y.z:

```markdown
## x.y.z

**Released MONTH YEAR**

### New
...
```

Add these changes and submit a PR:

```bash
git add docs/source/changes.md
git commit -m "REL x.y.z"
git push upstream REL-x.y.z
```

Once the PR has been reviewed and merged, pull from `upstream/main` and tag the merge commit:

```bash
git fetch upstream main
git switch upstream/main
git tag x.y.z
git push origin --tags
```

### Post-release

The release is done 🎉

Create a new boilerplate section in `docs/source/changes.md` for the next release:

```markdown
## x.y.z+1.dev

**Released MONTH YEAR**

### New

### Fixes

### Enhancements

### Changes
```

> [!caution]
> Current releases use Git tags and container builds. Update this page if PyPI publishing is added.

Based on contributing guidelines from the [STEMMRoleModels](https://github.com/KirstieJane/STEMMRoleModels/blob/gh-pages/CONTRIBUTING.md) project and [Nilearn contribution guidelines](https://nilearn.github.io/stable/development.html).
