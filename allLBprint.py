#!/usr/bin/env python3
#python3   allLBprint.py --csv members.csv  --no-printer
#python3   allLBprint.py --csv members.cs
import argparse
import csv
from types import SimpleNamespace

from src.label import creator as label_creator
from src.label import printer as label_printer
from src.backend import label_data
from src.backend.member import Member



def create_fake_member(member_number: str, member_name: str):
    member = Member.__new__(Member)

    object.__setattr__(member, "member_number", int(member_number))
    object.__setattr__(member, "member_name", member_name)

    # method still needed
    object.__setattr__(member, "get_name", lambda: member_name)

    return member

def parse_inline(members_str):
    members = []
    for item in members_str.split(","):
        if ":" in item:
            number, name = item.split(":", 1)
            members.append((number.strip(), name.strip()))
        else:
            members.append((item.strip(), f"Member {item.strip()}"))
    return members


def parse_csv(path):
    members = []
    with open(path, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                members.append((row[0].strip(), row[1].strip()))
    return members


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "members",
        nargs="?",
        help="Comma separated list like 1234:Gert,5678:Anna"
    )
    parser.add_argument(
        "--csv",
        help="CSV file with format: member_number,name"
    )
    parser.add_argument(
        "--no-printer",
        action="store_true"
    )

    args = parser.parse_args()

    members = []

    if args.members:
        members.extend(parse_inline(args.members))

    if args.csv:
        members.extend(parse_csv(args.csv))

    if not members:
        print("No members provided")
        return

    for member_number, member_name in members:
        print(f"Processing #{member_number} ({member_name})")

        try:
            fake_member = create_fake_member(member_number, member_name)

            label = label_data.BoxLabel.from_member(fake_member)

            uploaded_label = SimpleNamespace(
                label=label,
                public_observation_url="https://medlem.kalmarmakerspace.se"
            )

            label_image = label_creator.create_label(uploaded_label)

            if args.no_printer:
                filename = f"label_{member_number}.png"
                label_image.label.save(filename)
                print(f"Saved {filename}")
            else:
                label_printer.print_label(label_image.label)

        except Exception as e:
            print(f"Error for {member_number}: {e}")


if __name__ == "__main__":
    main()

