# ============================================================
# HR ATTRITION INTELLIGENCE DASHBOARD
# FIXED VERSION — Path Fix + Dropdown Dark Fix
# ============================================================

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import os  # FIXED: os import added for safe path handling

# ── COLOR SYSTEM ─────────────────────────────────────────────
BG_MAIN      = '#050d18'
BG_CARD      = '#0a1628'
BG_CHART     = '#0d1f35'
BORDER       = '#1a3a5c'
BLUE_PRIMARY = '#0ea5e9'
BLUE_DARK    = '#0369a1'
BLUE_LIGHT   = '#38bdf8'
BLUE_GLOW    = '#7dd3fc'
SUCCESS      = '#10b981'
WARNING      = '#f59e0b'
DANGER       = '#ef4444'
TEXT_HEAD    = '#f0f9ff'
TEXT_BODY    = '#bae6fd'
TEXT_MUTED   = '#64748b'
GRID         = '#0f2744'

# ── CHART TEMPLATE ───────────────────────────────────────────
def ct(title):
    return dict(
        title=dict(
            text=title,
            font=dict(size=14, color=TEXT_HEAD, family='Inter, Segoe UI'),
            x=0.02, y=0.98
        ),
        plot_bgcolor=BG_CHART,
        paper_bgcolor=BG_CARD,
        font=dict(color=TEXT_BODY, family='Inter, Segoe UI', size=11),
        xaxis=dict(gridcolor=GRID, showgrid=True, color=TEXT_MUTED,
                   zeroline=False, showline=False),
        yaxis=dict(gridcolor=GRID, showgrid=True, color=TEXT_MUTED,
                   zeroline=False, showline=False),
        margin=dict(l=50, r=30, t=55, b=40),
        legend=dict(bgcolor=BG_CARD, bordercolor=BORDER, borderwidth=1,
                    font=dict(color=TEXT_BODY))
    )

# ════════════════════════════════════════════════════════════
# DATA — FIXED PATH
# ════════════════════════════════════════════════════════════

# FIXED: __file__ se app.py ki location pakad lo,
#        phir usi folder mein CSV dhundo.
#        Iska faida: chahe kisi bhi folder se run karo, kaam karega.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "WA_Fn-UseC_-HR-Employee-Attrition.csv")

df_full = pd.read_csv(CSV_PATH)  # FIXED: hardcoded path hataya, dynamic path use kiya

df_full.drop(columns=['EmployeeCount', 'Over18',
                       'StandardHours', 'EmployeeNumber'],
             inplace=True)
df_full['Attrition_Num'] = df_full['Attrition'].map({'Yes': 1, 'No': 0})

def age_group(age):
    if age < 25:   return 'Under 25'
    elif age < 35: return '25-34'
    elif age < 45: return '35-44'
    elif age < 55: return '45-54'
    else:          return '55+'

df_full['AgeGroup'] = df_full['Age'].apply(age_group)

def get_risk(row):
    s = 0
    if row['OverTime'] == 'Yes':           s += 3
    if row['JobSatisfaction'] <= 2:        s += 2
    if row['WorkLifeBalance'] <= 2:        s += 2
    if row['MonthlyIncome'] < 3000:        s += 2
    if row['YearsAtCompany'] < 2:          s += 1
    if row['YearsSinceLastPromotion'] > 3: s += 1
    return ('High Risk' if s >= 6 else
            'Medium Risk' if s >= 3 else 'Low Risk')

df_full['RiskCategory'] = df_full.apply(get_risk, axis=1)

# ── FILTER OPTIONS ───────────────────────────────────────────
dept_opts   = [{'label': 'All Departments', 'value': 'All'}] + \
    [{'label': d, 'value': d} for d in sorted(df_full['Department'].unique())]
gender_opts = [{'label': 'All Genders', 'value': 'All'}] + \
    [{'label': g, 'value': g} for g in sorted(df_full['Gender'].unique())]
