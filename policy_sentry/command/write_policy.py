"""
Given a Policy Sentry YML template, write a least-privilege IAM Policy in CRUD mode or Actions mode.
"""
import sys
import json
import logging
import click
import click_log
import yaml
from policy_sentry.util.file import read_yaml_file
from policy_sentry.writing.sid_group import SidGroup

logger = logging.getLogger(__name__)
click_log.basic_config(logger)


@click.command(
    short_help="Write least-privilege IAM policies, restricting all actions to resource ARNs."
)
# pylint: disable=duplicate-code
@click.option(
    "--input-file",
    type=str,
    help="Path of the YAML File used for generating policies",
)
@click.option(
    "--minimize",
    required=False,
    type=int,
    help="Minimize the resulting statement with *safe* usage of wildcards to reduce policy length. "
    "Set this to the character length you want - for example, 4",
)
@click.option(
    "--fmt",
    type=click.Choice(["yaml", "json"]),
    default="json",
    required=False,
    help='Format output as YAML or JSON. Defaults to "json"',
)
@click_log.simple_verbosity_option(logger)
def write_policy(input_file, minimize, fmt):
    """
    Write least-privilege IAM policies, restricting all actions to resource ARNs.
    """

    if input_file:
        cfg = read_yaml_file(input_file)
    else:
        try:
            cfg = yaml.safe_load(sys.stdin)
        except yaml.YAMLError as exc:
            logger.critical(exc)
            sys.exit()
    policy = write_policy_with_template(cfg, minimize)
    if fmt == "yaml":
        print(yaml.dump(policy, sort_keys=False))
    else:
        print(json.dumps(policy, indent=4))


def write_policy_with_template(cfg, minimize=None):
    """
    This function is called by write-policy so the config can be passed in as a dict without running into a Click-related error. Use this function, rather than the write-policy function, if you are using Policy Sentry as a python library.

    Arguments:
        cfg: The loaded YAML as a dict. Must follow Policy Sentry dictated format.
        minimize: Minimize the resulting statement with *safe* usage of wildcards to reduce policy length. Set this to the character length you want - for example, 0, or 4. Defaults to none.
    Returns:
        Dictionary: The JSON policy
    """
    sid_group = SidGroup()
    policy = sid_group.process_template(cfg, minimize)
    return policy
