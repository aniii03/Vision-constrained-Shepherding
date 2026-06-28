import plotly.graph_objects as go
import numpy as np

def make_animation(results, alpha):

    L = 70.0
    slit = L/4

    pos_s_dat, _, pos_d_dat, *_, N_escaped = results
    steps = pos_s_dat.shape[0]

    points = int(L*10)

    line_1 = np.zeros(points)
    line_2 = np.linspace(0, L, points)
    line_3 = np.ones(points)
    line_4 = np.linspace(0, L/2 - slit/2, points)
    line_5 = np.linspace(L/2 + slit/2, L, points)

    group_centre = np.average(pos_s_dat,1)
    
    frames = []

    for t in range(steps+10):
        if N_escaped[t] == pos_s_dat.shape[1]:
            break

        sheep_pos = pos_s_dat[t]
        dog_pos = pos_d_dat[t]

        
        frame_data = []

        #Sheep trajectories
        for i in range(pos_s_dat.shape[1]):
            frame_data.append(
                go.Scatter(
                    x=pos_s_dat[:t+1, i, 0],
                    y=pos_s_dat[:t+1, i, 1],
                    mode='lines',
                    line=dict(
                        color='royalblue',
                        width=1
                    ),
                    opacity=0.2,
                    showlegend=False,
                    hoverinfo='skip'
                )
            )

        #Group centre trajectory
        frame_data.append(
            go.Scatter(
                x=group_centre[:t+1, 0],
                y=group_centre[:t+1, 1],
                mode='lines',
                line=dict(
                    color='darkorange',
                    width=2
                ),
                opacity=0.4,
                showlegend=True,
                name="Group Centre trajectory",
                hoverinfo='skip'
            )
        )

        #Dog trajectories
        for i in range(pos_d_dat.shape[1]):
            frame_data.append(
                go.Scatter(
                    x=pos_d_dat[:t+1, i, 0],
                    y=pos_d_dat[:t+1, i, 1],
                    mode='lines',
                    line=dict(
                        color='red',
                        width=2
                    ),
                    opacity=0.4,
                    showlegend=False,
                    hoverinfo='skip'
                )
            )

        #Current sheep positions
        frame_data.append(
            go.Scatter(
                x=sheep_pos[:, 0],
                y=sheep_pos[:, 1],
                mode='markers',
                marker=dict(
                    size=7,
                    color='royalblue'
                ),
                name='Sheep'
            )
        )

        #Current dog position
        frame_data.append(
            go.Scatter(
                x=dog_pos[:, 0],
                y=dog_pos[:, 1],
                mode='markers',
                marker=dict(
                    size=10,
                    color='red'
                ),
                name='Dog'
            )
        )

        frame_data.extend(
            [
                # Boundaries
                go.Scatter(
                    x=line_1,
                    y=line_2,
                    mode='lines',
                    line=dict(color='gray', width=3),
                    showlegend=False
                ),

                go.Scatter(
                    x=line_2,
                    y=line_1,
                    mode='lines',
                    line=dict(color='gray', width=3),
                    showlegend=False
                ),

                go.Scatter(
                    x=line_3 * L,
                    y=line_4,
                    mode='lines',
                    line=dict(color='gray', width=3),
                    showlegend=False
                ),

                go.Scatter(
                    x=line_3 * L,
                    y=line_5,
                    mode='lines',
                    line=dict(color='gray', width=3),
                    showlegend=False
                ),

                go.Scatter(
                    x=line_2,
                    y=line_3 * L,
                    mode='lines',
                    line=dict(color='gray', width=3),
                    showlegend=False
                )
            ]
        )

        frames.append(
            go.Frame(
                data=frame_data,
                name=str(t)
            )
        )

    fig = go.Figure(
        data=frames[0].data,
        frames=frames
    )

    fig.update_layout(

        width=700,
        height=700,

        xaxis=dict(
            range=[-1, L + 1],
            showgrid=False,
            zeroline=False,
            showticklabels=False
        ),

        yaxis=dict(
            range=[-1, L + 1],
            scaleanchor='x',
            showgrid=False,
            zeroline=False,
            showticklabels=False
        ),

        title='Time = 0',

        updatemenus=[

            dict(
                type='buttons',
                showactive=False,
                buttons=[

                    dict(
                        label='▶ Play',
                        method='animate',

                        args=[None,
                              dict(
                                  frame=dict(
                                      duration=100,
                                      redraw=True
                                  ),
                                  transition=dict(duration=0),
                                  fromcurrent=True
                              )]
                    ),

                    dict(
                        label='⏸ Pause',
                        method='animate',

                        args=[[None],
                              dict(
                                  frame=dict(duration=0),
                                  mode='immediate'
                              )]
                    )

                ]
            )

        ],

        sliders=[

            dict(

                currentvalue=dict(
                    prefix='Time = '
                ),

                steps=[

                    dict(

                        method='animate',

                        args=[[str(k)],
                              dict(
                                  frame=dict(
                                      duration=0,
                                      redraw=True
                                  ),
                                  mode='immediate'
                              )],

                        label=str(k)

                    )

                    for k in range(len(frames))

                ]

            )

        ]

    )

    return fig
