from shiny import App, render, ui
import geopandas as gpd
import pandas as pd
import altair as alt

# Load the U.S. geo shapefile
state_gdf = gpd.read_file("cb_2018_us_state_500k.shp")

# Exclude Alaska, Hawaii, and Puerto Rico
state_gdf = state_gdf[~state_gdf['STATEFP'].isin(['02', '15', '72'])]

# Load the unemployment and minimum wage dataset (merged_data.csv)
merged_data = pd.read_csv("merged_data.csv")

# Shiny UI
app_ui = ui.page_fluid(
    ui.panel_title("US Heatmaps: Unemployment Rate and Minimum Wage"),
    
    # Input slider for selecting the year
    ui.input_slider(
        id="year_slider",
        label="Select Year:",
        min=2014,
        max=2024,
        value=2014,
        step=1
    ),
    
    # Switch to toggle minimum wage plot display
    ui.input_switch(
        id="show_min_wage",
        label="Show Minimum Wage Plot",
        value=False  # Default is to hide the Minimum Wage plot initially
    ),
    
    # Output placeholder for the unemployment plot (Always visible)
    ui.output_ui("unemployment_plot"),
    
    # Output placeholder for the minimum wage plot (Conditional rendering)
    ui.output_ui("min_wage_plot")
)

# Shiny Server Logic
def server(input, output, session):
    
    # Function to generate the heatmap for unemployment rate (always shown)
    @output
    @render.ui
    def unemployment_plot():
        year = input.year_slider()
        
        # Filter data for selected year
        filtered_data = merged_data[merged_data["Year"] == year]
        
        # Merge with geo data for mapping
        geo_data = state_gdf.merge(filtered_data, left_on="NAME", right_on="State", how="left")
        
        # Create an Altair heatmap for unemployment rate
        chart = alt.Chart(geo_data).mark_geoshape().encode(
            color='Unemployment_Rate:Q',
            tooltip=['NAME:N', 'Unemployment_Rate:Q']
        ).properties(
            width=500,
            height=300,
            title=f"Unemployment Rate ({year})"
        ).project('albersUsa')
        
        return ui.HTML(chart.to_html())  # Render the chart using HTML

    # Function to generate the heatmap for minimum wage (conditionally shown based on switch)
    @output
    @render.ui
    def min_wage_plot():
        if input.show_min_wage():  # Check if the switch is ON
            year = input.year_slider()
            
            # Filter data for selected year
            filtered_data = merged_data[merged_data["Year"] == year]
            
            # Merge with geo data for mapping
            geo_data = state_gdf.merge(filtered_data, left_on="NAME", right_on="State", how="left")
            
            # Create an Altair heatmap for minimum wage
            chart = alt.Chart(geo_data).mark_geoshape().encode(
                color='Min_Wage:Q',
                tooltip=['NAME:N', 'Min_Wage:Q']
            ).properties(
                width=500,
                height=300,
                title=f"Minimum Wage ({year})"
            ).project('albersUsa')
            
            return ui.HTML(chart.to_html())  # Render the chart using HTML
        else:
            return ui.div()  # Return an empty div when switch is off

# Create the Shiny app
app = App(app_ui, server)