age_opts    = [{'label': 'All Age Groups', 'value': 'All'}] + \
    [{'label': a, 'value': a} for a in ['Under 25','25-34','35-44','45-54','55+']]

# ════════════════════════════════════════════════════════════
# APP
# ════════════════════════════════════════════════════════════
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# ── FIXED: Complete dropdown dark theme CSS ───────────────────
# Explanation: Dash dropdown React component uses dynamic class names
# So we target BOTH old (.Select-*) AND new (div[class*="..."]) class patterns
app.index_string = '''<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>HR Attrition Intelligence</title>
        {%favicon%}
        {%css%}
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * { font-family: Inter, Segoe UI, sans-serif !important; }
            body { background-color: #050d18 !important; margin: 0; padding: 0; }

            /* ── Scrollbar ── */
            ::-webkit-scrollbar { width: 4px; }
            ::-webkit-scrollbar-track { background: #050d18; }
            ::-webkit-scrollbar-thumb { background: #1a3a5c; border-radius: 2px; }

            /* ══════════════════════════════════════════════════
               DROPDOWN FIX — COMPLETE DARK THEME
               Covers old Dash (.Select-*) + new Dash (div[class*])
               ══════════════════════════════════════════════════ */

            /* --- Container box --- */
            .Select-control,
            .dash-dropdown .Select-control {
                background-color: #0a1628 !important;
                border: 1px solid #1a3a5c !important;
                border-radius: 6px !important;
            }

            /* --- Selected value text --- */
            .Select-value-label,
            .Select--single > .Select-control .Select-value,
            .Select--single > .Select-control .Select-value-label {
                color: #bae6fd !important;
            }

            /* --- Placeholder text --- */
            .Select-placeholder { color: #64748b !important; }

            /* --- Dropdown arrow --- */
            .Select-arrow { border-color: #64748b transparent transparent !important; }
            .is-open > .Select-control .Select-arrow {
                border-color: transparent transparent #64748b !important;
            }

            /* --- Dropdown menu box --- */
            .Select-menu-outer {
                background-color: #0a1628 !important;
                border: 1px solid #1a3a5c !important;
                border-radius: 6px !important;
                box-shadow: 0 8px 32px rgba(0,0,0,0.6) !important;
                z-index: 9999 !important;
            }
            .Select-menu { background-color: #0a1628 !important; }

            /* --- Each option item --- */
            .VirtualizedSelectOption,
            .Select-option {
                background-color: #0a1628 !important;
                color: #bae6fd !important;
                padding: 8px 12px !important;
            }

            /* --- Hovered option --- */
            .VirtualizedSelectFocusedOption,
            .Select-option.is-focused {
                background-color: #0ea5e9 !important;
                color: #ffffff !important;
            }

            /* --- Selected option --- */
            .Select-option.is-selected {
                background-color: #0369a1 !important;
                color: #ffffff !important;
            }

            /* --- Input inside dropdown --- */
            .Select-input > input {
                color: #bae6fd !important;
                background: transparent !important;
            }

            /* --- Focus border glow --- */
            .Select.is-focused > .Select-control,
            .Select.is-focused:not(.is-open) > .Select-control {
                background-color: #0a1628 !important;
                border-color: #0ea5e9 !important;
                box-shadow: 0 0 0 2px rgba(14,165,233,0.25) !important;
            }

            /* ══════════════════════════════════════════════════
               NEW DASH VERSION (React dynamic class names)
               FIXED: Added !important everywhere + more selectors
               ══════════════════════════════════════════════════ */

            /* Control box */
            div[class*="control"] {
                background-color: #0a1628 !important;
                border-color: #1a3a5c !important;
                color: #bae6fd !important;
                box-shadow: none !important;
            }
            div[class*="control"]:hover {
                border-color: #0ea5e9 !important;
            }

            /* Menu dropdown box */
            div[class*="menu"] {
                background-color: #0a1628 !important;
                border: 1px solid #1a3a5c !important;
                box-shadow: 0 8px 32px rgba(0,0,0,0.6) !important;
                z-index: 9999 !important;
            }

            /* Menu list inner scroll area */
            div[class*="MenuList"],
            div[class*="menu-list"] {
                background-color: #0a1628 !important;
            }

            /* Each option */
            div[class*="option"] {
                background-color: #0a1628 !important;
                color: #bae6fd !important;
            }
            div[class*="option"]:hover,
            div[class*="option"][class*="focused"],
            div[class*="option"][class*="selected"] {
                background-color: #0ea5e9 !important;
                color: #ffffff !important;
            }

            /* Selected value text */
            div[class*="singleValue"] {
                color: #bae6fd !important;
            }

            /* Placeholder text */
            div[class*="placeholder"] {
                color: #64748b !important;
            }

            /* Input text while searching/typing */
            div[class*="Input"] input,
            div[class*="input"] input {
                color: #bae6fd !important;
                caret-color: #bae6fd !important;
            }

            /* Dropdown arrow/indicator icons */
            div[class*="indicatorContainer"] svg {
                color: #64748b !important;
                fill: #64748b !important;
            }

            /* Separator line between value and arrow */
            div[class*="indicatorSeparator"] {
                background-color: #1a3a5c !important;
            }

            /* Outer dash-dropdown wrapper */
            .dash-dropdown > div,
            .dash-dropdown {
                background-color: #0a1628 !important;
                color: #bae6fd !important;
            }

        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>'''

