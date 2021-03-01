"""

"""
import os
import gzip
import base64
import pathlib
import click
import testspace_colab.ts_log

logger = testspace_colab.ts_log.get_logger("utils")

PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent.absolute()


def use_test_config():
    """Sets the TS_COLAB_CONFIG_DIR env variable to
    ./tests/.config/test

    See `test <https://lbrack.testspace.com/>` for details

    :return: None
    """
    os.environ["TS_COLAB_CONFIG_DIR"] = str(PROJECT_ROOT / "tests" / ".config" / "test")


def use_samples_config():
    """Sets the TS_COLAB_CONFIG_DIR env variable to
    ./tests/.config/samples

    See `samples <https://samples.testspace.com/>`_ for details

    :return: None
    """
    os.environ["TS_COLAB_CONFIG_DIR"] = str(
        PROJECT_ROOT / "tests" / ".config" / "samples"
    )


def get_notebook_dir():
    return PROJECT_ROOT / "notebooks"


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


def xml_to_json(xml_data, path, progress_callback=None):
    """converts an object of type element
    :param xml_data:
    :param path: Path leading to the XML content
    :param progress_callback: a progress callback function
    :return:
    """
    json_data = dict()
    element_type = xml_data.tag.replace("test_", "")
    json_data[element_type] = xml_data.attrib

    children_type = None

    if xml_data.tag == "test_suite":
        path = (
            f"{path}/{xml_data.attrib['name']}"
            if path
            else f"/{xml_data.attrib['name']}"
        )
        children_type = "cases"
        if progress_callback:
            progress_callback(object_type="suites", object_count=1)
    elif xml_data.tag == "test_case":
        path = (
            f"{path}/{xml_data.attrib['name']}"
            if path
            else f"/{xml_data.attrib['name']}"
        )
        children_type = "annotations"
        if progress_callback:
            progress_callback(object_type="cases", object_count=1)
    elif xml_data.tag == "annotation":
        path = (
            f"{path}/{xml_data.attrib['name']}"
            if path
            else f"/{xml_data.attrib['name']}"
        )
        if isinstance(xml_data.text, str):
            try:
                json_data[element_type]["text"] = gzip.decompress(
                    base64.b64decode(xml_data.text)
                ).decode("utf-8")
            except Exception as extract_error:
                logger.error(
                    f"Failed to decode annotation {path} error -> {extract_error}"
                )
        children_type = "comments"
        if progress_callback:
            progress_callback(object_type="annotations", object_count=1)
    elif xml_data.tag == "comment":
        # The text contains the actual comment
        json_data[element_type]["text"] = xml_data.text
        json_data[element_type]["path"] = path
    else:
        print("What is this")
        if progress_callback:
            progress_callback(object_type=xml_data.tag, object_count=1)

    if children_type:
        json_data[element_type][children_type] = []

        for children in xml_data:
            children_data = xml_to_json(
                xml_data=children, path=path, progress_callback=progress_callback
            )
            for children_datum in children_data.values():
                children_datum["path"] = path if path else "/"
                json_data[element_type][children_type].append(children_datum)
        if not json_data[element_type][children_type]:
            json_data[element_type].pop(children_type)
    else:
        pass

    return json_data
