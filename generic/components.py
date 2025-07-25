"""
Reusable UI Components and Core Functions for Bfabric App
=========================================================

IMPORTANT: DO NOT MODIFY THIS FILE
----------------------------------
This module contains essential components and core functionalities for the Bfabric web app.
It is a foundational part of the system, and any changes to this file may disrupt functionality
or compatibility with other modules.

This module includes:
  - Initialization of the Dash app instance.
  - Callbacks for authentication and URL parameter processing.
  - Callback for bug report handling.
  - Content to display for authenticated and unauthenticated users.
"""

from dash import html
import dash_bootstrap_components as dbc

# UI Components
# --------------

## Unauthenticated User Content
# ------------------------------
# Message displayed to users who are not authenticated.
no_auth = [
    html.P("You are not currently logged into an active session. Please log into bfabric to continue:"),
    html.A('Login to Bfabric', href='https://fgcz-bfabric.uzh.ch/bfabric/')  # Link to the Bfabric login page.
]

def lane_card(lane_position, container_ids):

    card_content = [
        dbc.CardHeader(f"Lane {lane_position}"),
        dbc.CardBody(
            [
                html.P(f"Container IDs:"),
            ] + [
                html.H5(name) for name in container_ids
            ]
        ),
    ]
    return dbc.Card(card_content, style={"max-width": "25vw", "margin": "10px"})


## Placeholder for Authenticated User Content
# --------------------------------------------
# Dynamic content displayed to authenticated users.
auth = [html.Div(id="auth-div")]
