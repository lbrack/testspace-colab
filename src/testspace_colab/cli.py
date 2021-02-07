"""Console script for testspace_colab."""
import sys
import click
import yaml
import json
import pprint
import logging
import testspace_colab.ts_log as log_module
import testspace_colab.client as client_module
import testspace_colab.lib as lib_module
import testspace_colab.utils as utils_module
import testspace_colab.elk as elk_module


logger = log_module.get_logger("cli")

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
@click.option("-d", "--debug", is_flag=True, help="debug")
def main(debug):
    """Console script for testspace_colab."""
    if debug:
        log_module.set_log_level(logging.DEBUG)


@main.resultcallback()
def process_result(result, **kwargs):
    """We use this to erase any log file - this is only called if the command is successful"""
    log_module.remove_log_file()


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
@click.option(
    "-f",
    "--format",
    type=click.Choice(["tabular", "yaml", "json"], case_sensitive=False),
    help="output format",
)
@click.option(
    "-o",
    "--output-file",
    default=None,
    type=click.Path(writable=True, file_okay=True, dir_okay=False, resolve_path=True),
    help="output file",
)
@click.option("-l", "--long", is_flag=True, help="Do not filter any column")
def get(args, long, output_file, format):
    """Performs a get request to the test space server and presents the
    response in a tabular manner.

    The first positional argument is the resource type of a given endpoint.
    The following positional parameters are passed as argument to the request.
    If the positional argument contains an `=` sign it will be sent as a keyword
    argument (kwarg) ortherwise each argument are sent as positional arguments

    There should be no spaces surrounding the '=' sign when specifying parameters.

    \b
    Examples:
    \b
        ts-colab get result result=test_data project=samples space=main
        ts-colab get result test_data samples main
        ts-colab get result test_data space=main # use the default project

    By default, certain column are filtered such as creation data, etc. Use the
    --long option to disable filtering

    For the list of available resources, check https://github.com/s2technologies/testspace-python

    \b
    Examples:
    \b
        ts-colab get projects
        ts-colab get spaces project=foo

    To obtain a complete report for a given result, you can use the built-in method

    \b
        ts-colab get result_details test_data -o dump.json -f json

    This will not only fetch the result meta-data but also the complete report
    consisting of suite and test case details and annotation.



    """

    if not format:
        format = "tabular"
    try:
        args[0]
    except IndexError:
        raise click.ClickException(
            "an endpoint is required e.g. project, projects, space ..."
        )
    kwargs = dict()
    pargs = list()
    for index in range(1, len(args)):
        if "=" in args[index]:
            key, value = args[index].split("=")
            kwargs[key.strip()] = value.strip()
        else:
            pargs.append(args[index])

    # Build the client
    client = lib_module.API()

    click.secho(f"URL={client.url}", bold=True)

    logger.debug(f"api->get_{args[0]}({pargs}, {kwargs})")

    try:
        response = client.__getattr__(f"get_{args[0]}")(*pargs, **kwargs)
    except AttributeError as attribute_error:
        logger.exception(attribute_error)
        if "'Testspace' object has no attribute" in str(attribute_error):
            raise click.ClickException(f"no method '{args[0]}' to access resource")
        raise click.ClickException(attribute_error)

    if format == "tabular":
        utils_module.json_to_table(
            json_data=response, ignore_columns=None if long else IGNORE_COLUMNS
        )
    elif format == "yaml":
        print(yaml.dump(response))
    else:
        pprint.pprint(response)

    if output_file:
        click.secho(f"saving response as json to {output_file}", fg="blue", nl=False)
        try:
            with open(output_file, "w") as file_handle:
                json.dump(response, file_handle, indent=4)
        except Exception as write_exception:
            logger.exception(write_exception)
            raise click.ClickException(f"failed {write_exception}")
        click.secho(" Done!", fg="green")


@main.group()
def elk():
    """command group to control the Elastic Search start"""


@elk.command()
def start():
    """"""
    elk_client = elk_module.ELK()
    click.secho("starting ... be patient", fg="blue")
    try:
        elk_client.start()
    except IOError as error:
        raise click.ClickException(f"Failed to start ELK {error}")
    click.secho(f"ELK Container started ID={elk_client.container.id}", fg="green")


@elk.command()
def stop():
    elk_client = elk_module.ELK()
    click.secho("stopping ... be patient", fg="blue")
    try:
        elk_client.stop()
    except IOError as error:
        raise click.ClickException(f"Failed to stop ELK {error}")
    click.secho("ELK stopped", fg="green")


@elk.command()
def health():
    elk_client = elk_module.ELK()
    click.secho("getting cluster health", fg="blue")
    health = elk_client.get_health()
    if health:
        print(yaml.dump(health))
        click.secho("ok", fg="green")
    else:
        click.secho("unavailable", fg="red")


@elk.command()
def info():
    elk_client = elk_module.ELK()
    if not elk_client.container:
        click.secho("container not running", fg="yellow")
    else:
        click.secho(f"container status {elk_client.container.status}")
        if elk_client.elastic_search:
            click.secho("elastic search info", fg="blue")
            print(yaml.dump(elk_client.elastic_search.info()))
            click.secho("Done", fg="green")
        else:
            click.secho("elastic search not available", fg="yellow")


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
