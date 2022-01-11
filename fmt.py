"""
    Output formatting
    Author: Harel Segev
    31/12/2021
"""

from datetime import timezone, datetime, timedelta


def to_datetime(timestamp: int):
    return datetime(1601, 1, 1) + timedelta(microseconds=(timestamp / 10))


def to_epoch(timestamp: int):
    return to_datetime(timestamp).replace(tzinfo=timezone.utc).timestamp()


def to_iso(timestamp: int):
    return to_datetime(timestamp).replace(tzinfo=timezone.utc).isoformat()


COMMON_FIELDS = {
    "index": lambda index_entry: index_entry["FILE_REFERENCE"]["FileRecordNumber"],
    "sequence": lambda index_entry: index_entry["FILE_REFERENCE"]["SequenceNumber"],

    "size": lambda index_entry: index_entry["RealSize"],
    "alloc_size": lambda index_entry: index_entry["AllocatedSize"],

    "cr_time": lambda index_entry: index_entry["CreationTime"],
    "m_time": lambda index_entry: index_entry["LastModificationTime"],
    "a_time": lambda index_entry: index_entry["LastAccessTime"],
    "c_time": lambda index_entry: index_entry["LastMftChangeTime"],
}

OUTPUT_FORMATS = {
    "csv":
    {
        "fmt": "{slack},\"{full_path}\",{flags},{index},{sequence},"
               "{size},{alloc_size},{cr_time},{m_time},{a_time},{c_time}\n",

        "header": "Source,Path,Flags,FileNumber,SequenceNumber,"
                  "Size,AllocatedSize,CreationTime,ModificationTime,AccessTime,ChangeTime\n",

        "fields":
        {
            "flags": lambda index_entry: "|".join
            (
                [flag for flag in index_entry["Flags"] if index_entry["Flags"][flag] and flag != "_flagsenum"]
            ),

            "slack": lambda index_entry: "Index Slack" if index_entry["IsSlack"] else "Index Record"

        } | COMMON_FIELDS,

        "adapted_fields": {"cr_time": to_iso, "m_time": to_iso, "a_time": to_iso, "c_time": to_iso}
    },

    "bodyfile":
    {
        "fmt": "0|{full_path} ($I30){slack}|{index}|{mode_part1}"
               "{mode_part2}|0|0|{size}|{a_time}|{m_time}|{c_time}|{cr_time}\n",

        "header": "",

        "fields":
        {
            "mode_part1": lambda index_entry: "d/-" if index_entry["Flags"]["DIRECTORY"] else "r/-",
            "mode_part2": lambda index_entry: 3 * "{}{}{}".format
            (
              "r" if not index_entry["Flags"]["READ_ONLY"] else "-",
              "w" if not index_entry["Flags"]["HIDDEN"] else "-",
              "x"
            ),

            "slack": lambda index_entry: " (slack)" if index_entry["IsSlack"] else ""

        } | COMMON_FIELDS,

        "adapted_fields": {"cr_time": to_epoch, "m_time": to_epoch, "a_time": to_epoch, "c_time": to_epoch},
    }
}


def populate_fmt_dict(fmt_dict, index_entry, output_format):
    output_fields = OUTPUT_FORMATS[output_format]["fields"]
    adapted_fields = OUTPUT_FORMATS[output_format]["adapted_fields"]

    for field in output_fields:
        fmt_dict[field] = output_fields[field](index_entry)

        if field in adapted_fields:
            fmt_dict[field] = adapted_fields[field](fmt_dict[field])


def get_entry_output(index_entry, parent_path, output_format):
    fmt_dict = {
        "full_path": parent_path + "/" + index_entry["FilenameInUnicode"]
    }

    populate_fmt_dict(fmt_dict, index_entry, output_format)
    return OUTPUT_FORMATS[output_format]["fmt"].format(**fmt_dict)


def get_format_header(output_format):
    return OUTPUT_FORMATS[output_format]["header"]