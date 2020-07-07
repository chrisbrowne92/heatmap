import pandas as pd
import plotly.offline as py
import plotly.graph_objs as go

# parameters & toggles
draw_legend = True  # draw boxes & text for legend
label_font_size = 13  # font size for data labels
fig_size = 1000  # size of figure
# colours
colour_1 = 'rgb(190, 226, 222)'
colour_2 = 'rgb(108, 200, 197)'
colour_3 = 'rgb(27, 173, 172)'
colour_4 = 'rgb(14, 133, 136)'
colour_5 = 'rgb(0, 93, 100)'
red = 'rgb(250, 86, 93)'
orange = 'rgb(247, 150, 70)'
colourscale = [[0, colour_1],
               [0.2, colour_3],
               [1, colour_5]]

# import data & clean
country_codes = pd.read_csv('countries.csv').set_index('country')
name_to_code = country_codes['code'].to_dict()
code_to_priority = dict(set(zip(country_codes['code'], country_codes['priority']))) # create mapping from country to priority

projects = pd.read_csv('projects_anon.csv')
projects['country_code'] = projects['Country'].map(name_to_code)  # country name to ISO-3 code
projects.sort_values('country_code', inplace=True)
projects = projects[projects['Level of engagement'] != 'None']  # remove projects with no level of engagement

counts = projects['country_code'].value_counts().sort_index() # determine number of projects in each country


def get_trace(priority):
    # function to create correct trace, dependent on priority
    line_width = 2
    # set outline parameters for country, based on priority
    if priority == 0:
        outline_params = dict()  # no special outline
    elif priority == 1:
        outline_params = dict(marker=dict(line=dict(
            color=red,
            width=line_width
        )))  # red outline
    else:
        outline_params = dict(marker=dict(line=dict(
            color=orange,
            width=line_width
        )))  # orange outline
    mask = counts.index.map(code_to_priority) == priority  # mask for countries with given priority
    out = dict(
        type='choropleth',
        locations=list(counts[mask].index),
        locationmode='ISO-3',
        colorscale=colourscale,
        z=list(counts[mask]),
        zmin=0,
        zmax=counts.max(),
        showscale=False)  # create generic properties of trace
    out.update(outline_params)  # add outline parameters to trace
    return out


data_p0 = get_trace(0)  # non-priority
data_p2 = get_trace(2)  # priority 1
data_p1 = get_trace(1)  # priority 2
labels = dict(
    type='scattergeo',
    locations=counts.index,
    locationmode='ISO-3',
    # text=['<b>' + str(x) + '</b>' for x in counts],
    text=counts,
    mode='text',
    textfont=dict(color='black', size=label_font_size))  # data labels

layout = dict(
        geo={'scope': 'africa'},
        width=fig_size,
        height=fig_size,
        title='Number of projects, by country',
        title_x=0.5)

if draw_legend:
    x0 = 0.2
    y0 = 0.45
    y_step = 0.03
    x_pad = 0.03
    white_space = '   '

    title_box = dict(
        x=x0,
        y=y0 - (0 * y_step),
        yanchor='middle',
        borderpad=2,
        bordercolor='rgb(255, 255, 255)',
        borderwidth=0,
        text='<b>Priority Countries</b>',
        align='center',
        showarrow=False)
    p1_box = dict(
        x=x0,
        y=y0 - (1 * y_step),
        yanchor='middle',
        borderpad=2,
        bordercolor='rgb(250, 86, 93)',
        borderwidth=2,
        text=white_space,
        align='center',
        showarrow=False)
    p2_box = dict(
        x=x0,
        y=y0 - (2 * y_step),
        yanchor='middle',
        borderpad=2,
        bordercolor='rgb(247, 150, 70)',
        borderwidth=2,
        text=white_space,
        align='center',
        showarrow=False)
    p0_box = dict(
        x=x0,
        y=y0 - (3 * y_step),
        yanchor='middle',
        borderpad=2.5,
        bordercolor='rgb(0, 0, 0)',
        borderwidth=1,
        text=white_space,
        align='center',
        showarrow=False)
    p1_text = dict(
        x=x0 + x_pad,
        y=y0 - (1 * y_step),
        yanchor='middle',
        borderpad=2,
        bordercolor='rgb(250, 86, 93)',
        borderwidth=0,
        text='Priority 1',
        align='center',
        showarrow=False)
    p2_text = dict(
        x=x0 + x_pad,
        y=y0 - (2 * y_step),
        yanchor='middle',
        borderpad=2,
        bordercolor='rgb(247, 150, 70)',
        borderwidth=0,
        text='Priority 2',
        align='center',
        showarrow=False)
    p0_text = dict(
        x=x0 + x_pad,
        y=y0 - (3 * y_step),
        yanchor='middle',
        borderpad=2,
        bordercolor='rgb(0, 0, 0)',
        borderwidth=0,
        text='Non-priority',
        align='center',
        showarrow=False)
    layout = layout.update(dict(annotations=[title_box, p1_box, p2_box, p0_box, p1_text, p2_text, p0_text]))

map = go.Figure(data=[data_p0, data_p2, data_p1, labels], layout=layout)
py.plot(map)

map.write_image('project_counts_heatmap.png')  # save as png
