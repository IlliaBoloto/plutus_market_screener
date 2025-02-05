import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.graph_objects as go

from scr.data_handler import DataHandler
from scr.technical_ind import TechnicalIndicators
from scr.simulations import MonteCarloSimulation
from scr.news_line import get_news_from_newsdata, get_news_from_newsapi

# Initialize the app with suppress_callback_exceptions=True.
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Market Analysis Dashboard"


def create_layout():
    return html.Div(
        style={
            'backgroundColor': '#121212',
            'color': '#E0E0E0',
            'fontFamily': '"Poppins", sans-serif',
            'padding': '20px'
        },
        children=[
            html.H1("Market Analysis Dashboard", style={'textAlign': 'center', 'fontSize': '36px'}),

            # Flex container for ticker input, interval dropdown, and search button.
            html.Div(
                style={
                    'display': 'flex',
                    'justifyContent': 'center',
                    'alignItems': 'center',
                    'gap': '10px',
                    'marginBottom': '20px'
                },
                children=[
                    # Ticker input box.
                    dcc.Input(
                        id="ticker-input",
                        type="text",
                        placeholder="Enter Ticker (e.g., AAPL, BTC-USD)",
                        style={
                            'width': '30%',
                            'padding': '10px',
                            'borderRadius': '8px',
                            'border': '1px solid #444',
                            'backgroundColor': '#1E1E1E',
                            'color': '#E0E0E0',
                            'fontSize': '16px'
                        }
                    ),
                    # Interval dropdown styled similarly to technical indicators inputs.
                    dcc.Dropdown(
                        id="interval-input",
                        options=[
                            {'label': '1d', 'value': '1d'},
                            {'label': '5d', 'value': '5d'},
                            {'label': '1wk', 'value': '1wk'},
                            {'label': '1mo', 'value': '1mo'},
                            {'label': '3mo', 'value': '3mo'},
                        ],
                        value="1d",  # Default interval
                        clearable=False,
                        searchable=False,
                        style={
                            'width': '60px',  # Compact width
                            'padding': '1px',  # Reduced padding for a smaller look
                            'border': '1px solid #444',
                            'borderRadius': '4px',
                            'backgroundColor': '#f0f0f0',  # Lighter background similar to technical inputs
                            'color': '#000',  # Black text
                            'fontSize': '14px',
                            'textAlign': 'center'
                        }
                    ),
                    # Search button.
                    html.Button(
                        "Search",
                        id="search-button",
                        n_clicks=0,
                        style={
                            'padding': '10px 20px',
                            'borderRadius': '8px',
                            'border': 'none',
                            'backgroundColor': '#1DB954',
                            'color': '#FFF',
                            'fontSize': '16px',
                            'cursor': 'pointer'
                        }
                    )
                ]
            ),

            # Tabs re-ordered: Monte Carlo Simulation first, then Technical Indicators, then News Feed.
            dcc.Tabs(
                id="tabs",
                value="montecarlo",  # Default tab set to Monte Carlo Simulation
                children=[
                    dcc.Tab(label="🔄 Monte Carlo Simulation", value="montecarlo"),
                    dcc.Tab(label="📈 Technical Indicators", value="technical"),
                    dcc.Tab(label="📰 News Feed", value="news"),
                ],
                style={'borderBottom': '2px solid #444'}
            ),

            # Loading spinner wrapping the tab content.
            dcc.Loading(
                id="loading-spinner",
                type="cube",
                color="#1DB954",
                children=[html.Div(id="tab-content")],
                style={'marginTop': '300px'}  # Adjust the value as needed
            )

        ]
    )


app.layout = create_layout()


