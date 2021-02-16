"""

"""
import click
import testspace_colab.ts_log

logger = testspace_colab.ts_log.get_logger("utils")


def json_to_table(json_data, ignore_columns=None):
    columns = dict()

    if isinstance(json_data, dict):
        tmp = json_data
        json_data = list()
        json_data.append(tmp)

    for name in json_data[0].keys():
        if ignore_columns and name in ignore_columns:
            continue
        columns[name] = len(name)

    for row in json_data:
        for name, value in row.items():
            if name not in columns:
                continue
            if value:
                value = len(str(value))
                if columns[name] < value:
                    columns[name] = value

    for name, lenght in columns.items():
        click.secho(f"{name.upper():{lenght}} | ", fg="green", nl=False)
    click.secho(nl=True)
    for row in json_data:
        for name, value in row.items():
            if name not in columns:
                continue
            click.secho(f"{str(value):{columns[name]}} | ", bold=True, nl=False)
        click.secho(nl=True)


def xml_to_json(xml_data, progress_callback=None):
    """converts an object of type element
    :param xml_data:
    :param progress_callback: a progress callback function
    :return:
    """
    json_data = dict()
    element_type = xml_data.tag.replace("test_", "")
    json_data[element_type] = xml_data.attrib

    children_type = "unknown"

    if xml_data.tag == "test_suite":
        children_type = "cases"
        if progress_callback:
            progress_callback(object_type="suites", object_count=1)
    elif xml_data.tag == "test_case":
        children_type = "annotations"
        if progress_callback:
            progress_callback(object_type="cases", object_count=1)
    elif xml_data.tag == "annotation":
        children_type = "children"
        if progress_callback:
            progress_callback(object_type="annotations", object_count=1)
    else:
        if progress_callback:
            progress_callback(object_type=xml_data.tag, object_count=1)
    json_data[element_type][children_type] = []

    for children in xml_data:
        children_data = xml_to_json(
            xml_data=children, progress_callback=progress_callback
        )
        for children_datum in children_data.values():
            json_data[element_type][children_type].append(children_datum)
    return json_data
