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


def karabiner_manipulators():
    config = json.loads(
        (ROOT / "dot_config/private_karabiner/private_karabiner.json").read_text()
    )
    return [
        manipulator
        for profile in config["profiles"]
        for rule in profile.get("complex_modifications", {}).get("rules", [])
        for manipulator in rule.get("manipulators", [])
    ]


def manipulators_for(key_code):
    return [
        manipulator
        for manipulator in karabiner_manipulators()
        if manipulator.get("from", {}).get("key_code") == key_code
    ]


class KarabinerInputGateTest(unittest.TestCase):
    def test_caps_is_escape_when_tapped_and_control_for_chords(self):
        caps = manipulators_for("caps_lock")
        self.assertEqual(len(caps), 1, "Expected one global Caps Lock manipulator")
        manipulator = caps[0]

        self.assertEqual(manipulator["to_if_alone"], [{"key_code": "escape"}])
        self.assertEqual(
            manipulator["from"].get("modifiers"), {"optional": ["any"]}
        )

        self.assertEqual(
            manipulator["to"],
            [{"key_code": "left_control", "lazy": True}],
            "Caps chords must emit exactly Control, never Option",
        )

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

    def test_left_option_is_global_super_and_preserves_incoming_modifiers(self):
        left_option = manipulators_for("left_option")
        self.assertEqual(
            len(left_option), 1, "Expected one global Left Option manipulator"
        )
        manipulator = left_option[0]

        self.assertEqual(
            manipulator["from"],
            {
                "key_code": "left_option",
                "modifiers": {"optional": ["any"]},
            },
            "Optional modifiers must remain available to the output, including Shift",
        )
        self.assertEqual(
            manipulator["to"],
            [{"key_code": "left_control", "modifiers": ["left_option"]}],
        )

    def test_right_option_is_not_remapped(self):
        self.assertEqual(manipulators_for("right_option"), [])

    def test_input_gate_is_global(self):
        for manipulator in (
            *manipulators_for("caps_lock"),
            *manipulators_for("left_option"),
        ):
            self.assertNotIn("conditions", manipulator)


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
