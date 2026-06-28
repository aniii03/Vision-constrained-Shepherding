import streamlit as st
import importlib
import matplotlib.pyplot as plt
import numpy as np
import time

st.markdown(
    """
    <h1 style='text-align: center; font-size: 30px;'>
        Vision Constrained Shepherding
    </h1>
    <h6 style='text-align: center; color: gray;'>
        Multi-agent simulation of shepherding under limited field of view
    </h6>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    st.header("Simulation Parameters")
    header ="Simulation Parameters",
    n_dogs = st.slider("Number of herders",1,5,1)
    n_sheep = st.slider("Number of flocking agents",5,20,14)
    vision_angle = st.slider("Vision angle",30,360,360)
    eps = st.slider("Noise ε",0.0,1.0,0.3,0.05)

SIM_MAP = {
    (1, True): ("simulation1", "plot1"),
    ("multi", True): ("simulation2", "plot2"),
    (1, False): ("simulation3", "plot3"),
    ("multi", False): ("simulation4", "plot4"),
}

key = (
    1 if n_dogs == 1 else "multi",
    vision_angle == 360
)

sim_name, plot_name = SIM_MAP[key]
sim = importlib.import_module(sim_name)
plot = importlib.import_module(plot_name)

with st.status("Calculating trajectories...", expanded=False) as status:
    results = sim.run_simulation(
                n_sheep,
                n_dogs,
                eps,
                vision_angle
            )
    status.update(label="Building animation...")
    fig = plot.make_animation(results, vision_angle)
    status.update(label="Done!", state="complete")
st.plotly_chart(fig, width='stretch')