# ── KPI CARD ─────────────────────────────────────────────────
def kpi_card(title, value, subtitle, color=BLUE_PRIMARY):
    return dbc.Col(
        html.Div([
            html.Div(value, style={
                'fontSize': '26px', 'fontWeight': '700',
                'color': color, 'lineHeight': '1.1', 'letterSpacing': '-0.5px'
            }),
            html.Div(title, style={
                'fontSize': '10px', 'color': TEXT_MUTED, 'fontWeight': '600',
                'marginTop': '6px', 'textTransform': 'uppercase', 'letterSpacing': '0.8px'
            }),
            html.Div(subtitle, style={
                'fontSize': '10px', 'color': TEXT_MUTED, 'marginTop': '2px'
            })
        ], style={
            'backgroundColor': BG_CARD,
            'border': f'1px solid {BORDER}',
            'borderTop': f'2px solid {color}',
            'borderRadius': '8px',
            'padding': '16px 14px',
            'textAlign': 'left',
            'height': '100%'
        }),
        xs=6, sm=4, md=3, lg=True
    )

# ── FILTER COLUMN ────────────────────────────────────────────
def filter_col(label, id_, options, value):
    return dbc.Col([
        html.Label(label, style={
            'color': TEXT_MUTED, 'fontSize': '10px', 'fontWeight': '600',
            'textTransform': 'uppercase', 'letterSpacing': '1px',
            'marginBottom': '6px', 'display': 'block'
        }),
        dcc.Dropdown(
            id=id_,
            options=options,
            value=value,
            clearable=False,
            style={
                'backgroundColor': BG_CARD,
                'color': TEXT_BODY,
                'border': f'1px solid {BORDER}',  # FIXED: border added inline too
            }
        )
    ], md=4)

# ── CHART BOX ────────────────────────────────────────────────
def chart_box(graph_id, height='320px'):
    return html.Div(
        dcc.Graph(
            id=graph_id,
            config={'displayModeBar': False},
            style={'height': height}
        ),
        style={
            'backgroundColor': BG_CARD,
            'borderRadius': '10px',
            'border': f'1px solid {BORDER}',
            'padding': '4px',
            'height': '100%'
        }
    )

