import logging
import dash
import dash_core_components as dcc
import dash_html_components as html
from app_code import rpg_data as rd, parse_life_paths as lp

LOGGER = logging.getLogger('gui')
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
dash_app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

skill_options = [{'label': 'None', 'value': 'None'}]
for skill in sorted(rd.CHAR_DATA.skill_dict):
    skill_options.append({'label': skill, 'value': skill})

dash_app.layout = html.Div([
    html.H1("Search for the following skills in the same lifepath."),
    dcc.Dropdown(id='skill_1', options=skill_options),
    dcc.Dropdown(id='skill_2', options=skill_options),
    dcc.Dropdown(id='skill_3', options=skill_options),
    dcc.Dropdown(id='skill_4', options=skill_options),
    html.Button("Submit", id='submit', n_clicks=0),
    html.Br(),
    html.Br(),
    html.Div(id='results')
])


@dash_app.callback(
    dash.dependencies.Output('results', 'children'),
    [
        dash.dependencies.Input('submit', 'n_clicks'),
    ],
    [
        dash.dependencies.State('skill_1', 'value'),
        dash.dependencies.State('skill_2', 'value'),
        dash.dependencies.State('skill_3', 'value'),
        dash.dependencies.State('skill_4', 'value'),
    ]
)
def search_lifepaths(submit_n_clicks, skill_1, skill_2, skill_3, skill_4):
    if submit_n_clicks == 0:
        return []

    output = []
    skill_list = []

    if skill_1 is not None and skill_1 != 'None':
        skill_list.append(skill_1)
    if skill_2 is not None and skill_2 != 'None':
        skill_list.append(skill_2)
    if skill_3 is not None and skill_3 != 'None':
        skill_list.append(skill_3)
    if skill_4 is not None and skill_4 != 'None':
        skill_list.append(skill_4)

    skill_count = len(skill_list)

    if skill_count == 0:
        LOGGER.info("Request to search life paths.  No skills selected")
        return html.Div(html.B("No skills selected"))

    match_df = rd.LIFEPATH_DATA.skill_df[rd.LIFEPATH_DATA.skill_df[lp.SKILL].isin(skill_list)].set_index(
        [lp.PROFESSION_FULL, lp.SKILL]).count(level=lp.PROFESSION_FULL)
    match_dict = match_df[match_df[lp.REQUIREMENTS] >= skill_count].to_dict(orient="index")
    match_count = len(match_dict)

    LOGGER.info("Request to search life paths.  skill_count=%d skills=%s match_count=%d",
                skill_count, skill_list, match_count)
    if match_count == 0:
        output.append(html.Div(html.B("No matches found")))
    else:
        cell_style = dict(cellspacing=10, verticalAlign='top')
        output.append(html.H1("Matched %d Lifepaths" % match_count))
        row_data = [
            html.Tr([
                html.Th('Group'),
                html.Th('Path'),
                html.Th('Requirements'),
            ])
        ]

        for lifepath in match_dict:
            lifepath_tokens = lifepath.split(':')
            group = lifepath_tokens[0].strip()
            path = ':'.join(lifepath_tokens[1:]).strip()
            requirement_list = []
            for requirement_token in rd.LIFEPATH_DATA.lifepath_dict[lifepath][lp.REQUIREMENTS]:
                requirement_list.append(html.Div(requirement_token))
            if len(rd.LIFEPATH_DATA.lifepath_dict[lifepath][lp.REQUIREMENTS]) == 0:
                requirement_list.append(html.Div('None'))

            row_data.append(
                html.Tr(
                    [
                        html.Td(group, style=cell_style),
                        html.Td(path, style=cell_style),
                        html.Td(html.Div(requirement_list), style=cell_style)
                    ]
                )
            )

        output.append(
            html.Table(row_data)
        )

    return output


if __name__ == '__main__':
    dash_app.run_server(debug=True)
