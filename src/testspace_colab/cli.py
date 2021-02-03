"""Console script for testspace_colab."""
import sys
import click
import yaml
import pprint
import testspace_colab.client as client_module
import testspace_colab.lib as lib_module
import testspace_colab.utils as utils_module

VERSION = f"{lib_module.API.get_version()} client {client_module.Binary().version}"

IGNORE_COLUMNS = [
    "created_at",
    "updated_at",
    "result_set_aggregation",
    "sandbox",
    "min_run_period",
    "sequence_number",
    "build_url",
    "pinned",
    "space_id",
    "commit_id",
    "badges",
    "health",
    "description",
    "user_id",
    "session_suite_counts",
    "session_case_counts",
    "session_failure_counts",
]


@click.group()
@click.version_option(version=VERSION)
def main():
    """Console script for testspace_colab."""
    pass


@main.command()
@click.argument("args", nargs=-1)
@click.option("-v", "--version", is_flag=True, help="client version")
@click.option("-h", "--help", is_flag=True, help="client help")
def client(args, version, help):
    """Runs the client with the specified parameters"""
    binary = client_module.Binary()
    if version:
        binary.exec("--version")
    elif help:
        binary.exec("--help")
    else:
        exception = click.ClickException(f"'{' '.join(args)}' failed")
        exception.exit_code = binary.exec(args, return_code=None)
        if exception.exit_code:
            raise exception


@main.command()
@click.argument("args", nargs=-1)
@click.option('-f', '--output-format',
              type=click.Choice(['tabular', 'yaml', 'raw'], case_sensitive=False),
              help="output formar")
@click.option("-l", "--long", is_flag=True, help="Do not filter any column")
def get(args, long, output_format):
    """Performs a get request to the test space server and presents the
    response in a tabular manner.

    The first positional argument is the resource type of a given endpoint.
    The following positional parameters are passed as argument to the request.
    There should be no spaces surrounding the '=' sign when specifying parameters.

    By default, certain column are filtered such as creation data, etc. Use the
    --long option to disable filtering

    For the list of available resources, check https://github.com/s2technologies/testspace-python

    \b
    Examples:
    \b
        ts-colab get projects
        ts-colab get spaces project=foo
    """
    if not output_format:
        output_format = 'tabular'
    try:
        args[0]
    except IndexError:
        raise click.ClickException(
            "an endpoint is required e.g. project, projects, space ..."
        )
    kwargs = dict()
    pargs = list()
    for index in range(1, len(args)):
        if '=' in args[index]:
            key, value = args[index].split("=")
            kwargs[key.strip()] = value.strip()
        else:
            pargs.append(args[index])

    # Build the client
    client = lib_module.API()


    click.secho(f"URL={client.url}", bold=True)

    try:
        response = client.__getattr__(f"get_{args[0]}")(*pargs, **kwargs)
    except AttributeError as attribute_error:
        if "'Testspace' object has no attribute" in str(attribute_error):
            raise click.ClickException(f"no method to access resourse '{args[0]}'")
        raise click.ClickException(attribute_error)

    if output_format == 'tabular':
        utils_module.json_to_table(
            json_data=response, ignore_columns=None if long else IGNORE_COLUMNS
        )
    elif output_format == 'yaml':
        print(yaml.dump(response))
    else:
        pprint.pprint(response)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
