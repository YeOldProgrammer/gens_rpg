import logging
import json
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from app_code import rpg_data as rd, parse_life_paths as lp
from app_code import gen_character as gc

LOGGER = logging.getLogger('gui')
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

skill_options = [{'label': 'None', 'value': 'None'}]
for skill in sorted(rd.CHAR_DATA.skill_dict):
    skill_options.append({'label': skill, 'value': skill})

div_character_start = html.Div(
    id='div_character_start',
    style=dict(display="none"),
    children=[
        html.H3("Enter Starting Data"),
        html.Button("Submit", id='btn_accept_start', style=dict(marginLeft=10)),
    ],
)


div_select_life_path = html.Div(
    id='div_select_life_path',
    style=dict(display='none'),
    children=[
        html.Div([
            html.Label("Lifepath skill filter:  ",
                       style=dict(verticalAlign='middle', display='inline-block', fontWeight='bold')),
            dcc.Checklist(id='options', options=[{'label': 'Childhood', 'value': 'childhood'}], value=['childhood'],
                          style=dict(verticalAlign='middle', display='inline-block', marginLeft="10px")),
            dcc.Dropdown(id='skills', options=skill_options, multi=True,
                         style=dict(display='inline-block', width="70%", verticalAlign="middle", marginLeft="10px")),
        ]),
        html.P(id='results'),
    ]
)


div_confirm_life_path = html.Div(
    id='div_confirm_life_path',
    style=dict(display='none'),
    children=[
        html.H3("Select Life Path"),
        html.Button("Accept", id='btn_submit_life_path', style=dict(marginLeft=10)),
   ]
)


div_confirm_general_skills = html.Div(
    id='div_confirm_general_skills',
    style=dict(display='none'),
    children=[
        html.H3("Select Life Path"),
        html.Button("Accept", id='btn_submit_general_skills', style=dict(marginLeft=10)),
   ]
)


div_confirm_results = html.Div(
    id='div_confirm_results',
    style=dict(display='none'),
    children=[
        html.H3("Select Life Path"),
        html.Button("Accept", id='btn_accept_life_path', style=dict(marginLeft=10)),
   ]
)


app.layout = html.Div([
    html.Div(children=[
        html.H1("Character Generation"),
        html.Button("Back", id='btn_back', style=dict(display='none', marginLeft=10)),
        html.Button("Clear", id='btn_clear', style=dict(display='inline-block', marginLeft=10)),
        html.Button("Load", id='btn_load', style=dict(display='inline-block', marginLeft=10)),
        html.Hr(),
    ], style=dict(float='left', width="100%", display="inline-block")),

    div_character_start,
    div_select_life_path,
    div_confirm_life_path,
    div_confirm_general_skills,
    div_confirm_results,
    html.Div(id='character_data', style={'display': 'none'})
])


@app.callback(
    [
        dash.dependencies.Output('div_character_start', 'style'),
        dash.dependencies.Output('div_select_life_path', 'style'),
        dash.dependencies.Output('div_confirm_life_path', 'style'),
        dash.dependencies.Output('div_confirm_general_skills', 'style'),
        dash.dependencies.Output('div_confirm_results', 'style'),
    ],
    [
        dash.dependencies.Input('btn_back', 'n_clicks'),
        dash.dependencies.Input('btn_clear', 'n_clicks'),
        dash.dependencies.Input('btn_load', 'n_clicks'),
        dash.dependencies.Input('btn_accept_start', 'n_clicks'),
        dash.dependencies.Input('btn_submit_life_path', 'n_clicks'),
        dash.dependencies.Input('btn_submit_general_skills', 'value'),
        dash.dependencies.Input('btn_accept_life_path', 'n_clicks'),
    ],
    [
        dash.dependencies.State('character_data', 'children'),
    ]
)
def master_callback(back_clicks, clear_clicks, load_clicks, accept_start_clicks, submit_life_path_clicks,
                    submit_general_skills_clicks, accept_life_path_clicks, character_data):

    if character_data is not None:
        try:
            json.loads(character_data)
        except Exception as error_text:
            LOGGER.error("Failed to load character data - %s", str(error_text))
            character_data = gc.BLANK_CHARACTER
    else:
        character_data = gc.BLANK_CHARACTER

    LOGGER.info("back:%s clear:%s load:%s accept_start:%s submit_life_path:%s submit_general_skills:%s accept_life_path:%s\n%s",
                back_clicks, clear_clicks, load_clicks, accept_start_clicks, submit_life_path_clicks,
                submit_general_skills_clicks, accept_life_path_clicks, json.dumps(character_data, indent=4)
                )

    display_none = dict(display='none')
    display_show = dict(display='inline')

    if character_data['potential_used'] == 0:
        return display_show, display_none, display_none, display_none, display_none

    return display_none, display_none, display_none, display_none, display_none


