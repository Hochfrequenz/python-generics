# Python Template Repository including Tox.ini, Unittests, Linting Actions and Coverage Measurements

<!--- you need to replace the `organization/repo_name` in the status badge URLs --->

![Unittests status badge](https://github.com/Hochfrequenz/python_template_repository/workflows/Unittests/badge.svg)
![Coverage status badge](https://github.com/Hochfrequenz/python_template_repository/workflows/Coverage/badge.svg)
![Linting status badge](https://github.com/Hochfrequenz/python_template_repository/workflows/Linting/badge.svg)
![Black status badge](https://github.com/Hochfrequenz/python_template_repository/workflows/Black/badge.svg)

This is a template repository. It doesn't contain any useful code but only a minimal working setup for a Python project including:

- a basic **project structure** with
  - tox.ini
  - requirements.in
  - and a requirements.txt derived from it
  - an example class
  - an example unit test (using pytest)
- ready to use **Github Actions** for
  - [pytest](https://pytest.org)
  - [code coverage measurement](https://coverage.readthedocs.io) (fails below 80% by default)
  - [pylint](https://pylint.org/) (only accepts 10/10 code rating by default)
  - [mypy](https://github.com/python/mypy) (static type checks where possible)
  - [black](https://github.com/psf/black) code formatter check
  - [isort](https://pycqa.github.io/isort/) import order check
  

By default, it uses Python version 3.11.

## How to use this Repository on Your Machine

This introduction assumes that you have tox installed already (
see [installation instructions](https://tox.readthedocs.io/en/latest/installation.html)) and that a `.toxbase` environment
has been created.
`.toxbase` is a project independent virtual environment-template for all the tox environments on your machine. If anything is weird during the tox installation or after the installation, try turning your computer off and on again before getting too frustrated.

Also on new windows machines it is possible that the execution policy is set to restricted and you are not allowed execute scripts. You can find detailed information [here](https://learn.microsoft.com/de-de/powershell/module/microsoft.powershell.core/about/about_execution_policies?view=powershell-7.3).

If this is the case, clone this repository and create the `dev` environment on your machine.

```bash
tox -e dev
```

### How to use with PyCharm

1. Create a new project using existing sources with your local working copy of this repository as root directory. Choose
   the path `your_repo/.tox/dev/` as path of the "previously configured interpreter".
2. Set the
   default [test runner of your project](https://www.jetbrains.com/help/pycharm/choosing-your-testing-framework.html) to
   pytest.
3. Set the `src` directory as sources root (via right click, [docs](https://www.jetbrains.com/help/pycharm/content-root.html)).
4. Set
   the [working directory of the unit tests](https://www.jetbrains.com/help/pycharm/creating-run-debug-configuration-for-tests.html)
   to the project root (instead of the unittest directory).

### How to use with VS Code

1. Open the folder with VS Code.
2. **Select the python interpreter** ([official docs](https://code.visualstudio.com/docs/python/environments#_manually-specify-an-interpreter)) which is created by tox. Open the command pallett with `CTRL + P` and type `Python: Select Interpreter`. Select the interpreter which is placed in `.tox/dev/Scripts/python.exe` under Windows or `.tox/dev/bin/python` under Linux and macOS.
3. **Setup pytest and pylint**. Therefore we open the file `.vscode/settings.json` which should be automatically generated during the interpreter setup. Insert the following lines into the settings:

```json
{
    "python.testing.unittestEnabled": false,
    "python.testing.nosetestsEnabled": false,
    "python.testing.pytestEnabled": true,
    "pythonTestExplorer.testFramework": "pytest",
    "python.testing.pytestArgs": [
        "unittests"
    ],
    "python.linting.pylintEnabled": true
}
```
4. Create a `.env` file and insert the following line

For Windows:
```
PYTHONPATH=src;${PYTHONPATH}
```
For Linux and Mac:
```
PYTHONPATH=src:${PYTHONPATH}
```
This makes sure, that the imports are working for the unittests.
At the moment I am not totally sure that it is the best practise, but it's getting the job done.

5. Enjoy 🤗

## Contribute

You are very welcome to contribute to this template repository by opening a pull request against the main branch.
