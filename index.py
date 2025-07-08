# Ensure version compatibility between bfabric_web_apps and bfabric_web_app_template.
# Both must be the same version to avoid compatibility issues.
# Example: If bfabric_web_apps is version 0.1.3, bfabric_web_app_template must also be 0.1.3.
# Verify and update versions accordingly before running the application.

from dash import Input, Output, State, html, dcc
import dash_bootstrap_components as dbc
import bfabric_web_apps
from generic.callbacks import app
from generic.components import no_auth
from pathlib import Path
import dash_daq as daq
from generic.components import lane_card
from utils.entity_utils import extended_entity_data as eed
import json
from utils.draugr_utils import generate_draugr_command

# Here we define the sidebar of the UI, including the clickable components like dropdown and slider. 
sidebar = [
    html.P(id="sidebar_text", children="Select Orders to DMX"),
    dcc.Dropdown([], id='draugr-dropdown', multi=True),
    html.Br(),
    html.P(id="sidebar_text_2", children="Select Draugr Advanced Options"),
    dcc.Dropdown(
        [
            "--demux-only-mode",
            "--skip-ss-generation",
            "--skip-demux",
            "--skip-post-demux",
            "--skip-gstore-copy"
        ], 
        id='draugr-flags', 
        multi=True
    ),
    html.Br(),
    html.P(id="draugr-text-2", children="Disable Wizard"),
    daq.BooleanSwitch(id='wizard', on=False),
    html.P(id="draugr-text-4", children="Is Multiome"),
    daq.BooleanSwitch(id='multiome', on=False),
    html.Br(),
    dbc.Input(value="", placeholder='Custom Bcl2fastq flags', id='bcl-input'),
    html.Br(),
    dbc.Input(value="", placeholder='Custom Cellranger flags', id='cellranger-input'),
    html.Br(),
    dbc.Input(value="", placeholder='Custom Bases2fastq flags', id='bases2fastq-input'),
    html.Br(),
    dbc.Button('Submit', id='draugr-button'),
]
# here we define the modal that will pop up when the user clicks the submit button.
modal = html.Div([
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Ready to Run Draugr?")),
        dbc.ModalBody("Are you sure you're ready to trigger demultiplexing?"),
        dbc.ModalFooter(dbc.Button("Yes!", id="Submit", className="ms-auto", n_clicks=0)),],
    id="modal-confirmation",
    is_open=False,),
])

# Here are the alerts which will pop up when the user creates workunits 
alerts = html.Div(
    [
        dbc.Alert("Success: Draugr Initiated!", color="success", id="alert-fade-success", dismissable=True, is_open=False),
        dbc.Alert("Error: Draugr Initiation Failed!", color="danger", id="alert-fade-fail", dismissable=True, is_open=False),
        dbc.Alert("Warning: Please select Order to DMX!", color="warning", id="alert-fade-warning", dismissable=True, is_open=False),
        dbc.Alert("Warning: Missing 'server' in entity!", color="warning",  id="alert-warning-no-system", dismissable=False, is_open=False),
        dbc.Alert("Warning: Missing 'datafolder' in entity!", color="warning",  id="alert-warning-no-data-folder", dismissable=False, is_open=False),
    ], style={"margin": "20px"}
)

# Here we define a Dash layout, which includes the sidebar, and the main content of the app. 
app_specific_layout = dbc.Row(
        id="page-content-main",
        children=[
            dcc.Loading(dcc.Store(id="extended-entity-data", storage_type="session")),
            dcc.Loading(alerts), 
            modal,  # Modal defined earlier.
            dbc.Col(
                html.Div(
                    id="sidebar",
                    children=sidebar,  # Sidebar content defined earlier.
                    style={
                        "border-right": "2px solid #d4d7d9",
                        "height": "100%",
                        "padding": "20px",
                        "font-size": "20px",
                        "overflow-y":"scroll",
                        "overflow-x":"hidden",
                        "max-height":"65vh"
                    }
                ),
                width=3,  # Width of the sidebar column.
            ),
            dbc.Col(
                dcc.Loading(
                    html.Div(
                        id="page-content",
                        children=[
                            html.Div(id="auth-div")  # Placeholder for `auth-div` to be updated dynamically.
                        ],
                        style={
                            "margin-top": "2vh",
                            "margin-left": "2vw",
                            "font-size": "20px",
                            "overflow-y":"scroll",
                            "overflow-x":"hidden",
                            "max-height":"65vh"
                        }
                    ),
                ),
                width=9,  # Width of the main content column.
            ),
        ],
        style={"margin-top": "0px", "min-height": "40vh"}  # Overall styling for the row layout.
    )

