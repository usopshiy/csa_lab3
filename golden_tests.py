import json
import logging
import os
import tempfile

import pytest
from src.translator import translate
from src.machine import simulate


@pytest.mark.golden_test("./golden/*.yml")
def test_bar(golden, caplog):
    caplog.set_level(logging.DEBUG)

    with tempfile.TemporaryDirectory() as tmpdir:
        source_file = os.path.join(tmpdir, "source.asm")
        target_file1 = os.path.join(tmpdir, "data.json")
        target_file2 = os.path.join(tmpdir, "instr.json")
        input_token = [ord(i) for i in golden["stdin"].rstrip("\n")]


        with open(source_file, "w", encoding="utf-8") as file:
            file.write(golden["source_code"])
        translate(source_file, target_file1, target_file2)
        print("=" * 5)
        data_dict = json.load(open(target_file1, encoding="utf-8"))
        instr_dict = json.load(open(target_file2, encoding="utf-8"))
        simulate(instr_dict, data_dict, input_token)

        with open(target_file2, encoding="utf-8") as file:
            human_readable = file.read()

        with open(target_file1, encoding="utf-8") as file:
            human_readable1 = file.read()

        assert human_readable.rstrip("\n") == golden.out["instr"].rstrip("\n")
        assert human_readable1.rstrip("\n") == golden.out["data"].rstrip("\n")
        open("file_log.txt", "w").write(caplog.text)
        assert caplog.text.rstrip("\n") == golden.out["logs"].rstrip("\n")