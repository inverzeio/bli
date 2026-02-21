#!/usr/bin/env python3
"""bli — Browserling Integration CLI for security URL detonation."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich import box

from bli.client import BrowserlingAuthError, BrowserlingClient, BrowserlingClientError
from bli.session import SUPPORTED_BROWSERS, SUPPORTED_OSES, DetonationSession

load_dotenv()

console = Console()
err_console = Console(stderr=True)

BROWSER_CHOICES = click.Choice(SUPPORTED_BROWSERS)
OS_CHOICES = click.Choice(SUPPORTED_OSES)


def _make_session() -> DetonationSession:
    try:
        client = BrowserlingClient()
    except BrowserlingAuthError as exc:
        err_console.print(f"[bold red]Auth error:[/] {exc}")
        sys.exit(1)
    return DetonationSession(client)


@click.group()
@click.version_option("0.1.0", prog_name="bli")
def cli() -> None:
    """bli — Browserling Integration for security URL detonation.

    Opens suspicious URLs inside isolated, sandboxed Browserling browser
    sessions so analysts can observe behaviour safely.
    """


@cli.command()
@click.argument("url")
@click.option("--browser", "-b", default="chrome", type=BROWSER_CHOICES, show_default=True, help="Browser to use.")
@click.option("--browser-version", "-V", default="latest", show_default=True, help="Browser version.")
@click.option("--os", "os_name", default="windows", type=OS_CHOICES, show_default=True, help="Operating system.")
@click.option("--os-version", default="10", show_default=True, help="OS version.")
@click.option("--no-open", is_flag=True, default=False, help="Print session URL without opening it locally.")
def detonate(
    url: str,
    browser: str,
    browser_version: str,
    os_name: str,
    os_version: str,
    no_open: bool,
) -> None:
    """Detonate a single URL in a sandboxed Browserling session.

    \b
    Example:
        bli detonate https://suspicious.example.com
        bli detonate https://example.com --browser firefox --os macos
    """
    session = _make_session()
    open_locally = not no_open

    with console.status(f"[cyan]Requesting Browserling session for [bold]{url}[/bold]...[/]"):
        result = session.detonate(
            url,
            browser=browser,
            browser_version=browser_version,
            os_name=os_name,
            os_version=os_version,
            open_locally=open_locally,
        )

    if not result.success:
        err_console.print(f"[bold red]Detonation failed:[/] {result.error}")
        sys.exit(1)

    _print_result_table([result], opened=open_locally)


@cli.command("detonate-batch")
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--browser", "-b", default="chrome", type=BROWSER_CHOICES, show_default=True, help="Browser to use.")
@click.option("--browser-version", "-V", default="latest", show_default=True, help="Browser version.")
@click.option("--os", "os_name", default="windows", type=OS_CHOICES, show_default=True, help="Operating system.")
@click.option("--os-version", default="10", show_default=True, help="OS version.")
@click.option("--no-open", is_flag=True, default=False, help="Print session URLs without opening them locally.")
def detonate_batch(
    file: Path,
    browser: str,
    browser_version: str,
    os_name: str,
    os_version: str,
    no_open: bool,
) -> None:
    """Detonate all URLs in FILE (one URL per line) sequentially.

    \b
    Example:
        bli detonate-batch urls.txt
        bli detonate-batch iocs.txt --no-open
    """
    urls = [line.strip() for line in file.read_text().splitlines() if line.strip() and not line.startswith("#")]

    if not urls:
        err_console.print("[yellow]No URLs found in file.[/]")
        sys.exit(0)

    console.print(f"[cyan]Detonating [bold]{len(urls)}[/bold] URL(s)...[/]")

    session = _make_session()
    open_locally = not no_open
    results = []

    for i, url in enumerate(urls, 1):
        with console.status(f"[cyan]({i}/{len(urls)}) Requesting session for [bold]{url}[/bold]...[/]"):
            result = session.detonate(
                url,
                browser=browser,
                browser_version=browser_version,
                os_name=os_name,
                os_version=os_version,
                open_locally=open_locally,
            )
        results.append(result)

    _print_result_table(results, opened=open_locally)

    failures = [r for r in results if not r.success]
    if failures:
        err_console.print(f"\n[bold red]{len(failures)} detonation(s) failed.[/]")
        sys.exit(1)


def _print_result_table(results: list, *, opened: bool) -> None:
    table = Table(box=box.ROUNDED, show_lines=True)
    table.add_column("URL", style="cyan", no_wrap=False)
    table.add_column("Browser", style="magenta")
    table.add_column("OS", style="blue")
    table.add_column("Status", justify="center")
    table.add_column("Session URL", style="green", no_wrap=False)

    for r in results:
        if r.success:
            status = "[green]OK[/green]"
            session_url = r.session_url
        else:
            status = "[red]FAIL[/red]"
            session_url = f"[red]{r.error}[/red]"

        table.add_row(
            r.url,
            f"{r.browser} {r.browser_version}",
            f"{r.os_name} {r.os_version}",
            status,
            session_url,
        )

    console.print(table)

    if opened:
        console.print("[dim]Session(s) opened in your local browser.[/]")
    else:
        console.print("[dim]Use the session URL above to observe the detonation.[/]")


if __name__ == "__main__":
    cli()