# ── DIVIDER ──────────────────────────────────────────────────
def divider(text):
    return html.Div([
        html.Span(text, style={
            'color': TEXT_MUTED, 'fontSize': '10px',
            'fontWeight': '600', 'letterSpacing': '2px'
        })
    ], style={
        'borderBottom': f'1px solid {BORDER}',
        'paddingBottom': '8px', 'marginBottom': '16px', 'marginTop': '8px'
    })

# ════════════════════════════════════════════════════════════
# LAYOUT
# ════════════════════════════════════════════════════════════
app.layout = html.Div([

    # ── HEADER ───────────────────────────────────────────────
    html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Span('HR', style={
                        'color': BLUE_PRIMARY, 'fontWeight': '800', 'fontSize': '26px'
                    }),
                    html.Span(' Attrition Intelligence', style={
                        'color': TEXT_HEAD, 'fontWeight': '300', 'fontSize': '26px'
                    }),
                ]),
                html.P('Employee Risk & Retention Analysis Dashboard',
                       style={'color': TEXT_MUTED, 'margin': '2px 0 0 0',
                              'fontSize': '12px', 'letterSpacing': '0.3px'})
            ], md=8),
            dbc.Col([
                html.Div([
                    html.Span('IBM HR Analytics', style={'color': TEXT_MUTED, 'fontSize': '11px'}),
                    html.Br(),
                    html.Span('1,470 Employees | 2024', style={
                        'color': BLUE_LIGHT, 'fontSize': '11px', 'fontWeight': '600'
                    })
                ], style={'textAlign': 'right', 'marginTop': '8px'})
            ], md=4)
        ])
    ], style={
        'backgroundColor': BG_CARD,
        'padding': '20px 32px',
        'borderBottom': f'1px solid {BORDER}',
        'boxShadow': '0 1px 0 rgba(14,165,233,0.25)'
    }),

    # ── MAIN ─────────────────────────────────────────────────
    html.Div([

        # Filters
        html.Div([
            dbc.Row([
                filter_col('Department', 'dept-filter',   dept_opts,   'All'),
                filter_col('Gender',     'gender-filter', gender_opts, 'All'),
                filter_col('Age Group',  'age-filter',    age_opts,    'All'),
            ])
        ], style={
            'backgroundColor': BG_CARD, 'border': f'1px solid {BORDER}',
            'borderRadius': '10px', 'padding': '16px 20px', 'marginBottom': '20px'
        }),

        # KPIs
        html.Div(id='kpi-cards', style={'marginBottom': '20px'}),

        # Charts Row 1
        divider('ATTRITION ANALYSIS'),
        dbc.Row([
            dbc.Col(chart_box('chart-dept'), md=6, style={'marginBottom': '16px'}),
            dbc.Col(chart_box('chart-age'),  md=6, style={'marginBottom': '16px'}),
        ]),

        # Charts Row 2
        dbc.Row([
            dbc.Col(chart_box('chart-gender'),   md=4, style={'marginBottom': '16px'}),
            dbc.Col(chart_box('chart-overtime'), md=4, style={'marginBottom': '16px'}),
            dbc.Col(chart_box('chart-risk'),     md=4, style={'marginBottom': '16px'}),
        ]),

        # Charts Row 3
        divider('ROLE & COMPENSATION ANALYSIS'),
        dbc.Row([
            dbc.Col(chart_box('chart-jobrole', '370px'), md=6, style={'marginBottom': '16px'}),
            dbc.Col(chart_box('chart-salary',  '370px'), md=6, style={'marginBottom': '16px'}),
        ]),

        # Footer
        html.Div([
            html.Span(
                'HR Attrition Intelligence  •  Python & Plotly Dash  •  IBM HR Analytics Dataset',
                style={'color': TEXT_MUTED, 'fontSize': '10px'}
            )
        ], style={
            'textAlign': 'center', 'padding': '20px',
            'borderTop': f'1px solid {BORDER}', 'marginTop': '8px'
        })

    ], style={'padding': '24px 32px'})

], style={'backgroundColor': BG_MAIN, 'minHeight': '100vh'})