# ----------------------------------------------------------------------
# Render Technical Indicators Tab (unchanged)
# ----------------------------------------------------------------------
def render_technical_indicators(df):
    # (Your existing technical indicators layout and inputs)
    # Here’s a minimal version for demonstration:
    dropdown_options = [{'label': str(i), 'value': i} for i in range(1, 101)]
    input_style = {
        'width': '50px',  # Even smaller width
        'padding': '2px',
        'border': '1px solid #444',
        'borderRadius': '4px',
        'backgroundColor': '#f0f0f0',  # Lighter background
        'color': '#000',  # Black text
        'fontSize': '12px',
        'textAlign': 'left'
    }
    inputs_row = html.Div(
        style={
            'display': 'flex',
            'justifyContent': 'center',
            'alignItems': 'center',
            'gap': '20px',
            'marginBottom': '20px'
        },
        children=[
            html.Div([
                html.Label("SMA", style={'marginRight': '5px', 'color': '#E0E0E0'}),
                dcc.Dropdown(
                    id="sma-input",
                    options=dropdown_options,
                    value=14,
                    clearable=False,
                    searchable=False,
                    style=input_style
                )
            ], style={'display': 'flex', 'alignItems': 'center'}),
            html.Div([
                html.Label("EMA", style={'marginRight': '5px', 'color': '#E0E0E0'}),
                dcc.Dropdown(
                    id="ema-input",
                    options=dropdown_options,
                    value=14,
                    clearable=False,
                    searchable=False,
                    style=input_style
                )
            ], style={'display': 'flex', 'alignItems': 'center'}),
            html.Div([
                html.Label("RSI", style={'marginRight': '5px', 'color': '#E0E0E0'}),
                dcc.Dropdown(
                    id="rsi-input",
                    options=dropdown_options,
                    value=14,
                    clearable=False,
                    searchable=False,
                    style=input_style
                )
            ], style={'display': 'flex', 'alignItems': 'center'}),
            html.Div([
                html.Label("MACD Short", style={'marginRight': '5px', 'color': '#E0E0E0'}),
                dcc.Dropdown(
                    id="macd-short-input",
                    options=dropdown_options,
                    value=12,
                    clearable=False,
                    searchable=False,
                    style=input_style
                )
            ], style={'display': 'flex', 'alignItems': 'center'}),
            html.Div([
                html.Label("MACD Long", style={'marginRight': '5px', 'color': '#E0E0E0'}),
                dcc.Dropdown(
                    id="macd-long-input",
                    options=dropdown_options,
                    value=26,
                    clearable=False,
                    searchable=False,
                    style=input_style
                )
            ], style={'display': 'flex', 'alignItems': 'center'}),
            html.Div([
                html.Label("Bollinger", style={'marginRight': '5px', 'color': '#E0E0E0'}),
                dcc.Dropdown(
                    id="bollinger-input",
                    options=dropdown_options,
                    value=20,
                    clearable=False,
                    searchable=False,
                    style=input_style
                )
            ], style={'display': 'flex', 'alignItems': 'center'})
        ]
    )
    results_table = html.Div(
        style={'width': '100%'},
        children=[
            html.H3("Technical Indicators", style={'color': '#E0E0E0', 'textAlign': 'center'}),
            html.Table(
                style={'width': '100%', 'borderCollapse': 'collapse'},
                children=[
                    html.Thead([
                        html.Tr([
                            html.Th("Indicator", style={'color': '#E0E0E0', 'textAlign': 'left', 'width': '33%'}),
                            html.Th("Value", style={'color': '#E0E0E0', 'textAlign': 'center', 'width': '33%'}),
                            html.Th("Signal", style={'color': '#E0E0E0', 'textAlign': 'center', 'width': '34%'})
                        ])
                    ]),
                    html.Tbody(id="technical-table-body")
                ]
            )
        ]
    )
    return html.Div(
        style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'},
        children=[inputs_row, results_table]
    )


@app.callback(
    Output("technical-table-body", "children"),
    Input("sma-input", "value"),
    Input("ema-input", "value"),
    Input("rsi-input", "value"),
    Input("macd-short-input", "value"),
    Input("macd-long-input", "value"),
    Input("bollinger-input", "value"),
    State("ticker-input", "value"),
    State("interval-input", "value")
)
def update_technical_indicators(sma_period, ema_period, rsi_period,
                                macd_short, macd_long, bollinger_period,
                                ticker, interval):
    # For debugging, you can uncomment the next line:
    # print("update_technical_indicators triggered with:", sma_period, ema_period, ticker, interval)
    if not ticker:
        return [
            html.Tr([
                html.Td("Enter a ticker first.", colSpan=3,
                        style={'color': 'grey', 'textAlign': 'center'})
            ])
        ]

    data_handler = DataHandler()
    df = data_handler.fetch_stock_data(ticker, period="1y", interval=interval)
    if isinstance(df, dict) and "error" in df:
        return [
            html.Tr([
                html.Td(f"Error: {df['error']}", colSpan=3,
                        style={'color': 'red', 'textAlign': 'center'})
            ])
        ]

    # Compute technical indicators.
    ti = TechnicalIndicators(df)
    df = ti.simple_moving_average(sma_period)
    df = ti.exponential_moving_average(ema_period)
    df = ti.relative_strength_index(rsi_period)
    df = ti.macd(macd_short, macd_long)
    df = ti.bollinger_bands(bollinger_period)

    # Build a dictionary of indicator names to (value, signal)
    indicators = {
        "SMA": (df[f"SMA_{sma_period}"].iloc[-1], df[f"Signal_SMA_{sma_period}"].iloc[-1]),
        "EMA": (df[f"EMA_{ema_period}"].iloc[-1], df[f"Signal_EMA_{ema_period}"].iloc[-1]),
        "RSI": (df["RSI"].iloc[-1], df["Signal_RSI"].iloc[-1]),
        "MACD": (df[f"MACD_{macd_short}_{macd_long}"].iloc[-1], df[f"Signal_MACD_{macd_short}_{macd_long}"].iloc[-1]),
        "Bollinger Bands": (
        df[f"Bollinger_Mid_{bollinger_period}"].iloc[-1], df[f"Signal_Bollinger_{bollinger_period}_2"].iloc[-1])
    }

    # Build the table rows.
    return [
        html.Tr([
            html.Td(indicator, style={'padding': '10px', 'fontWeight': 'bold'}),
            html.Td(f"{value:.2f}", style={'textAlign': 'center'}),
            html.Td(
                signal,
                style={
                    'textAlign': 'center',
                    'color': 'green' if "Buy" in signal else 'red'
                }
            )
        ])
        for indicator, (value, signal) in indicators.items()
    ]


