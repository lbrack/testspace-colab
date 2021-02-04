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


def xml_to_json(xml_data, depth=0):
    """converts an object of type element

    :param xml_data:
    :param depth:
    :return:
    """
    json_data = dict()
    element_type = xml_data.tag.replace("test_", "")
    json_data[element_type] = xml_data.attrib

    children_type = "unknown"

    if xml_data.tag == "test_suite":
        children_type = "cases"
        click.secho("  " * depth + f"[suite] {xml_data.attrib['name']}", fg="blue")
    elif xml_data.tag == "test_case":
        children_type = "annotations"
        click.secho("  " * depth + f"[case] {xml_data.attrib['name']}", fg="green")
    elif xml_data.tag == "annotation":
        children_type = "children"
        click.secho("  " * depth + f"[{xml_data.tag}] ", fg="yellow")
    else:
        click.secho("  " * depth + f"[{xml_data.tag}] ", fg="yellow")

    json_data[element_type][children_type] = []

    for children in xml_data:
        json_data[element_type][children_type].append(
            xml_to_json(xml_data=children, depth=depth + 1)
        )
    return json_data