# Here we define the documentation content for the app.
documentation_content = [
    html.H2("Welcome to Draugr UI"),
    html.P([
        "This app serves as the user-interface for ",
        html.A("Draugr,", href="https://gitlab.bfabric.org/Genomics/draugr", target="_blank"),
        " or Demultiplexing wRapper And Updated GRiffin."
    ]),
    html.Br(),
    html.H4("Developer Info"),
    html.P([
        "This app was written by Griffin White, for the FGCZ. If you wish to report a bug, please use the \"bug reports\" tab. If you wish to contact the developer for other reasons, please use the email:",
        html.A(" griffin@gwcustom.com", href="mailto:griffin@gwcustom.com"),
    ]),
    html.Br(),
    html.H4("Draugr / DMX Tab"),
    html.P([
        html.B(
            "Select Orders to DMX --"
        ), " Select the order(s) for which you'd like to re-trigger demultiplexing.",
        html.Br(),html.Br(),
        html.B(
            "Skip Gstore Copy --"
        ), " Select this option if you don't want to copy to gstore. Mostly useful if you're not sure yet if the current settings will work.",
        html.Br(),html.Br(),
        html.B(
            "Disable Wizard --"
        ), " The wizard is Draugr's internal automatic-barcode detection and correction engine. If you're confident that the correct barcodes are assigned, or the wizard is creating barcode conflicts while checking new settings, you should turn the wizard off.",
        html.Br(),html.Br(),
        html.B(
            "Is Multiome --"
        ), " If you're processing a multiome run, select this option.",
        html.Br(),html.Br(),
        html.B(
            "Custom Bcl2fastq flags --"
        ), """Custom bcl2fastq flags to use for the standard samples wrapped in a
        string, with arguments separated by '|' characters, E.g. "--barcode-
        mismatches 2|--minimum-trimmed-read-length ". For a full list of possible flags, see the """,
        html.A(" bcl2fastq documentation.", href="https://support.illumina.com/content/dam/illumina-support/documents/documentation/software_documentation/bcl2fastq/bcl2fastq_letterbooklet_15038058brpmi.pdf", target="_blank"),
        html.Br(),html.Br(),
        html.B(
            "Custom Cellranger flags --"
        ), """ Custom cellranger mkfastq flags to use for the 10x samples wrapped in a
        string, with arguments separated by '|' characters, E.g. "--barcode-
        mismatches 2|--delete-undetermined". For a full list of possible flags, see the 
        """,
        html.A("cellranger documentation", href="https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/mkfastq", target="_blank"),
        html.Br(),html.Br(),
        html.B(
            "Custom Bases2fastq flags --"
        ), """ Custom bases2fastq flags to use wrapped in a string, with arguments
        separated by ';' characters, E.g. "--i1-cycles 8;--r2-cycles 40 ". For a full list of possible flags, see the 
        """,
        html.A("bases2fastq documentation", href="https://docs.elembio.io/docs/bases2fastq/", target="_blank"),
        html.Br(),
        html.Br(),
        
    ], style={"margin-left": "2vw"})
]

app_title = "Draugr UI"

# here we use the get_static_layout function from bfabric_web_apps to set up the app layout.
app.layout = bfabric_web_apps.get_static_layout(                    # The function from bfabric_web_apps that sets up the app layout.
    base_title=app_title,                                           # The app title we defined previously
    main_content=app_specific_layout,                               # The main content for the app defined in components.py
    documentation_content=documentation_content,                    # Documentation content for the app defined in components.py
    layout_config={
        "workunits": False, 
        "queue": True, 
        "bug": True
    }   # Configuration for the layout
)

# This callback is necessary for the modal to pop up when the user clicks the submit button.
@app.callback(
    Output("modal-confirmation", "is_open"),
    [Input("draugr-button", "n_clicks"), Input("Submit", "n_clicks")],
    [State("modal-confirmation", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output('draugr-dropdown', 'options'),
    [Input('extended-entity-data', 'data')]
)
def update_dropdown(entity):
    entity_data = json.loads(entity) if entity else None
    orders = entity_data.get('containers')
    options = [{"label": elt, "value": elt} for elt in orders]
    return options


@app.callback(
    Output("extended-entity-data", "data"),
    [Input("token_data", "data")]
)
def update_extended_entity_data(token_data):
    """
    This callback retrieves extended entity data based on the provided token data.
    It uses the `extended_entity_data` function to fetch and return the entity data.
    """
    if not token_data:
        return None
    return eed(token_data)


@app.callback(
    [
        Output("draugr-dropdown", "disabled"),
        Output("draugr-flags", "disabled"),
        Output("wizard", "disabled"),
        Output("multiome", "disabled"),
        Output("bcl-input", "disabled"),
        Output("cellranger-input", "disabled"),
        Output("bases2fastq-input", "disabled"),
        Output("draugr-button", "disabled"),
        Output("auth-div", "children"),
        Output("alert-warning-no-system", "is_open"),
        Output("alert-warning-no-data-folder", "is_open"),
    ],
    [
        Input("extended-entity-data", "data"),
    ],
    [
        State("token_data", "data")
    ]
)
def update_ui(entity_data, token):
    """
    This callback updates the UI based on the authentication token and entity data.
    If the user is authenticated, it enables the UI components for selecting orders and options.
    If the user is not authenticated, it disables the components and shows a no-auth message.
    """
    entity = json.loads(entity_data) if entity_data else None

    if not token or not entity:
        return (
            True, True, True, True, True, True, True, True, no_auth, False, False
        )

    elif not entity.get("server"):
        return (
            True, True, True, True, True, True, True, True,
            html.Div(),
            True,
            False
        )

    elif not entity.get("datafolder"):
        return (
            True, True, True, True, True, True, True, True,
            html.Div(),
            False,
            True
        )

    else: 
        # If the user is authenticated, enable all components and show the auth-div.     
        if len(list(entity['lanes'].values())) != 8:
            container = dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    lane_card(
                                        lane_position=lane_position,
                                        container_ids=container_ids
                                    ) for lane_position, container_ids in entity['lanes'].items()
                                ]
                            )
                        ]
                    )
                ]
            )
        else:
            container = dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    lane_card(
                                        lane_position=i,
                                        container_ids=entity['lanes'][str(i)]
                                    ) for i in range(1,5)
                                ]
                            ),
                            dbc.Col(
                                [
                                    lane_card(
                                        lane_position=i,
                                        container_ids=entity['lanes'][str(i)]
                                    ) for i in range(5,9)
                                ]
                            )
                        ]
                    )
                ]
            )
    
        return (
            False, False, False, False, False, False, False, False, container, False, False
        )
    
