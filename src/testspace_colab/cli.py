"""Console script for testspace_colab."""
import sys
import os
import platform
import webbrowser
import click
import yaml
import json
import pprint
import pathlib
import logging
import urllib.parse
import jsonpath_ng
import testspace_colab.ts_log as log_module
import testspace_colab.client as client_module
import testspace_colab.lib as lib_module
import testspace_colab.utils as utils_module
import testspace_colab.elk as elk_module


logger = log_module.get_logger("cli")

VERSION = f"{lib_module.API.get_version()} client {client_module.Binary().version} " \
          f"Python {sys.version_info.major}.{sys.version_info.minor} {platform.platform()}"

IGNORE_COLUMNS = [
    "created_at",
    "updated_at",
    "result_set_aggregation",
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
@click.option(
    "-p",
    "--preset",
    type=click.Choice(["none", "samples", "test"], case_sensitive=False),
    help="uses preset configuration for playing around",
)
def main(debug, preset):
    """Console script for testspace_colab."""
    if debug:
        log_module.set_log_level(logging.DEBUG)
    if preset == "test":
        utils_module.use_test_config()
    elif preset == "samples":
        utils_module.use_samples_config()


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
@click.option(
    "-j",
    "--json-path",
    default=None,
    required=False,
    help="json path expression",
)
@click.option("-l", "--long", is_flag=True, help="Do not filter any column")
def get(args, long, output_file, format, json_path):
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

    Extract all test cases or suites from the response
    \b
        ts-colab get result_details test_data -f json -j '$..[cases][:]'
        ts-colab get result_details test_data -f json -j '$..[suites][:]'


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

    if json_path:
        try:
            response = [
                match.value for match in jsonpath_ng.parse(json_path).find(response)
            ]
        except Exception as exception:
            raise click.ClickException(
                f"Failed to parse {json_path} expression {exception}"
            )

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


@main.command()
@click.option(
    "-o",
    "--output-dir",
    default=None,
    type=click.Path(writable=True, dir_okay=True, resolve_path=True),
    help="output directory",
)
@click.option("-p", "--project", required=False, help="Project to scan (name or ID)")
@click.option("-s", "--space", required=False, help="Space to scan (name or ID)")
@click.option("-r", "--result", required=False, help="result name or ID")
def crawl(project, space, output_dir, result):
    """Crawls an organization for specific project and spaces.

    If an output-dir is specified, dumps results into files (with result id)
    using a directory structure composed of <netloc>/<project>/<space>/...

    Example:

    \b
        /home/laurent/testspace-colab
        └── lbrack.testspace.com
            ├── lbrack:testspace-colab
            │   ├── elk
            │   │   ├── build.10@PR-3.json
            │   │   ├── build.11@PR-3.json
            │   │   └── build.12@PR-3.json
            │   ├── json-data-access
            │   │   ├── build.7@PR-2.json
            │   └── main
            │       ├── build.13.json
            │       └── build.9.json
            ├── lbrack:testspace.getting-started
            │   └── main
            │       ├── Sequence_4.json
            │       ├── Sequence_5.json
            └── samples
                └── main
                    └── test_data.json

    """
    parse_error_spec = []
    parse_ok_count = 0

    client = lib_module.API()

    if output_dir:
        output_dir = pathlib.Path(output_dir)
        if not output_dir.is_dir():
            output_dir.mkdir(exist_ok=True)
        org_dir = output_dir / urllib.parse.urlparse(client.url).netloc

        if not org_dir.is_dir():
            click.secho(f"creating org dir {org_dir}", fg="blue")
            org_dir.mkdir()

    projects = [project] if project else [s["name"] for s in client.get_projects()]

    for current_project in projects:
        if output_dir:
            project_dir = org_dir / current_project
            if not project_dir.is_dir():
                click.secho(f"creating project dir {project_dir}", fg="blue")
                project_dir.mkdir()
        spaces = (
            [space]
            if space
            else [s["name"] for s in client.get_spaces(project=current_project)]
        )
        for current_space in spaces:
            if output_dir:
                space_dir = project_dir / current_space
                if not space_dir.is_dir():
                    click.secho(f"creating space dir {space_dir}", fg="blue")
                    space_dir.mkdir(parents=True)

            results = (
                [result]
                if result
                else [
                    s["name"]
                    for s in client.get_results(
                        project=current_project, space=current_space
                    )
                ]
            )

            for current_result in results:
                result_file = None
                if output_dir:
                    result_file = space_dir / f"{current_result}.json"  # By result ID
                    if result_file.is_file():
                        click.secho(
                            f"result file {result_file} already exists - skipping",
                            fg="yellow",
                            bold=True,
                        )
                        continue
                load_spec = (
                    f"crawl=>org={client.url}, project={current_project}, space={current_space}, "
                    f"result={current_result}"
                )
                click.secho(load_spec, fg="blue")
                logger.debug(load_spec)
                try:
                    response = client.get_result_details(
                        current_result, project=current_project, space=current_space
                    )
                    parse_ok_count += 1
                except Exception:
                    parse_error_spec.append(load_spec)
                    logger.exception(f"failed to parse {load_spec}")
                else:
                    if result_file:
                        click.secho(
                            f"saving response as json to {result_file}",
                            fg="blue",
                            nl=False,
                        )
                        try:
                            with open(result_file, "w") as file_handle:
                                json.dump(response, file_handle, indent=4)
                        except Exception as write_exception:
                            logger.exception(write_exception)
                            raise click.ClickException(f"failed {write_exception}")
                        click.secho(" Done!", fg="green")

    num_failures = len(parse_error_spec)

    click.secho(f"Parsed {parse_ok_count} resuls with {num_failures} errors")
    if num_failures:
        raise click.ClickException(
            f"Failed to parse {num_failures} results - see log for details"
        )


@main.command()
@click.option("--no-elk", is_flag=True, help="Do not start the ELK stack")
def jupyter(no_elk):
    """Starts the Jupyter lab

    When running in CodeSpaces, the browser is not automatically
    started.



    """
    notebook_dir = utils_module.get_notebook_dir()
    no_browser = "--no-browser" if "CODESPACES" in os.environ else ""

    elk = elk_module.ELK() if not no_elk else None
    if elk:
        click.secho("starting ELK", fg="green")
        elk.start()

    exit_code = os.system(f"jupyter lab --notebook-dir={notebook_dir} {no_browser}")

    if elk:
        elk.stop()

    if exit_code and exit_code != 2:
        raise click.ClickException(f"Jupyter lab existed with an error {exit_code}")


@main.group()
def elk():
    """Command group to control the Elastic Stack docker image"""


@elk.command()
def start():
    """Starts the EKL docker image"""
    elk_client = elk_module.ELK()
    click.secho("starting ... be patient", fg="blue")
    try:
        elk_client.start()
    except IOError as error:
        raise click.ClickException(f"Failed to start ELK {error}")
    click.secho(f"ELK Container started ID={elk_client.container.id}", fg="green")


@elk.command()
def stop():
    """Stops the EKL docker image"""
    elk_client = elk_module.ELK()
    click.secho("stopping ... be patient", fg="blue")
    try:
        elk_client.stop()
    except IOError as error:
        raise click.ClickException(f"Failed to stop ELK {error}")
    click.secho("ELK stopped", fg="green")


@elk.command()
def health():
    """show cluster health status"""
    elk_client = elk_module.ELK()
    if elk_client.available:
        click.secho("getting cluster health", fg="blue")
        health = elk_client.get_health()
        print(yaml.dump(health))
        click.secho("Done", fg="green")
    else:
        click.secho("ELK not available", fg="yellow")


@elk.command()
def info():
    """Shows elastic search info"""
    elk_client = elk_module.ELK()
    if elk_client.available:
        click.secho("elastic search info", fg="blue")
        print(yaml.dump(elk_client.elastic_search.info()))
        click.secho("Done", fg="green")
    else:
        click.secho("ELK not available", fg="yellow")


@elk.command()
def kibana():
    """ starts a browser and connects to Kibana in the docker instance."""
    elk_client = elk_module.ELK()
    if elk_client.available:
        url = "http://localhost:5601"
        click.secho(f"connecting to {url}", fg="blue")
        webbrowser.open("http://localhost:5601")
        click.secho("Done", fg="green")
    else:
        click.secho("kibana not available", fg="yellow")


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
