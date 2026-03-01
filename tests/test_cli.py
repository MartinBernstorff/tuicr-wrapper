from typer.testing import CliRunner

from incremental_review.cli import app

runner = CliRunner()


def test_cli_launches_with_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
