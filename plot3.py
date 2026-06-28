import plotly.graph_objects as go
import numpy as np


def make_animation(results, alpha):

    L = 70.0
    slit = L/4
    alpha = alpha * np.pi / 180
    pos_s_dat, _, pos_d_dat, vel_d_dat, *_, N_escaped = results

    steps = pos_s_dat.shape[0]

    points = int(L*10)

    line_1 = np.zeros(points)
    line_2 = np.linspace(0, L, points)
    line_3 = np.ones(points)
    line_4 = np.linspace(0, L/2 - slit/2, points)
    line_5 = np.linspace(L/2 + slit/2, L, points)

    group_centre = np.average(pos_s_dat,1)

    frames = []

    for t in range(steps):
        if N_escaped[t] == pos_s_dat.shape[1]:
            break

        sheep_pos = pos_s_dat[t]
        dog_pos = pos_d_dat[t]
        dog_vel = vel_d_dat[t]

        traces = []

        #Sheep trajectories
        for i in range(pos_s_dat.shape[1]):
            traces.append(
                go.Scattergl(
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
        traces.append(
            go.Scattergl(
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
        traces.append(
            go.Scattergl(
                x=pos_d_dat[:t+1, 0],
                y=pos_d_dat[:t+1, 1],
                mode='lines',
                line=dict(
                    color='red',
                    width=2
                ),
                opacity=0.2,
                showlegend=False,
                hoverinfo='skip'
            )
        )
        # sheep
        traces.append(
            go.Scatter(
                x=sheep_pos[:,0],
                y=sheep_pos[:,1],
                mode='markers',
                marker=dict(
                    size=7,
                    color='royalblue'
                ),
                name='Sheep'
            )
        )

        # dog
        traces.append(
            go.Scatter(
                x=[dog_pos[0]],
                y=[dog_pos[1]],
                mode='markers',
                marker=dict(
                    size=10,
                    color='red'
                ),
                name='Dog'
            )
        )

        # vision cone
        if not np.isnan(dog_vel).any():

            angle = np.arctan2(dog_vel[1], dog_vel[0])

            theta = np.linspace(
                angle - alpha/2,
                angle + alpha/2,
                100
            )

            x_cone = np.concatenate((
                [dog_pos[0]],
                dog_pos[0] + L*np.cos(theta),
                [dog_pos[0]]
            ))

            y_cone = np.concatenate((
                [dog_pos[1]],
                dog_pos[1] + L*np.sin(theta),
                [dog_pos[1]]
            ))

            traces.append(
                go.Scatter(
                    x=x_cone,
                    y=y_cone,
                    fill='toself',
                    fillcolor='rgba(255,255,0,0.2)',
                    line=dict(color='rgba(255,255,0,0)'),
                    showlegend=False
                )
            )

        frames.append(
            go.Frame(
                data=traces,
                name=str(t),
                layout=go.Layout(
                    title_text=f"Time = {t}"
                )
            )
        )

    fig = go.Figure(
        data=frames[0].data,
        frames=frames
    )

    # walls (constant)
    for x, y in [
        (line_1, line_2),
        (line_2, line_1),
        (line_3*L, line_4),
        (line_3*L, line_5),
        (line_2, line_3*L)
    ]:

        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode='lines',
                line=dict(
                    color='gray',
                    width=3
                ),
                showlegend=False
            )
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
                        args=[
                            None,
                            dict(
                                frame=dict(
                                    duration=100,
                                    redraw=True
                                ),
                                transition=dict(duration=0),
                                fromcurrent=True
                            )
                        ]
                    ),

                    dict(
                        label='⏸ Pause',
                        method='animate',
                        args=[
                            [None],
                            dict(
                                frame=dict(duration=0),
                                mode='immediate'
                            )
                        ]
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
                        args=[
                            [str(k)],
                            dict(
                                frame=dict(
                                    duration=0,
                                    redraw=True
                                ),
                                mode='immediate'
                            )
                        ],
                        label=str(k)
                    )

                    for k in range(len(frames))
                ]
            )
        ]
    )

    return fig