@app.callback(
    Output("alert-fade-success", "is_open"),   # Show success alert.
    Output("alert-fade-fail", "is_open"),      # Show failure alert.
    Output("alert-fade-warning", "is_open"),   # Show warning alert.
    [Input("Submit", "n_clicks")],             # Detect button clicks.
    [State("draugr-dropdown", "value"),        # Selected orders to DMX.
     State("draugr-flags", "value"),           # Selected Draugr flags.
     State("wizard", "on"),                    # Wizard toggle state.
     State("multiome", "on"),                  # Multiome toggle state.
     State("bcl-input", "value"),              # Custom Bcl2fastq flags.
     State("cellranger-input", "value"),       # Custom Cellranger flags.
     State("bases2fastq-input", "value"),
     State('url', 'search'),
     State("extended-entity-data", "data"),
     State("token_data", "data")],  # Authentication token and entity data.
    prevent_initial_call=True                  # Prevent callback on initial load.
)
def handle_draugr_submission(n_clicks, draugr_orders, draugr_flags, wizard, multiome, bcl_flags, cellranger_flags, bases2fastq_flags, token, entity_data, token_data):
    """
    Handles the submission of Draugr orders and options.
    It triggers the demultiplexing process and returns the success or failure alert states.
    
    Parameters:
        n_clicks (int): Number of times the submit button was clicked.
        draugr_orders (list): Selected orders to DMX.
        draugr_flags (list): Selected Draugr flags.
        wizard (bool): State of the wizard toggle.
        multiome (bool): State of the multiome toggle.
        bcl_flags (str): Custom Bcl2fastq flags.
        cellranger_flags (str): Custom Cellranger flags.
        bases2fastq_flags (str): Custom Bases2fastq flags.
        token_data (dict): Authentication token data.
        entity_data (dict): Metadata about the authenticated entity.
    Returns:
        tuple: Success and failure alert states.
    """

    env = token_data.get("environment")

    if not draugr_orders:
        return False, False, True  # success=False, fail=False, warning=True

    try:
        entity = json.loads(entity_data) if entity_data else None
        server = entity['server'],
        run_folder = entity['datafolder']

        command = generate_draugr_command(
            server=server,
            run_folder=run_folder,
            order_list=draugr_orders,
            disable_wizard=wizard,
            is_multiome=multiome,
            bcl_flags=bcl_flags,
            cellranger_flags=cellranger_flags,
            bases2fastq_flags=bases2fastq_flags,
            advanced_options=draugr_flags,
            env=env
        )

        arguments = {
            "files_as_byte_strings": {},
            "bash_commands": [command],
            "resource_paths": {}, 
            "attachment_paths": {},
            "token": token,
            "service_id":0,
            "charge": []
        }

        # Submit the job to a queue! 
        bfabric_web_apps.q(server[0]).enqueue(
            bfabric_web_apps.run_main_job,
            kwargs=arguments
        )
        # bfabric_web_apps.q("light").enqueue(
        #     bfabric_web_apps.run_main_job,
        #     kwargs=arguments
        # )

        print(f"Command submitted: {command}")

        return True, False, False  # Show success alert, hide failure alert.

    except Exception as e:
        print(f"Error generating Draugr command: {e}")
        return False, True, False

# Here we run the app on the specified host and port.
if __name__ == "__main__":
    app.run(debug=bfabric_web_apps.DEBUG, port=bfabric_web_apps.PORT, host=bfabric_web_apps.HOST)

