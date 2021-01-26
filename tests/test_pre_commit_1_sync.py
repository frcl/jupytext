import pytest
from git.exc import HookExecutionError
from nbformat.v4.nbbase import new_markdown_cell
from pre_commit.main import main as pre_commit

from jupytext import read, write
from jupytext.cli import jupytext

from .utils import skip_pre_commit_tests_on_windows


@skip_pre_commit_tests_on_windows
def test_pre_commit_hook_sync(
    tmpdir,
    cwd_tmpdir,
    tmp_repo,
    capsys,
    jupytext_repo_root,
    jupytext_repo_rev,
    python_notebook,
):
    pre_commit_config_yaml = f"""
repos:
- repo: {jupytext_repo_root}
  rev: {jupytext_repo_rev}
  hooks:
  - id: jupytext
    args: [--sync]
"""
    tmpdir.join(".pre-commit-config.yaml").write(pre_commit_config_yaml)

    tmp_repo.git.add(".pre-commit-config.yaml")
    pre_commit(["install", "--install-hooks", "-f"])

    # write a test notebook and sync it to py:percent
    nb = python_notebook
    write(nb, "test.ipynb")

    jupytext(["--set-formats", "ipynb,py:percent", "test.ipynb"])

    # try to commit it, should fail because the py version hasn't been added
    tmp_repo.git.add("test.ipynb")
    with pytest.raises(
        HookExecutionError,
        match="Please run 'git add test.py'",
    ):
        tmp_repo.index.commit("failing")

    # add the py file, now the commit will succeed
    tmp_repo.git.add("test.py")
    tmp_repo.index.commit("passing")
    assert "test.ipynb" in tmp_repo.tree()
    assert "test.py" in tmp_repo.tree()

    # modify the ipynb file
    nb = read("test.ipynb")
    nb.cells.append(new_markdown_cell("A new cell"))
    write(nb, "test.ipynb")

    tmp_repo.git.add("test.ipynb")

    # We try to commit one more time, this updates the py file
    with pytest.raises(
        HookExecutionError,
        match="files were modified by this hook",
    ):
        tmp_repo.index.commit("failing")

    # the text file has been updated
    assert "A new cell" in tmpdir.join("test.py").read()

    # trying to commit should fail again because we forgot to add the .py version
    with pytest.raises(HookExecutionError, match="Please run 'git add test.py'"):
        tmp_repo.index.commit("still failing")

    nb = read("test.ipynb")
    assert len(nb.cells) == 2

    # add the text file, now the commit will succeed
    tmp_repo.git.add("test.py")
    tmp_repo.index.commit("passing")
