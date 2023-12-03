import os
import sys
import argparse
import time
import datetime

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

from utils import open_config


def get_arguments():
    args = argparse.ArgumentParser()
    args.add_argument("--config", default=os.path.join(ROOT_DIR, "config.yaml"))
    args.add_argument(
        "--version",
        default=datetime.datetime.fromtimestamp(int(time.time())).strftime(
            "%Y-%m-%dT%H-%M-%S"
        ),
    )
    return args.parse_args()


def collect_idt_boost_samples(wes_sample_path: str, output_path: str) -> None:
    idt_boost_samples = list()
    columns = list()
    col2idx = dict()
    with open(wes_sample_path) as fh:
        columns = fh.readline().rstrip().split("\t")
        col2idx = {col: idx for idx, col in enumerate(columns)}
        for line in fh:
            if line.startswith("#"):
                continue

            row = line.rstrip().split("\t")
            if len(row) <= col2idx["used.for.in-house.freq"]:
                continue

            is_valid = row[col2idx["is.valid.sample"]]
            is_patient = row[col2idx["is.patient"]]
            is_used_for_inhouse_count = row[col2idx["used.for.in-house.freq"]]
            called_by = row[col2idx["called.by"]]
            kit_name = row[col2idx["kit.name"]]

            if (
                is_valid != "1"
                or is_patient != "1"
                or is_used_for_inhouse_count != "1"
                or called_by != "3B"
                or kit_name != "IDT_3B_V1"
            ):
                continue

            idt_boost_samples.append(line)

    fh_output = open(output_path, "w")
    fh_output.write("#" + "\t".join(columns) + "\n")
    fh_output.write("".join(idt_boost_samples))
    fh_output.close()

    return


def main():
    args = get_arguments()
    config = open_config(args.config)

    step_config = config["IDT_BOOST_SAMPLE_COLLECTOR"]

    wes_sample_path = os.path.join(
        ROOT_DIR, "data", step_config["WES_SAMPLE_FILENAME"]
    )
    output_path = os.path.join(
        ROOT_DIR, "data", step_config["IDT_BOOST_SAMPLE_FILENAME"]
    )

    collect_idt_boost_samples(wes_sample_path, output_path)

    return


if __name__ == "__main__":
    main()
