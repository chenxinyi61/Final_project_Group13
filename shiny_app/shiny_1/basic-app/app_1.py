from shiny import App, render, ui
import pandas as pd
import altair as alt

merged_race_data = pd.read_csv("merged_race_data.csv")

states = sorted(merged_race_data["State"].unique())

app_ui = ui.page_fluid(
    ui.panel_title("Unemployment Rate vs. Minimum Wage by State and Race"),
    ui.input_select(
        id="state_dropdown",
        label="Select a State:",
        choices=states,
        selected=states[0]
    ),
    ui.output_ui("scatter_plot")
)

def server(input, output, session):
    
    @output
    @render.ui
    def scatter_plot():
        selected_state = input.state_dropdown()
        state_data = merged_race_data[merged_race_data["State"] == selected_state]
        
        chart = alt.Chart(state_data).mark_circle(size=100).encode(
            x=alt.X('Min_Wage:Q', scale=alt.Scale(zero=False), title='Minimum Wage ($)'),
            y=alt.Y('Unemployment_Rate:Q', title='Unemployment Rate (%)'),
            color=alt.Color('Group:N', title='Race', legend=alt.Legend(labelFontSize=14, titleFontSize=16)),
            tooltip=['Year', 'Unemployment_Rate', 'Min_Wage', 'Group']
        ).properties(
            title=f"Unemployment Rate vs Minimum Wage for {selected_state}",
            width=800,
            height=600
        )
        
        regression_lines = alt.Chart(state_data).transform_regression(
            'Min_Wage', 'Unemployment_Rate', groupby=['Group']
        ).mark_line().encode(
            x=alt.X('Min_Wage:Q', scale=alt.Scale(zero=False), title='Minimum Wage ($)'),
            y=alt.Y('Unemployment_Rate:Q', title='Unemployment Rate (%)'),
            color=alt.Color('Group:N', title='Race')
        )
        
        combined_chart = chart + regression_lines
        
        return ui.HTML(combined_chart.to_html()) # we has problem showing the plot, chatGPT helped us debugged with this code

app = App(app_ui, server)
