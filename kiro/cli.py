#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kiro Proxy - CLI tool for Kiro Gateway

Usage:
    kiro-proxy install <credentials.json>  - Configure with Kiro credentials
    kiro-proxy start [--port PORT]         - Start the proxy server
    kiro-proxy status                      - Show current configuration
"""

import json
import secrets
import sys
from pathlib import Path
from typing import Optional

import click

# Config directory and file
CONFIG_DIR = Path.home() / ".kiro-proxy"
CONFIG_FILE = CONFIG_DIR / "config.json"


def find_kiro_ide_credentials() -> Optional[Path]:
    """自动查找 Kiro IDE 凭证文件"""
    home = Path.home()
    
    # 可能的凭证文件位置
    possible_paths = [
        # Kiro IDE 标准路径
        home / ".aws" / "sso" / "cache" / "kiro-auth-token.json",
    ]
    
    # 首先检查标准路径
    for path in possible_paths:
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'accessToken' in content or 'refreshToken' in content:
                        return path
            except Exception:
                continue
    
    # 如果没找到，搜索 .aws/sso/cache 目录下的所有 JSON 文件
    cache_dir = home / ".aws" / "sso" / "cache"
    if cache_dir.exists():
        json_files = list(cache_dir.glob("*.json"))
        if json_files:
            # 按修改时间排序，使用最新的
            json_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'accessToken' in content or 'refreshToken' in content:
                            return json_file
                except Exception:
                    continue
    
    return None


def get_config() -> dict:
    """Load configuration from file."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_config(config: dict) -> None:
    """Save configuration to file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def print_banner():
    """Print startup banner."""
    click.echo()
    click.secho("  👻 Kiro Proxy", fg="white", bold=True)
    click.echo()


def print_connection_info(port: int, api_key: str):
    """Print connection information."""
    click.echo()
    click.secho("  ✅ Kiro Proxy is running!", fg="green", bold=True)
    click.echo()
    click.echo("  " + "─" * 45)
    click.echo()
    click.secho("  Connection Info:", fg="white", bold=True)
    click.echo()
    click.echo(f"    Base URL:  ", nl=False)
    click.secho(f"http://localhost:{port}/v1", fg="cyan", bold=True)
    click.echo()
    click.echo(f"    API Key:   ", nl=False)
    click.secho(api_key, fg="yellow")
    click.echo()
    click.echo(f"    Models:    ", nl=False)
    click.secho("claude-sonnet-4.5, claude-sonnet-4, claude-haiku-4.5", fg="white")
    click.echo()
    click.echo("  " + "─" * 45)
    click.echo()
    click.secho("  Example (Python):", fg="white", bold=True)
    click.echo()
    click.echo("    from openai import OpenAI")
    click.echo(f'    client = OpenAI(base_url="http://localhost:{port}/v1", api_key="{api_key}")')
    click.echo('    response = client.chat.completions.create(model="claude-sonnet-4.5", ...)')
    click.echo()
    click.echo("  " + "─" * 45)
    click.echo()
    click.secho("  Press Ctrl+C to stop", fg="white", dim=True)
    click.echo()


@click.group()
@click.version_option(version="1.0.0", prog_name="kiro-proxy")
def main():
    """Kiro Proxy - Use Claude models with OpenAI-compatible API."""
    pass


@main.command()
@click.argument('credentials_file', type=click.Path(exists=True), required=False, default=None)
@click.option('--ide', is_flag=True, help='Auto-detect Kiro IDE credentials')
@click.option('--api-key', '-k', default=None, help='Custom API key (auto-generated if not provided)')
def install(credentials_file: Optional[str], ide: bool, api_key: Optional[str]):
    """Configure Kiro Proxy with credentials file.
    
    CREDENTIALS_FILE: Path to Kiro credentials JSON file (optional with --ide)
    
    Example:
        kiro-proxy install --ide
        kiro-proxy install ~/.aws/sso/cache/kiro-auth-token.json
    """
    print_banner()
    
    # IDE 模式：自动查找凭证文件
    if ide:
        click.echo("  🔍 Searching for Kiro IDE credentials...")
        found_path = find_kiro_ide_credentials()
        if found_path:
            click.secho(f"  ✅ Found: {found_path}", fg="green")
            creds_path = found_path
        else:
            click.secho("  ❌ Kiro IDE credentials not found!", fg="red")
            click.echo()
            click.echo("  Please ensure:")
            click.echo("    1. Kiro IDE is installed: https://kiro.dev/")
            click.echo("    2. You are logged in to Kiro IDE")
            click.echo()
            click.echo("  Or specify the credentials file manually:")
            click.secho("    kiro-proxy install <credentials.json>", fg="cyan")
            click.echo()
            sys.exit(1)
    elif credentials_file:
        creds_path = Path(credentials_file).resolve()
    else:
        click.secho("  ❌ Please provide a credentials file or use --ide mode", fg="red")
        click.echo()
        click.echo("  Usage:")
        click.secho("    kiro-proxy install --ide", fg="cyan")
        click.secho("    kiro-proxy install <credentials.json>", fg="cyan")
        click.echo()
        sys.exit(1)
    
    # Validate credentials file
    click.echo(f"  📄 Checking credentials file...")
    try:
        with open(creds_path, 'r', encoding='utf-8') as f:
            creds = json.load(f)
        
        if 'accessToken' not in creds and 'refreshToken' not in creds:
            click.secho("  ❌ Invalid credentials file: missing accessToken or refreshToken", fg="red")
            sys.exit(1)
        
        click.secho(f"  ✅ Valid credentials file: {creds_path}", fg="green")
    except json.JSONDecodeError:
        click.secho(f"  ❌ Invalid JSON file: {creds_path}", fg="red")
        sys.exit(1)
    except Exception as e:
        click.secho(f"  ❌ Error reading file: {e}", fg="red")
        sys.exit(1)
    
    # Generate API key if not provided
    if not api_key:
        api_key = secrets.token_urlsafe(16)
        click.echo(f"  🔑 Generated API Key: ", nl=False)
        click.secho(api_key, fg="yellow", bold=True)
    
    # Save configuration
    config = {
        "credentials_file": str(creds_path),
        "api_key": api_key,
        "port": 8000
    }
    save_config(config)
    
    click.echo()
    click.secho(f"  ✅ Configuration saved to: {CONFIG_FILE}", fg="green")
    click.echo()
    click.echo("  Now run:")
    click.secho("    kiro-proxy start", fg="cyan", bold=True)
    click.echo()


@main.command()
@click.option('--port', '-p', default=None, type=int, help='Server port (default: 8000)')
def start(port: Optional[int]):
    """Start the Kiro Proxy server.
    
    Example:
        kiro-proxy start
        kiro-proxy start --port 9000
    """
    config = get_config()
    
    if not config.get('credentials_file'):
        click.secho("  ❌ Not configured! Run 'kiro-proxy install <credentials.json>' first.", fg="red")
        sys.exit(1)
    
    # Check credentials file still exists
    creds_path = Path(config['credentials_file'])
    if not creds_path.exists():
        click.secho(f"  ❌ Credentials file not found: {creds_path}", fg="red")
        click.echo("  Run 'kiro-proxy install <credentials.json>' to reconfigure.")
        sys.exit(1)
    
    # Use provided port or config port or default
    server_port = port or config.get('port', 8000)
    api_key = config.get('api_key', '')
    
    # Set environment variables for the app
    import os
    os.environ['KIRO_CREDS_FILE'] = str(creds_path)
    os.environ['PROXY_API_KEY'] = api_key
    
    print_banner()
    print_connection_info(server_port, api_key)
    
    # Start uvicorn server
    try:
        import uvicorn
        
        # Add package directory to path so main.py can be found
        package_dir = Path(__file__).parent.parent
        if str(package_dir) not in sys.path:
            sys.path.insert(0, str(package_dir))
        os.chdir(package_dir)
        
        uvicorn.run("main:app", host="0.0.0.0", port=server_port, log_level="warning")
    except KeyboardInterrupt:
        click.echo()
        click.secho("  👋 Kiro Proxy stopped.", fg="yellow")
    except Exception as e:
        click.secho(f"  ❌ Failed to start server: {e}", fg="red")
        sys.exit(1)


@main.command()
def init():
    """Interactive setup wizard for Kiro Proxy."""
    click.echo()
    click.secho("  👻 Kiro Proxy Setup", fg="white", bold=True)
    click.echo()
    click.secho("  ? Select credentials source:", fg="white", bold=True)
    click.echo()
    click.echo("    ❯ ", nl=False)
    click.secho("1. Kiro IDE ", fg="cyan", bold=True, nl=False)
    click.secho("(auto-detect)", fg="white")
    click.echo("      ", nl=False)
    click.secho("2. kiro-cli ", fg="white", dim=True, nl=False)
    click.secho("(not available)", fg="red")
    click.echo("      ", nl=False)
    click.secho("3. Manual file path ", fg="cyan", bold=True, nl=False)
    click.secho("(e.g. ~/.aws/sso/cache/kiro-auth-token.json)", fg="white", dim=True)
    click.echo()
    
    # Get user choice
    while True:
        choice = click.prompt("  Enter choice", type=str, default="1")
        if choice in ["1", "2", "3"]:
            break
        click.secho("  Please enter 1, 2, or 3", fg="red")
    
    click.echo()
    creds_path = None
    
    if choice == "1":
        # Kiro IDE auto-detect
        click.echo("  🔍 Searching for Kiro IDE credentials...")
        found_path = find_kiro_ide_credentials()
        if found_path:
            click.secho(f"  ✅ Found: {found_path}", fg="green")
            creds_path = found_path
        else:
            click.secho("  ❌ Kiro IDE credentials not found!", fg="red")
            click.echo()
            click.echo("  Please ensure:")
            click.echo("    1. Kiro IDE is installed: https://kiro.dev/")
            click.echo("    2. You are logged in to Kiro IDE")
            click.echo()
            sys.exit(1)
    
    elif choice == "2":
        # kiro-cli not available
        click.secho("  ❌ kiro-cli support is not available yet.", fg="red")
        click.echo()
        click.echo("  Please use Kiro IDE or manual file path instead.")
        click.echo()
        sys.exit(1)
    
    elif choice == "3":
        # Manual file path
        click.echo("  📄 Example paths:")
        click.secho("     ~/.aws/sso/cache/kiro-auth-token.json", fg="white", dim=True)
        click.secho("     C:\\Users\\xxx\\.aws\\sso\\cache\\kiro-auth-token.json", fg="white", dim=True)
        click.echo()
        file_path = click.prompt("  Enter credentials file path", type=str)
        file_path = Path(file_path).expanduser().resolve()
        
        if not file_path.exists():
            click.secho(f"  ❌ File not found: {file_path}", fg="red")
            sys.exit(1)
        
        # Validate JSON
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                creds = json.load(f)
            if 'accessToken' not in creds and 'refreshToken' not in creds:
                click.secho("  ❌ Invalid credentials file: missing accessToken or refreshToken", fg="red")
                sys.exit(1)
            click.secho(f"  ✅ Valid credentials file", fg="green")
            creds_path = file_path
        except json.JSONDecodeError:
            click.secho(f"  ❌ Invalid JSON file", fg="red")
            sys.exit(1)
    
    click.echo()
    
    # Port configuration
    port_input = click.prompt("  ? Server port", default="8000")
    try:
        port = int(port_input)
    except ValueError:
        port = 8000
    
    click.echo()
    
    # Generate API key
    api_key = secrets.token_urlsafe(16)
    click.echo("  🔑 Generated API Key: ", nl=False)
    click.secho(api_key, fg="yellow", bold=True)
    
    # Save configuration
    config = {
        "credentials_file": str(creds_path),
        "api_key": api_key,
        "port": port
    }
    save_config(config)
    
    click.echo()
    click.secho(f"  ✅ Configuration saved!", fg="green")
    click.echo()
    click.echo("  " + "─" * 45)
    click.echo()
    click.secho("  📁 Config saved to:", fg="white", bold=True)
    click.secho(f"     {CONFIG_FILE}", fg="white", dim=True)
    click.echo()
    click.secho("  💡 Forgot your API Key? Run:", fg="white")
    click.secho("     kiro-gateway-cli status", fg="cyan")
    click.echo()
    click.echo("  " + "─" * 45)
    click.echo()
    click.secho("  Quick Start:", fg="white", bold=True)
    click.echo()
    click.secho("    kiro-gateway-cli start", fg="cyan", bold=True)
    click.echo()
    
    # Ask if user wants to start now
    start_now = click.confirm("  ? Start server now", default=True)
    if start_now:
        click.echo()
        ctx = click.get_current_context()
        ctx.invoke(start, port=port)


@main.command()
def status():
    """Show current configuration status."""
    print_banner()
    
    config = get_config()
    
    if not config:
        click.secho("  ❌ Not configured", fg="red")
        click.echo()
        click.echo("  Run:")
        click.secho("    kiro-proxy install <credentials.json>", fg="cyan")
        click.echo()
        return
    
    click.secho("  📋 Current Configuration:", fg="white", bold=True)
    click.echo()
    
    creds_file = config.get('credentials_file', 'Not set')
    creds_exists = Path(creds_file).exists() if creds_file != 'Not set' else False
    
    click.echo(f"    Credentials: ", nl=False)
    if creds_exists:
        click.secho(creds_file, fg="green")
    else:
        click.secho(f"{creds_file} (NOT FOUND)", fg="red")
    
    click.echo(f"    API Key:     ", nl=False)
    click.secho(config.get('api_key', 'Not set'), fg="yellow")
    
    click.echo(f"    Port:        ", nl=False)
    click.secho(str(config.get('port', 8000)), fg="cyan")
    
    click.echo(f"    Config File: ", nl=False)
    click.secho(str(CONFIG_FILE), fg="white", dim=True)
    
    click.echo()


if __name__ == "__main__":
    main()
