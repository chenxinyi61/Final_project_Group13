from shiny import App, render, ui
import geopandas as gpd
import pandas as pd
import altair as alt

state_gdf = gpd.read_file("cb_2018_us_state_500k.shp")
# excluding Alaska (02), Hawaii (15), and Puerto Rico (72) for better view
state_gdf = state_gdf[~state_gdf['STATEFP'].isin(['02', '15', '72'])]
merged_data = pd.read_csv("merged_data.csv")

app_ui = ui.page_fluid(
    ui.panel_title("US Heatmaps: Unemployment Rate and Minimum Wage"),
    ui.input_slider(
        id="year_slider",
        label="Select Year:",
        min=2014,
        max=2024,
        value=2014,
        step=1
    ),
    ui.input_switch(
        id="show_min_wage",
        label="Show Minimum Wage Plot",
        value=False 
    ),
    ui.output_ui("main_plot")  
)

def server(input, output, session):
    @output
    @render.ui
    def main_plot():
        year = input.year_slider()
        show_min_wage = input.show_min_wage()

        filtered_data = merged_data[merged_data["Year"] == year]
        geo_data = state_gdf.merge(filtered_data, left_on="NAME", right_on="State", how="left")

        if show_min_wage:  
            chart = alt.Chart(geo_data).mark_geoshape().encode(
                color='Min_Wage:Q',
                tooltip=['NAME:N', 'Min_Wage:Q']
            ).properties(
                width=800,
                height=600,
                title=f"Minimum Wage ({year})"
            ).project('albersUsa')
        else:  
            chart = alt.Chart(geo_data).mark_geoshape().encode(
                color='Unemployment_Rate:Q',
                tooltip=['NAME:N', 'Unemployment_Rate:Q']
            ).properties(
                width=800,
                height=600,
                title=f"Unemployment Rate ({year})"
            ).project('albersUsa') # chatGPT suggests to add this project for better view

        return ui.HTML(chart.to_html()) # we has problem showing the plot, chatGPT helped us debugged with this code

app = App(app_ui, server)
