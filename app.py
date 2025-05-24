import plotly.express as px
from shiny.express import input, ui, render
from shinywidgets import render_plotly
import pandas as pd
from shiny import reactive
import faicons as fa
import os

ui.tags.style(
    """
    .header_container {
        display: flex;
        align-items: center;
        justify-content: center; /* Centers the content horizontally */
        height: 60px;
    }

    .logo_container {
        margin-right: 5px; /* Adjust the spacing as needed */
        height: 100% !important;
        padding: 10px;
    }

    .logo_container img {
        height: 40px;
    }

    .title_container h1 {
        color: white;
        padding: 5px;
        margin: 0;
    }

    body {
        background-color: #099bd6;
    }

    .modebar{
        display: none;
    }

    .control-label {
        color: #035f86 !important;
        font-family: Arial, sans-serif !important;
        font-size: 24px !important;
        font-weight: bold !important;
    }
    .value-box-container {
        margin-bottom: 30px;  /* adjust spacing here */
    }       
    
    .value-total {
        background-color: #bfdbe8 !important;
    }

    .value-abschluss {
        background-color: #bfdbe8 !important;
    }

    .value-pruefung {
        background-color: #bfdbe8 !important;
    }
    .value-box-title {
        font-size: 20px !important; 
        font-family: Arial, sans-serif !important;
        color: #035f86 !important;
        font-weight: bold !important;
    }
    .value-box-value {
        font-size: 20px !important;
        font-family: Arial, sans-serif !important;
        color: #035f86 !important;
        font-weight: bold !important;
    }

    .graph-section {
        margin-bottom: 30px;
    }

    body, .shiny-input-container, label, .card-header, .dataTables_wrapper {
        color: #035f86 !important;
        font-family: Arial, sans-serif !important;
        font-size: 14px !important;
    }
    
    .dataTable td {
        color: #035f86 !important;
        font-family: Arial, sans-serif !important;
        font-size: 14px !important;
    }

/* Header row */
    .dataTable thead th {
        color: #035f86 !important;
        font-weight: bold !important;
        font-family: Arial, sans-serif !important;
    }

/* Filter input labels and controls */
    .dataTables_wrapper .dataTables_filter label,
    .dataTables_wrapper .dataTables_length label,
    .dataTables_wrapper .dataTables_info,
    .dataTables_wrapper .dataTables_paginate {
        color: #035f86 !important;
        font-family: Arial, sans-serif !important;
    }

    """
)

with ui.div(class_ = "header_container"):
    with ui.div(class_ = "logo_container"):
        @render.image  
        def image():
            app_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(app_dir, "dehst.png")
            return {"src": image_path, "width": "180px"}
    with ui.div(class_ = "title_container"):
        ui.h1("Controlling Dashboard", class_ = "title")

#ui.page_opts(title="Controlling Dashboard", fillable=False)
ICONS = {
    "user": fa.icon_svg("user", "regular"),
    "wallet": fa.icon_svg("wallet"),
    "hourglass": fa.icon_svg("hourglass", "solid"),
}


app_dir = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.join(app_dir, "mock_data.xlsx")
xls = pd.ExcelFile(excel_path)
sheet_names = xls.sheet_names
#sheet_names = [name.replace(" ", "_") for name in sheet_names]

@reactive.calc
def excel_data():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(app_dir, "mock_data.xlsx")
    xls = pd.ExcelFile(excel_path)
    return {sheet: pd.read_excel(xls, sheet_name=sheet) for sheet in xls.sheet_names}

@reactive.calc
def data():
    return excel_data()[input.sheet_name()]


with ui.sidebar(bg="#bfdbe8", open='open'):  
            ui.input_select(
                "sheet_name",
                "Select a team:",
                choices=sheet_names,
                selected=sheet_names[0],
                multiple=False,)
            ui.input_action_button("update", "Update", class_="btn-primary")

with ui.div(class_="value-box-container"):
    with ui.layout_columns(fill=False):
        with ui.value_box(showcase=ICONS["user"], class_="value-total"):
            "Total AZ"
            @render.express
            def total_AZ():
                total_az = sum(df["AZ"].count() for df in excel_data().values())
                f"{total_az:,} Anträge"

        with ui.value_box(showcase=ICONS["wallet"], class_="value-abschluss"):
            "Abgeschlossene AZ"
            @render.express
            def abschluss_AZ():
                total = sum(
                (df["BS"] == "AS").sum()
                for df in excel_data().values()
                )
                f"{total:,}"

        with ui.value_box(showcase=ICONS["hourglass"], class_="value-pruefung"):
            "In Prüfung"
            @render.express
            def pruef_AZ():
                total = sum(
                (df["BS"] == "IP").sum()
                for df in excel_data().values()
                )
                f"{total:,} "

with ui.div(class_="graph-section"):
    with ui.layout_column_wrap(width = 1/2):
        with ui.card():
            ui.card_header()
            @render_plotly
            def bearbeitung():
                df = data().copy()
                df = df.groupby('Team_no')['BS'].value_counts()
                df = df.reset_index(name='counts')
                color_map = {
                            "IB": "#035f86",
                            "IP": "#bfdbe8",
                            "AS": "#3c9726"
                            }
                fig = px.bar(df, x='Team_no', y='counts', color='BS', title=f"Bearbeitungstatus for {input.sheet_name()}", 
                            color_discrete_map=color_map)
                fig.update_layout(
                    title_font_color="#035f86",
                    font=dict(
                        color="#035f86",
                        family="Arial"
                    ),
                    legend=dict(
                        font=dict(color="#035f86")
                    ),
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                return fig
            
        with ui.card():
            ui.card_header()
            @render_plotly
            def pruefung():
                df = data().copy()
                df = df.groupby('Team_no')['PS'].value_counts()
                df = df.reset_index(name='counts')
                color_map = {
                            "AV": "#035f86",
                            "AE": "#bfdbe8",
                            "KAE": "#3c9726"
                            }
                fig = px.bar(df, x='Team_no', y='counts', color='PS', title=f"Prüfstatus for {input.sheet_name()}", 
                            color_discrete_map=color_map)
                fig.update_layout(
                    title_font_color="#035f86",
                    font=dict(
                        color="#035f86",
                        family="Arial"
                    ),
                    legend=dict(
                        font=dict(color="#035f86")
                    ),
                    plot_bgcolor="rgba(0,0,0,0)",
                )
                return fig

with ui.card():
    ui.card_header("Raw Data")
    @render.data_frame
    def data_frame():
        df = data().copy()
        return render.DataTable (df, filters = True, selection_mode="row")