@app.callback(
    dash.dependencies.Output('results', 'children'),
    [
        dash.dependencies.Input('skills', 'value'),
        dash.dependencies.Input('options', 'value'),
    ],
)
def refresh_lifepaths(skill_list, options):
    output = []
    if skill_list is not None:
        skill_count = len(skill_list)
    else:
        skill_count = 0

    if skill_count > 0:
        if 'childhood' in options:
            base_df = rd.LIFEPATH_DATA.skill_df[rd.LIFEPATH_DATA.skill_df[lp.SHEET_NAME] == 'Childhood']
        else:
            base_df = rd.LIFEPATH_DATA.skill_df[rd.LIFEPATH_DATA.skill_df[lp.SHEET_NAME] != 'Childhood']

        match_df = base_df[
            base_df[lp.SKILL].isin(skill_list)
        ].set_index([lp.PROFESSION_FULL, lp.SKILL]).count(level=lp.PROFESSION_FULL)
        match_dict = match_df[match_df[lp.REQUIREMENTS] >= skill_count].to_dict(orient="index")
        match_count = len(match_dict)
    else:
        match_dict = {}
        for key in rd.LIFEPATH_DATA.lifepath_dict.keys():
            if 'childhood' in options and rd.LIFEPATH_DATA.lifepath_dict[key][lp.SHEET_NAME] != 'Childhood':
                continue
            elif 'childhood' not in options and rd.LIFEPATH_DATA.lifepath_dict[key][lp.SHEET_NAME] == 'Childhood':
                continue

            match_dict[key] = {'requirements': 0}
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
                html.Th('Row'),
                html.Th('Skills'),
                html.Th('Traits'),
                html.Th('Requirements'),
            ])
        ]

        for lifepath in sorted(match_dict):
            lifepath_tokens = lifepath.split(':')
            group = lifepath_tokens[0].strip()
            path = ':'.join(lifepath_tokens[1:]).strip()
            row = rd.LIFEPATH_DATA.lifepath_dict[lifepath][lp.SHEET_ROW]
            requirement_list = []
            skills_list = []
            trait_list = []
            for requirement_token in rd.LIFEPATH_DATA.lifepath_dict[lifepath][lp.REQUIREMENTS]:
                requirement_list.append(html.Div(requirement_token))
            if len(rd.LIFEPATH_DATA.lifepath_dict[lifepath][lp.REQUIREMENTS]) == 0:
                requirement_list.append(html.Div('None'))

            for skill_group in lp.SKILL_GROUPS:
                if skill_group not in rd.LIFEPATH_DATA.lifepath_dict[lifepath]:
                    continue
                for this_skill in rd.LIFEPATH_DATA.lifepath_dict[lifepath][skill_group]:
                    if this_skill in skills_list:
                        continue
                    skills_list.append(this_skill)

            for trait in rd.LIFEPATH_DATA.lifepath_dict[lifepath][lp.TRAITS]:
                trait_list.append(trait)

            skill_div_list = []
            trait_div_list = []
            for this_skill in sorted(skills_list):
                display_skill = this_skill.title()
                if display_skill in rd.CHAR_DATA.skill_dict:
                    display_skill = display_skill + ' ' + rd.CHAR_DATA.skill_dict[display_skill]['potential']
                else:
                    LOGGER.warning("SKILL NO POTENTIAL (%s)", this_skill)
                skill_div_list.append(html.Div(display_skill))

            for this_trait in sorted(trait_list):
                trait_div_list.append(html.Div(this_trait))

            row_data.append(
                html.Tr(
                    [
                        html.Td(group, style=cell_style),
                        html.Td(path, style=cell_style),
                        html.Td(row, style=cell_style),
                        html.Td(html.Div(skill_div_list), style=cell_style),
                        html.Td(html.Div(trait_div_list), style=cell_style),
                        html.Td(html.Div(requirement_list), style=cell_style)
                    ]
                )
            )

        output.append(
            html.Table(row_data)
        )

    return output


if __name__ == '__main__':
    app.run_server(debug=True)
