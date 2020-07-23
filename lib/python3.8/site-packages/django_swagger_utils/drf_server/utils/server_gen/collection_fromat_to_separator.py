def collection_format_to_separator(collection_format):
    if collection_format == "multi":
        raise Exception("collection format type multi not supported yet")
    collection_format_mapping = {
        "csv": ",",
        "ssv": " ",
        "tsv": "\\t",
        "pipes": "|"
    }
    return collection_format_mapping.get(collection_format)


def collection_format_to_separator_regex(collection_format):
    if collection_format == "multi":
        raise Exception("collection format type multi not supported yet")
    collection_format_mapping_regex = {
        "csv": ",",
        "ssv": "\s",
        "tsv": "\\t",
        "pipes": "\|"
    }
    return collection_format_mapping_regex.get(collection_format)
