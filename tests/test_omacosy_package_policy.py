#!/usr/bin/env python3
"""Tests for the source-owned omacosy pin and invocation gate."""

import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import tomllib
import unittest


ROOT = Path(__file__).parents[1]
PIN = "93ac20082fa21339978550faccb03381087f3a77"
PRIVATE_REPOSITORY = "git@github-personal:KaviiSuri/omacosy.git"
PUBLIC_UPSTREAM = "https://github.com/paulsp94/omacosy.git"
WRAPPER_SOURCE = ROOT / "dot_local/bin/executable_omacosy-desktop.tmpl"
POLICY_SOURCE = ROOT / "dot_config/omacosy/package-policy.toml.tmpl"
SYSTEM_PATH = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"


class OmacosyPackagePolicyTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="omacosy-policy-", dir="/tmp")
        self.home = Path(self.temp_dir.name)
        self.wrapper = self.home / "omacosy-desktop"
        self.policy_file = self.home / "package-policy.toml"
        self.checkout = self.home / "code/KaviiSuri/omacosy"
        self.git_shim_dir = self.home / "test-bin"
        self.args_file = self.home / "args"
        self.cache_dir = self.home / "cache"
        self.config_file = self.home / "config/chezmoi.toml"
        self.state_file = self.home / "state/chezmoi.boltdb"

        directories = {
            "TMPDIR": self.home / "tmp",
            "XDG_CONFIG_HOME": self.home / "config",
            "XDG_CACHE_HOME": self.home / "cache",
            "XDG_STATE_HOME": self.home / "state",
        }
        for directory in directories.values():
            directory.mkdir(parents=True)
        self.config_file.write_text("")
        self.environment = {
            "HOME": str(self.home),
            "PATH": SYSTEM_PATH,
            "LANG": "C",
            "LC_ALL": "C",
            "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_CONFIG_NOSYSTEM": "1",
            **{name: str(path) for name, path in directories.items()},
        }

        self.render(WRAPPER_SOURCE, self.wrapper)
        self.render(POLICY_SOURCE, self.policy_file)
        self.wrapper.chmod(0o755)

        self.checkout.mkdir(parents=True)
        self.run_command(["git", "init", "--quiet", str(self.checkout)])
        self.configure_repository(self.checkout)

        fixture = self.checkout / "fixture"
        fixture.write_text("disposable repository\n")
        executable = self.checkout / "bin/omacosy"
        executable.parent.mkdir()
        executable.write_text(
            "#!/bin/sh\n"
            "printf '%s\\0' \"$@\" >\"$OMACOSY_TEST_ARGS_FILE\"\n"
        )
        executable.chmod(0o755)
        self.run_command(
            ["git", "-C", str(self.checkout), "add", "fixture", "bin/omacosy"]
        )
        self.run_command(
            ["git", "-C", str(self.checkout), "commit", "--quiet", "-m", "fixture"]
        )
        self.run_command(
            [
                "git",
                "-C",
                str(self.checkout),
                "remote",
                "add",
                "origin",
                PRIVATE_REPOSITORY,
            ]
        )

        real_git = shutil.which("git", path=SYSTEM_PATH)
        self.assertIsNotNone(real_git)
        self.git_shim_dir.mkdir()
        git_shim = self.git_shim_dir / "git"
        git_shim.write_text(
            "#!/bin/sh\n"
            "if [ \"${3-}\" = rev-parse ] && [ \"${4-}\" = --verify ] "
            "&& [ \"${5-}\" = HEAD ]; then\n"
            "  printf '%s\\n' \"$OMACOSY_TEST_HEAD\"\n"
            "  exit 0\n"
            "fi\n"
            f'exec "{real_git}" "$@"\n'
        )
        git_shim.chmod(0o755)

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_command(self, command):
        return subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            env=self.environment,
        )

    def render(self, source, output):
        self.run_command(
            [
                "chezmoi",
                "execute-template",
                "--config",
                str(self.config_file),
                "--config-format",
                "toml",
                "--cache",
                str(self.cache_dir),
                "--persistent-state",
                str(self.state_file),
                "--source",
                str(ROOT),
                "--destination",
                str(self.home),
                "--file",
                str(source),
                "--output",
                str(output),
            ]
        )

    def configure_repository(self, repository):
        self.run_command(
            ["git", "-C", str(repository), "config", "user.name", "Policy Test"]
        )
        self.run_command(
            [
                "git",
                "-C",
                str(repository),
                "config",
                "user.email",
                "policy-test@example.invalid",
            ]
        )

    def commit_all(self, message):
        self.run_command(["git", "-C", str(self.checkout), "add", "--all"])
        self.run_command(
            ["git", "-C", str(self.checkout), "commit", "--quiet", "-m", message]
        )

    def invoke(self, *arguments, head=PIN):
        environment = {
            **self.environment,
            "PATH": f"{self.git_shim_dir}{os.pathsep}{SYSTEM_PATH}",
            "OMACOSY_TEST_HEAD": head,
            "OMACOSY_TEST_ARGS_FILE": str(self.args_file),
        }
        return subprocess.run(
            [str(self.wrapper), *arguments],
            env=environment,
            capture_output=True,
            text=True,
        )

    def assert_refused(self, expected_error, *, head=PIN):
        result = self.invoke("inspect", head=head)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(expected_error, result.stderr)
        self.assertFalse(self.args_file.exists())

    def test_rendered_policy_contains_the_reviewed_source_pin(self):
        with self.policy_file.open("rb") as policy_stream:
            policy = tomllib.load(policy_stream)

        self.assertEqual(
            policy,
            {
                "private_repository": PRIVATE_REPOSITORY,
                "public_upstream": PUBLIC_UPSTREAM,
                "tested_commit": PIN,
                "checkout_path": "~/code/KaviiSuri/omacosy",
            },
        )

    def test_brewfile_keeps_amethyst_and_adds_official_aerospace_cask(self):
        brewfile = (ROOT / "dot_Brewfile").read_text()

        self.assertRegex(brewfile, r'(?m)^tap "nikitabobko/tap"$')
        self.assertRegex(brewfile, r'(?m)^cask "nikitabobko/tap/aerospace"$')
        self.assertRegex(brewfile, r'(?m)^cask "amethyst"$')

    def test_clean_exact_pin_invokes_checkout_and_preserves_arguments(self):
        arguments = ["inspect", "argument with spaces", "", "*.toml", "--flag=value"]
        result = self.invoke(*arguments)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            self.args_file.read_bytes().split(b"\0")[:-1],
            [argument.encode() for argument in arguments],
        )

    def test_absent_checkout_is_refused(self):
        shutil.rmtree(self.checkout)
        self.assert_refused("checkout not found")

    def test_non_repository_is_refused(self):
        shutil.rmtree(self.checkout / ".git")
        self.assert_refused("is not a Git worktree")

    def test_wrong_worktree_root_is_refused(self):
        shutil.rmtree(self.checkout / ".git")
        repository_root = self.checkout.parent
        self.run_command(["git", "init", "--quiet", str(repository_root)])
        self.assert_refused("is not the root of its Git worktree")

    def test_wrong_head_is_refused(self):
        wrong_head = "0" * 40
        self.assert_refused(f"expected {PIN}, found {wrong_head}", head=wrong_head)

    def test_missing_origin_is_refused(self):
        self.run_command(["git", "-C", str(self.checkout), "remote", "remove", "origin"])
        self.assert_refused("origin is missing")

    def test_multiple_origin_urls_are_refused(self):
        self.run_command(
            [
                "git",
                "-C",
                str(self.checkout),
                "config",
                "--add",
                "remote.origin.url",
                "https://github.com/KaviiSuri/omacosy.git",
            ]
        )
        self.assert_refused("origin refusal")

    def test_unapproved_origin_is_refused(self):
        self.run_command(
            [
                "git",
                "-C",
                str(self.checkout),
                "remote",
                "set-url",
                "origin",
                "https://github.com/attacker/omacosy.git",
            ]
        )
        self.assert_refused("origin refusal")

    def test_missing_executable_is_refused(self):
        (self.checkout / "bin/omacosy").unlink()
        self.commit_all("remove executable")
        self.assert_refused("expected executable is missing or not executable")

    def test_non_executable_file_is_refused(self):
        (self.checkout / "bin/omacosy").chmod(0o644)
        self.commit_all("remove executable bit")
        self.assert_refused("expected executable is missing or not executable")

    def test_staged_change_is_refused(self):
        (self.checkout / "fixture").write_text("staged change\n")
        self.run_command(["git", "-C", str(self.checkout), "add", "fixture"])
        self.assert_refused("checkout is not clean")

    def test_unstaged_change_is_refused(self):
        (self.checkout / "fixture").write_text("unstaged change\n")
        self.assert_refused("checkout is not clean")

    def test_tracked_deletion_is_refused(self):
        (self.checkout / "fixture").unlink()
        self.assert_refused("checkout is not clean")

    def test_untracked_file_is_refused(self):
        (self.checkout / "untracked").write_text("untracked\n")
        self.assert_refused("checkout is not clean")

    def test_replaced_untracked_executable_is_refused(self):
        self.run_command(
            ["git", "-C", str(self.checkout), "rm", "--cached", "--quiet", "bin/omacosy"]
        )
        (self.checkout / "bin/omacosy").write_text("#!/bin/sh\nexit 0\n")
        (self.checkout / "bin/omacosy").chmod(0o755)
        self.assert_refused("checkout is not clean")

    def test_ignored_untracked_file_is_refused(self):
        (self.checkout / ".gitignore").write_text("ignored.tmp\n")
        self.commit_all("add ignore rule")
        (self.checkout / "ignored.tmp").write_text("still untracked\n")
        self.assert_refused("checkout is not clean")

    def test_rendered_wrapper_has_no_mutating_commands(self):
        wrapper = self.wrapper.read_text()
        forbidden = re.compile(
            r"(?m)^\s*(?:git\s+(?:clone|pull|fetch|checkout|switch|reset)|"
            r"brew(?:\s+bundle|\s+(?:tap|install))|"
            r"omacosy\s+(?:apply|enable|install|update)|"
            r"(?:open|launchctl|kill|pkill)\b)"
        )

        self.assertIsNone(forbidden.search(wrapper))


if __name__ == "__main__":
    unittest.main()