# ════════════════════════════════════════════════════════════
# CALLBACK
# ════════════════════════════════════════════════════════════
@app.callback(
    Output('kpi-cards',      'children'),
    Output('chart-dept',     'figure'),
    Output('chart-age',      'figure'),
    Output('chart-gender',   'figure'),
    Output('chart-overtime', 'figure'),
    Output('chart-risk',     'figure'),
    Output('chart-jobrole',  'figure'),
    Output('chart-salary',   'figure'),
    Input('dept-filter',     'value'),
    Input('gender-filter',   'value'),
    Input('age-filter',      'value'),
)
def update(dept, gender, age):

    df = df_full.copy()
    if dept   != 'All': df = df[df['Department'] == dept]
    if gender != 'All': df = df[df['Gender']     == gender]
    if age    != 'All': df = df[df['AgeGroup']   == age]

    total     = len(df)
    att       = int(df['Attrition_Num'].sum())
    rate      = round((att / total) * 100, 1) if total > 0 else 0
    active    = total - att
    income    = f"${df['MonthlyIncome'].mean():,.0f}"
    avg_age_v = round(df['Age'].mean(), 1)
    tenure    = round(df['YearsAtCompany'].mean(), 1)
    high_risk = len(df[df['RiskCategory'] == 'High Risk'])
    ot_pct    = round(len(df[df['OverTime'] == 'Yes']) / total * 100, 1) if total > 0 else 0

    cards = dbc.Row([
        kpi_card('Total Employees',  f'{total:,}',    'Headcount',          BLUE_PRIMARY),
        kpi_card('Attrition Cases',  f'{att:,}',      'Employees left',     DANGER),
        kpi_card('Attrition Rate',   f'{rate}%',      'Industry avg: 10%',
                 DANGER if rate > 15 else WARNING),
        kpi_card('Active Employees', f'{active:,}',   'Currently working',  SUCCESS),
        kpi_card('Avg Income',       income,           'Monthly salary',     SUCCESS),
        kpi_card('Average Age',      f'{avg_age_v}y', 'Years old',          BLUE_LIGHT),
        kpi_card('Avg Tenure',       f'{tenure}y',    'Years at company',   BLUE_LIGHT),
        kpi_card('High Risk',        f'{high_risk}',  'May leave soon',     DANGER),
        kpi_card('Overtime %',       f'{ot_pct}%',    'Working overtime',   WARNING),
    ], className='g-2')

    # Chart 1 — Attrition by Department
    d = df.groupby('Department')['Attrition_Num'].mean() * 100
    d = d.reset_index().sort_values('Attrition_Num')
    f1 = go.Figure(go.Bar(
        x=d['Attrition_Num'], y=d['Department'], orientation='h',
        marker=dict(color=d['Attrition_Num'],
                    colorscale=[[0, BLUE_PRIMARY], [0.5, WARNING], [1, DANGER]],
                    showscale=False),
        text=[f"{v:.1f}%" for v in d['Attrition_Num']],
        textposition='outside', textfont=dict(color=TEXT_BODY, size=12)
    ))
    f1.update_layout(**ct('Attrition Rate by Department'))

    # Chart 2 — Attrition by Age Group
    age_order = ['Under 25', '25-34', '35-44', '45-54', '55+']
    a = df.groupby('AgeGroup')['Attrition_Num'].mean() * 100
    a = a.reindex(age_order).reset_index()
    f2 = go.Figure(go.Scatter(
        x=a['AgeGroup'], y=a['Attrition_Num'],
        mode='lines+markers',
        line=dict(color=BLUE_PRIMARY, width=2.5),
        marker=dict(size=8, color=BG_CARD,
                    line=dict(color=BLUE_PRIMARY, width=2.5)),
        fill='tozeroy', fillcolor='rgba(14,165,233,0.12)'
    ))
    f2.update_layout(**ct('Attrition Rate by Age Group'))

    # Chart 3 — Attrition by Gender (Donut)
    g = df.groupby('Gender')['Attrition_Num'].sum().reset_index()
    f3 = go.Figure(go.Pie(
        labels=g['Gender'], values=g['Attrition_Num'],
        hole=0.65,
        marker=dict(colors=[BLUE_PRIMARY, BLUE_LIGHT],
                    line=dict(color=BG_MAIN, width=2)),
        textinfo='label+percent',
        textfont=dict(color=TEXT_HEAD, size=12)
    ))
    f3.update_layout(
        title=dict(text='Attrition by Gender',
                   font=dict(size=14, color=TEXT_HEAD), x=0.02),
        paper_bgcolor=BG_CARD, plot_bgcolor=BG_CHART,
        font=dict(color=TEXT_BODY),
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(bgcolor=BG_CARD, bordercolor=BORDER,
                    font=dict(color=TEXT_BODY))
    )

    # Chart 4 — Overtime Impact
    f4 = go.Figure()
    for att_val, color, label in zip(
        ['Yes', 'No'], [DANGER, BLUE_PRIMARY], ['Left', 'Stayed']
    ):
        ot = df.groupby('OverTime').apply(
            lambda x, a=att_val: (x['Attrition'] == a).sum()
        ).reset_index()
        ot.columns = ['OverTime', 'Count']
        f4.add_trace(go.Bar(
            name=label, x=ot['OverTime'], y=ot['Count'],
            marker=dict(color=color),
            text=ot['Count'], textposition='auto',
            textfont=dict(color=TEXT_HEAD)
        ))
    f4.update_layout(barmode='group', **ct('Overtime Impact on Attrition'))

    # Chart 5 — Risk Distribution
    r = df['RiskCategory'].value_counts().reset_index()
    r.columns = ['RiskCategory', 'Count']
    risk_colors = {'High Risk': DANGER, 'Medium Risk': WARNING, 'Low Risk': SUCCESS}
    f5 = go.Figure(go.Bar(
        x=r['RiskCategory'], y=r['Count'],
        marker=dict(color=[risk_colors.get(x, BLUE_PRIMARY) for x in r['RiskCategory']],
                    line=dict(color=BG_MAIN, width=1)),
        text=r['Count'], textposition='auto',
        textfont=dict(color=TEXT_HEAD, size=13)
    ))
    f5.update_layout(**ct('Employee Risk Distribution'))

    # Chart 6 — Attrition by Job Role
    jr = df.groupby('JobRole')['Attrition_Num'].mean() * 100
    jr = jr.reset_index().sort_values('Attrition_Num')
    f6 = go.Figure(go.Bar(
        x=jr['Attrition_Num'], y=jr['JobRole'], orientation='h',
        marker=dict(color=jr['Attrition_Num'],
                    colorscale=[[0, BLUE_DARK], [0.5, BLUE_PRIMARY], [1, BLUE_GLOW]],
                    showscale=False),
        text=[f"{v:.1f}%" for v in jr['Attrition_Num']],
        textposition='outside', textfont=dict(color=TEXT_BODY, size=11)
    ))
    f6.update_layout(**ct('Attrition Rate by Job Role'))

    # Chart 7 — Income vs Attrition (Box Plot)
    f7 = go.Figure()
    for att_val, color, fill_color, label in zip(
        ['Yes', 'No'],
        [DANGER, SUCCESS],
        ['rgba(239,68,68,0.18)', 'rgba(16,185,129,0.18)'],
        ['Left Company', 'Stayed']
    ):
        f7.add_trace(go.Box(
            y=df[df['Attrition'] == att_val]['MonthlyIncome'],
            name=label,
            marker=dict(color=color),
            line=dict(color=color),
            fillcolor=fill_color,
            boxmean=True
        ))
    f7.update_layout(**ct('Monthly Income vs Attrition'))

    return cards, f1, f2, f3, f4, f5, f6, f7

# ── RUN ──────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, port=8050)