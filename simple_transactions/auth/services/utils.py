from functools import wraps


def model_row_to_dict(row) -> dict:
    formatted_row = dict(row.__dict__)
    formatted_row.pop("_sa_instance_state", None)
    return formatted_row
