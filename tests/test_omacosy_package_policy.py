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


ROOT = Path(os.environ.get("OMACOSY_POLICY_ROOT", Path(__file__).parents[1]))
PIN = "93ac20082fa21339978550faccb03381087f3a77"
PRIVATE_REPOSITORY = "git@github-personal:KaviiSuri/omacosy.git"
PUBLIC_UPSTREAM = "https://github.com/paulsp94/omacosy.git"
WRAPPER_SOURCE = ROOT / "dot_local/bin/executable_omacosy-desktop.tmpl"
POLICY_SOURCE = ROOT / "dot_config/omacosy/package-policy.toml.tmpl"


def run(command, **kwargs):
    return subprocess.run(command, check=True, capture_output=True, text=True, **kwargs)


class OmacosyPackagePolicyTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="omacosy-policy-")
        self.home = Path(self.temp_dir.name)
        self.wrapper = self.home / "omacosy-desktop"
        self.policy_file = self.home / "package-policy.toml"
        self.git_shim_dir = self.home / "test-bin"
        self.args_file = self.home / "args"

        run(
            [
                "chezmoi",
                "execute-template",
                "--source",
                str(ROOT),
                "--destination",
                str(self.home),
                "--file",
                str(WRAPPER_SOURCE),
                "--output",
                str(self.wrapper),
            ]
        )
        run(
            [
                "chezmoi",
                "execute-template",
                "--source",
                str(ROOT),
                "--destination",
                str(self.home),
                "--file",
                str(POLICY_SOURCE),
                "--output",
                str(self.policy_file),
            ]
        )
        self.wrapper.chmod(0o755)

        self.checkout = self.home / "code/KaviiSuri/omacosy"
        self.checkout.mkdir(parents=True)
        run(["git", "init", "--quiet", str(self.checkout)])
        run(["git", "-C", str(self.checkout), "config", "user.name", "Policy Test"])
        run(
            [
                "git",
                "-C",
                str(self.checkout),
                "config",
                "user.email",
                "policy-test@example.invalid",
            ]
        )
        (self.checkout / "fixture").write_text("disposable repository\n")
        run(["git", "-C", str(self.checkout), "add", "fixture"])
        run(["git", "-C", str(self.checkout), "commit", "--quiet", "-m", "fixture"])
        run(
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

        executable = self.checkout / "bin/omacosy"
        executable.parent.mkdir()
        executable.write_text(
            "#!/bin/sh\n"
            "printf '%s\\0' \"$@\" >\"$OMACOSY_TEST_ARGS_FILE\"\n"
        )
        executable.chmod(0o755)

        real_git = shutil.which("git")
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

    def invoke(self, *arguments, head=PIN):
        environment = {
            **os.environ,
            "HOME": str(self.home),
            "PATH": f"{self.git_shim_dir}{os.pathsep}{os.environ['PATH']}",
            "OMACOSY_TEST_HEAD": head,
            "OMACOSY_TEST_ARGS_FILE": str(self.args_file),
        }
        return subprocess.run(
            [str(self.wrapper), *arguments],
            env=environment,
            capture_output=True,
            text=True,
        )

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

    def test_exact_pin_invokes_checkout_and_preserves_arguments(self):
        arguments = ["inspect", "argument with spaces", "", "*.toml", "--flag=value"]
        result = self.invoke(*arguments)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.args_file.read_bytes().split(b"\0")[:-1], [
            argument.encode() for argument in arguments
        ])

    def test_head_mismatch_is_refused_before_invocation(self):
        wrong_head = "0" * 40
        result = self.invoke("inspect", head=wrong_head)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(f"expected {PIN}, found {wrong_head}", result.stderr)
        self.assertFalse(self.args_file.exists())

    def test_unapproved_origin_is_refused_before_invocation(self):
        run(
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
        result = self.invoke("inspect")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("origin refusal", result.stderr)
        self.assertFalse(self.args_file.exists())

    def test_non_worktree_is_refused_before_invocation(self):
        shutil.rmtree(self.checkout / ".git")
        result = self.invoke("inspect")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("is not a Git worktree", result.stderr)
        self.assertFalse(self.args_file.exists())

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