# ----------------------------------------------------------------------
# Monte Carlo Simulation Tab Layout & Graph (unchanged from previous version)
# ----------------------------------------------------------------------
def render_montecarlo_tab(ticker, interval):
    simulation_inputs = html.Div(
        style={
            'display': 'flex',
            'justifyContent': 'center',
            'alignItems': 'center',
            'gap': '20px',
            'marginBottom': '20px'
        },
        children=[
            html.Div([
                html.Label("Simulations", style={'marginRight': '5px', 'color': '#E0E0E0'}),
                dcc.Dropdown(
                    id="num-simulations",
                    options=[{'label': str(x), 'value': x} for x in [500, 1000, 2000, 5000]],
                    value=1000,
                    clearable=False,
                    searchable=False,
                    style={
                        'width': '80px',
                        'padding': '2px',
                        'border': '1px solid #444',
                        'borderRadius': '4px',
                        'backgroundColor': '#f0f0f0',
                        'color': '#000',
                        'fontSize': '12px',
                        'textAlign': 'center'
                    }
                )
            ], style={'display': 'flex', 'alignItems': 'center'}),
            html.Div([
                html.Label("Days", style={'marginRight': '5px', 'color': '#E0E0E0'}),
                dcc.Dropdown(
                    id="num-days",
                    options=[{'label': str(x), 'value': x} for x in [15, 30, 60, 90]],
                    value=30,
                    clearable=False,
                    searchable=False,
                    style={
                        'width': '80px',
                        'padding': '2px',
                        'border': '1px solid #444',
                        'borderRadius': '4px',
                        'backgroundColor': '#f0f0f0',
                        'color': '#000',
                        'fontSize': '12px',
                        'textAlign': 'center'
                    }
                )
            ], style={'display': 'flex', 'alignItems': 'center'}),
            html.Div([
                html.Label("Mu", style={'marginRight': '5px', 'color': '#E0E0E0'}),
                dcc.Dropdown(
                    id="mu-input",
                    options=[
                        {'label': 'Auto', 'value': 'Auto'},
                        {'label': '0.01', 'value': 0.01},
                        {'label': '0.02', 'value': 0.02},
                        {'label': '0.03', 'value': 0.03}
                    ],
                    value='Auto',
                    clearable=False,
                    searchable=False,
                    style={
                        'width': '80px',
                        'padding': '2px',
                        'border': '1px solid #444',
                        'borderRadius': '4px',
                        'backgroundColor': '#f0f0f0',
                        'color': '#000',
                        'fontSize': '12px',
                        'textAlign': 'center'
                    }
                )
            ], style={'display': 'flex', 'alignItems': 'center'}),
            html.Div([
                html.Label("Sigma", style={'marginRight': '5px', 'color': '#E0E0E0'}),
                dcc.Dropdown(
                    id="sigma-input",
                    options=[
                        {'label': 'Auto', 'value': 'Auto'},
                        {'label': '0.1', 'value': 0.1},
                        {'label': '0.2', 'value': 0.2},
                        {'label': '0.3', 'value': 0.3}
                    ],
                    value='Auto',
                    clearable=False,
                    searchable=False,
                    style={
                        'width': '80px',
                        'padding': '2px',
                        'border': '1px solid #444',
                        'borderRadius': '4px',
                        'backgroundColor': '#f0f0f0',
                        'color': '#000',
                        'fontSize': '12px',
                        'textAlign': 'center'
                    }
                )
            ], style={'display': 'flex', 'alignItems': 'center'})
        ]
    )
    simulation_graph_placeholder = html.Div(id="montecarlo-graph")
    return html.Div(
        style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'},
        children=[simulation_inputs, simulation_graph_placeholder]
    )


