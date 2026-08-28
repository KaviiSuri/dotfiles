#!/usr/bin/env python3
"""Focused regression tests for the source-owned input gate configuration."""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import tomllib
import unittest


ROOT = Path(os.environ.get("INPUT_GATE_ROOT", Path(__file__).parents[1]))


def caps_manipulators():
    config = json.loads(
        (ROOT / "dot_config/private_karabiner/private_karabiner.json").read_text()
    )
    manipulators = (
        manipulator
        for profile in config["profiles"]
        for rule in profile.get("complex_modifications", {}).get("rules", [])
        for manipulator in rule.get("manipulators", [])
    )
    return [
        manipulator
        for manipulator in manipulators
        if manipulator.get("from", {}).get("key_code") == "caps_lock"
    ]


class KarabinerInputGateTest(unittest.TestCase):
    def test_caps_is_escape_when_tapped_and_super_for_chords(self):
        caps = caps_manipulators()
        self.assertEqual(len(caps), 1, "Expected one global Caps Lock manipulator")
        manipulator = caps[0]

        self.assertEqual(manipulator["to_if_alone"], [{"key_code": "escape"}])
        self.assertEqual(
            manipulator["from"].get("modifiers"), {"optional": ["any"]}
        )

        self.assertEqual(len(manipulator["to"]), 1, "Expected one lazy Super event")
        hold_event = manipulator["to"][0]
        hold_modifiers = {hold_event["key_code"], *hold_event.get("modifiers", [])}
        self.assertTrue(
            {"left_control", "left_option"}.issubset(hold_modifiers),
            f"Caps chord must emit Control+Option, got {sorted(hold_modifiers)}",
        )
        self.assertTrue(hold_event.get("lazy"), "Caps tap must not leak a modifier")

        self.assertNotIn(
            "to_if_held_down",
            manipulator,
            "A held threshold must not suppress Escape for slower Caps taps",
        )
        # Karabiner's documented default is 1000 ms. Keeping it explicit accepts
        # deliberate Caps taps; another key still cancels the tap immediately.
        self.assertEqual(
            manipulator.get("parameters"),
            {"basic.to_if_alone_timeout_milliseconds": 1000},
        )

    def test_caps_rule_has_no_application_condition(self):
        application_condition_types = {
            "frontmost_application_if",
            "frontmost_application_unless",
        }
        condition_types = set()
        for manipulator in caps_manipulators():
            condition_types.update(
                condition.get("type")
                for condition in manipulator.get("conditions", [])
            )

        self.assertTrue(application_condition_types.isdisjoint(condition_types))


class TmuxInputGateTest(unittest.TestCase):
    def test_source_replaces_old_prefixes_and_preserves_send_prefix(self):
        source = (ROOT / "dot_config/tmux/options.conf").read_text()

        self.assertRegex(source, r"(?m)^set\s+-g\s+prefix\s+C-M-a$")
        self.assertRegex(source, r"(?m)^unbind-key\s+C-a$")
        self.assertRegex(source, r"(?m)^unbind-key\s+C-b$")
        self.assertRegex(source, r"(?m)^bind-key\s+C-M-a\s+send-prefix$")
        self.assertIsNone(re.search(r"(?m)^bind-key\s+C-[ab]\s+send-prefix$", source))

    def test_disposable_server_has_only_the_super_send_prefix_binding(self):
        tmux = shutil.which("tmux")
        if tmux is None:
            self.skipTest("tmux is unavailable")

        config = ROOT / "dot_config/tmux/options.conf"
        # tmux uses a Unix socket, whose macOS path limit is easy to exceed under
        # the default per-user temporary directory.
        with tempfile.TemporaryDirectory(prefix="igt-", dir="/tmp") as temp_dir:
            environment = {**os.environ, "TMUX_TMPDIR": temp_dir}
            command = [tmux, "-L", "input-gate-test"]
            try:
                subprocess.run(
                    [*command, "-f", str(config), "new-session", "-d", "-s", "test"],
                    env=environment,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                prefix = subprocess.run(
                    [*command, "show-options", "-gv", "prefix"],
                    env=environment,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                prefix_keys = subprocess.run(
                    [*command, "list-keys", "-T", "prefix"],
                    env=environment,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout
            finally:
                subprocess.run(
                    [*command, "kill-server"],
                    env=environment,
                    check=False,
                    capture_output=True,
                )

        self.assertEqual(prefix, "C-M-a")
        send_prefix_keys = re.findall(
            r"(?m)^bind-key\s+-T\s+prefix\s+(\S+)\s+send-prefix$", prefix_keys
        )
        self.assertEqual(send_prefix_keys, ["C-M-a"])
        self.assertNotRegex(prefix_keys, r"(?m)^bind-key\s+-T\s+prefix\s+C-[ab]\s")


class ApplicationPrefixTest(unittest.TestCase):
    def test_herdr_uses_super_prefix(self):
        with (ROOT / "dot_config/herdr/config.toml").open("rb") as config_file:
            config = tomllib.load(config_file)

        self.assertEqual(config["keys"]["prefix"], "ctrl+alt+a")

    def test_wezterm_uses_super_leader(self):
        source = (ROOT / "dot_config/wezterm/wezterm.lua").read_text()
        leader = re.search(
            r'config\.leader\s*=\s*\{\s*key\s*=\s*"a"\s*,\s*'
            r'mods\s*=\s*"([^"]+)"\s*,\s*timeout_milliseconds\s*=\s*(\d+)\s*\}',
            source,
        )

        self.assertIsNotNone(leader, "WezTerm leader declaration is missing")
        self.assertEqual(leader.group(1), "CTRL|ALT")
        self.assertEqual(leader.group(2), "2000")


if __name__ == "__main__":
    unittest.main()
