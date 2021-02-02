"""

"""
import click


def json_to_table(json, ignore_columns=None):
    columns = dict()
    for name in json[0].keys():
        if ignore_columns and name in ignore_columns:
            continue
        columns[name] = len(name)

    for row in json:
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
    for row in json:
        for name, value in row.items():
            if name not in columns:
                continue
            click.secho(f"{str(value):{columns[name]}} | ", bold=True, nl=False)
        click.secho(nl=True)