def render_montecarlo_simulation(ticker, num_simulations, num_days, mu, sigma, interval):
    # Convert 'Auto' values to None.
    if mu == 'Auto':
        mu = None
    if sigma == 'Auto':
        sigma = None

    data_handler = DataHandler()
    df_hist = data_handler.fetch_stock_data(ticker, period="1y", interval=interval)
    historical_dates = df_hist.index
    historical_price = df_hist["Close"]

    simulator = MonteCarloSimulation(ticker, period="1y", interval=interval)
    simulated_prices = simulator.run_simulation(
        num_simulations=num_simulations,
        num_days=num_days,
        mu=mu,
        sigma=sigma
    )

    # Create future dates based on the last historical date
    last_date = historical_dates[-1]
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=num_days)

    # If simulated_prices is not already a DataFrame, convert it.
    # (Assuming simulated_prices is a NumPy array with shape (num_days, num_simulations))
    if not isinstance(simulated_prices, pd.DataFrame):
        simulated_prices = pd.DataFrame(simulated_prices, index=future_dates)
    else:
        simulated_prices.index = future_dates

    # Calculate the min and max across simulation runs (columns) for each day
    simulated_min = simulated_prices.min(axis=1)
    simulated_max = simulated_prices.max(axis=1)

    # Build the Plotly figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=historical_dates,
        y=historical_price,
        mode='lines',
        name='Historical Price',
        line=dict(color='blue', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=simulated_max,
        mode='lines',
        name='Simulated Max',
        line=dict(color='lightgrey', width=1),
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=simulated_min,
        mode='lines',
        name='Simulated Range',
        fill='tonexty',
        fillcolor='rgba(30,144,255,0.3)',
        line=dict(color='lightgrey', width=1),
        showlegend=True
    ))
    fig.update_layout(
        title={
            'text': "Monte Carlo Simulation",
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=24)
        },
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_dark",
        height=700,
        width=1200,
        paper_bgcolor="#121212",
        plot_bgcolor="#121212",
        font=dict(color="#E0E0E0", family='"Poppins", sans-serif'),
        margin=dict(l=50, r=50, t=70, b=50)
    )

    return html.Div(
        [dcc.Graph(figure=fig, style={'width': '100%', 'height': '700px'})],
        style={'width': '100%', 'maxWidth': '1200px', 'margin': '0 auto'}
    )

# ----------------------------------------------------------------------
# Main Callback to update tab content.
# ----------------------------------------------------------------------
@app.callback(
    Output("tab-content", "children"),
    Input("search-button", "n_clicks"),
    Input("tabs", "value"),
    Input("ticker-input", "value"),
    Input("interval-input", "value"),
    prevent_initial_call=True
)
def update_content(n_clicks, tab, ticker, interval):
    if not ticker:
        return html.Div("Enter a ticker (e.g., AAPL, BTC-USD) to start.",
                        style={'textAlign': 'center', 'marginTop': '20px'})
    try:
        data_handler = DataHandler()
        df = data_handler.fetch_stock_data(ticker, period="1y", interval=interval)
        if isinstance(df, dict) and "error" in df:
            return html.Div(f"Error: {df['error']}",
                            style={'color': 'red', 'textAlign': 'center'})
        if tab == "montecarlo":
            return render_montecarlo_tab(ticker, interval)
        elif tab == "technical":
            return render_technical_indicators(df)
        elif tab == "news":
            return render_news_feed(ticker)
    except Exception as e:
        return html.Div(f"An error occurred: {str(e)}",
                        style={'color': 'red', 'textAlign': 'center'})


# ----------------------------------------------------------------------
# Callback to update the Monte Carlo simulation graph.
# ----------------------------------------------------------------------
@app.callback(
    Output("montecarlo-graph", "children"),
    Input("num-simulations", "value"),
    Input("num-days", "value"),
    Input("mu-input", "value"),
    Input("sigma-input", "value"),
    State("ticker-input", "value"),
    State("interval-input", "value")
)
def update_montecarlo_graph(num_simulations, num_days, mu, sigma, ticker, interval):
    if not ticker:
        return html.Div("Enter a ticker first.", style={'textAlign': 'center'})
    return render_montecarlo_simulation(ticker, num_simulations, num_days, mu, sigma, interval)


# ----------------------------------------------------------------------
# Render News Feed
# ----------------------------------------------------------------------
def render_news_feed(ticker):
    try:
        news_df1 = get_news_from_newsdata(ticker)
        news_df2 = get_news_from_newsapi(ticker)
        df_combined = pd.concat([news_df1, news_df2]).drop_duplicates().sort_index(ascending=False)
        return html.Div([
            html.H3(f"Latest News for {ticker}"),
            html.Ul([
                html.Li(
                    html.A(row["Title"], href=row["URL"], target="_blank")
                )
                for _, row in df_combined.iterrows()
            ])
        ])
    except ValueError:
        return html.Div(
            f"No news found for {ticker}.",
            style={'color': 'red', 'textAlign': 'center'}
        )


if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)
