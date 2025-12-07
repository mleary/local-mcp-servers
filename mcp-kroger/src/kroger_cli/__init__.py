from __future__ import annotations

import json
from typing import Optional

import typer

from kroger_core.client import KrogerService
from kroger_core.config import resolve_location_id
from kroger_core.products import summarize_products

app = typer.Typer(help="Dual-mode Kroger tools usable via CLI or MCP server.")
cart_app = typer.Typer(help="Cart operations (requires user auth)")
app.add_typer(cart_app, name="cart")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search term, e.g. 'milk'"),
    limit: int = typer.Option(5, help="Maximum number of items to return"),
    location_id: Optional[str] = typer.Option(None, help="Kroger location ID; defaults to KROGER_STORE_ID env"),
    json_output: bool = typer.Option(True, "--json/--no-json", help="Emit machine-readable JSON"),
):
    """Search Kroger products and optionally emit summarized JSON."""
    service = KrogerService()
    raw = service.search_products(term=query, limit=limit, location_id=location_id)
    summary = summarize_products(raw)
    if json_output:
        typer.echo(json.dumps(summary))
    else:
        for item in summary["items"]:
            typer.echo(f"{item.get('description')} (UPC {item.get('upc')}) - {item.get('brand')}")


@cart_app.command("add")
def add_to_cart(
    upc: str = typer.Argument(..., help="UPC of the item to add"),
    quantity: int = typer.Option(1, min=1, help="Quantity to add"),
    modality: str = typer.Option("PICKUP", help="PICKUP or DELIVERY"),
    location_id: Optional[str] = typer.Option(None, help="Kroger location ID; defaults to KROGER_STORE_ID env"),
):
    """Add a product to the authenticated user's cart."""
    service = KrogerService()
    resolved_location = resolve_location_id(location_id)
    try:
        service.add_to_cart(upc=upc, quantity=quantity, modality=modality.upper(), location_id=resolved_location)
        typer.echo(json.dumps({
            "status": "success",
            "upc": upc,
            "quantity": quantity,
            "modality": modality.upper(),
            "location_id": resolved_location,
        }))
    except Exception as exc:  # noqa: BLE001
        typer.echo(json.dumps({"error": str(exc)}))
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
