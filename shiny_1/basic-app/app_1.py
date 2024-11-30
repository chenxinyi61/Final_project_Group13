from shiny import App, render, ui
import pandas as pd
import altair as alt

# Load the merged data
merged_race_data = pd.read_csv("merged_race_data.csv")

# Ensure the state list is in alphabetical order
states = sorted(merged_race_data["State"].unique())

# Define the UI
app_ui = ui.page_fluid(
    ui.panel_title("Unemployment Rate vs. Minimum Wage by State"),
    
    # Dropdown menu for state selection
    ui.input_select(
        id="state_dropdown",
        label="Select a State:",
        choices=states,
        selected=states[0]  # Default selection is the first state in alphabetical order
    ),
    
    # Output plot
    ui.output_ui("scatter_plot")
)

# Define the server logic
def server(input, output, session):
    
    @output
    @render.ui
    def scatter_plot():
        # Filter the data for the selected state
        selected_state = input.state_dropdown()
        state_data = merged_race_data[merged_race_data["State"] == selected_state]
        
        # Create the Altair scatter plot
        chart = alt.Chart(state_data).mark_circle(size=100).encode(
            x=alt.X('Min_Wage:Q', scale=alt.Scale(zero=False), title='Minimum Wage ($)'),
            y=alt.Y('Unemployment_Rate:Q', title='Unemployment Rate (%)'),
            color=alt.Color('Group:N', title='Race'),
            tooltip=['Year', 'Unemployment_Rate', 'Min_Wage', 'Group']
        ).properties(
            title=f"Unemployment Rate vs Minimum Wage for {selected_state}",
            width=400,
            height=300
        )
        
        # Add regression lines
        regression_lines = alt.Chart(state_data).transform_regression(
            'Min_Wage', 'Unemployment_Rate', groupby=['Group']
        ).mark_line().encode(
            x=alt.X('Min_Wage:Q', scale=alt.Scale(zero=False), title='Minimum Wage ($)'),
            y=alt.Y('Unemployment_Rate:Q', title='Unemployment Rate (%)'),
            color=alt.Color('Group:N', title='Race')
        )
        
        # Combine scatter plot and regression lines
        combined_chart = chart + regression_lines
        
        # Render the chart as HTML
        return ui.HTML(combined_chart.to_html())

# Create the Shiny app
app = App(app_ui, server)
