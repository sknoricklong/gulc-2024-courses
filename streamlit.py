import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import datetime
import re
import random


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    st.set_page_config(
        page_title="Search GUKC Courses",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    df_full = pd.read_csv("./matched_courses.csv")
    median_rating = df_full['recommend_1'].median()
    median_courses = df_full['accessible_1'].median()

    last_selected = None

    with st.sidebar:
        options = ["See all courses", "Search for courses"]
        type = st.radio("", options, index=0)

        if type == "Search for courses":
            selected_term = st.text_input("Add search term:", "environment").strip()

            # Replace 3 letters followed by a space and then 3 numbers with a hyphen in place of the space
            selected_term = re.sub(r'([A-Za-z]{3}) (\d{3})', r'\1-\2', selected_term)

            # Replace 3 letters immediately followed by 3 numbers with a hyphen in between
            selected_term = re.sub(r'([A-Za-z]{3})(\d{3})', r'\1-\2', selected_term)

            # If there's an alternate term, add it to the search pattern
            search_pattern = selected_term

            df = df_full[(df_full["Course.Name"].str.contains(search_pattern, case=False, regex=True)) |
                         (df_full["Section.Content"].str.contains(search_pattern, case=False, regex=True)) |
                         (df_full["Professor_1"].str.contains(search_pattern, case=False, regex=True))]
        elif type == "See all courses":
            df = df_full.copy()

        # Add slider for minimum n_courses
        min_courses = st.slider("Minimum Number of Courses", 0, int(df_full['n_courses'].max()), value=0)

            # Filter dataframe based on slider value
        df = df[(df['n_courses'] >= min_courses) | (df['n_courses'].isna())]

        st.markdown("👉 [Feedback?](https://forms.gle/dVQtp7XwVhqnv5Dw8)")


    def plot_scatterplot(df):
        # Updated y axis to represent 'accessible_1'
        fig = px.scatter(df, x='recommend_1', y='accessible_1', hover_name="Course.Name")



        # Hover template without additional clearing price data
        def create_hovertemplate(row):
            template = ("<b>%{hovertext}</b><br>"
                        "<b>Course ID:</b> %{customdata[0]}<br>"
                        "<b>Professor:</b> %{customdata[1]}<br>"
                        "<b>Rating:</b> %{customdata[2]:.2f}<br>"
                        "<b>Accessible:</b> %{customdata[3]}<br>"
                        "<b>Number of Courses:</b> %{customdata[4]}")
            return template

        hovertemplates = df.apply(create_hovertemplate, axis=1)

        fig.update_xaxes(title_text="Recommendation Score")
        fig.update_yaxes(title_text="Accessibility Score")

        # Updated customdata array to match the new hover template
        fig.update_traces(
            marker=dict(color='blue', line=dict(width=0, color='DarkSlateGrey')),
            customdata=df[['Course.ID', 'Professor_1', 'recommend_1', 'accessible_1', 'n_courses']].values,
            hovertemplate=hovertemplates
        )

        fig.update_layout(hoverlabel=dict(font_size=12))
        fig.update_layout(width=900)

        # Add horizontal line
        fig.add_shape(
            type='line',
            x0=median_rating,
            y0=0,
            x1=median_rating,
            y1=5,
            yref='y',
            line=dict(
                color='grey',
                dash='dash',
            )
        )

        # Add vertical line
        fig.add_shape(
            type='line',
            x0=0,
            y0=median_courses,
            x1=5.1,
            y1=median_courses,
            xref='x',
            line=dict(
                color='grey',
                dash='dash',
            )
        )

        # Calculate 5th percentile for both recommend_1 and accessible_1
        min_recommend = df_full['recommend_1'].quantile(0.05) - .05
        max_recommend = 5.05

        min_accessible = df_full['accessible_1'].quantile(0.05) - .05
        max_accessible = 5.05

        fig.update_xaxes(range=[min_recommend, max_recommend])
        fig.update_yaxes(range=[min_accessible, max_accessible])

        fig.update_layout(showlegend=False)

        fig.update_layout(uniformtext_minsize=15)

        st.plotly_chart(fig)


    st.header("🗓️ Compare Spring 2024 Courses at Georgetown Law")
    st.info("""
        - Explore courses by instructor **quality** and **accessibility outside class**; each point is a professor's average score when teaching that course
        - Hover over points to see course scores; filter for **all** or **specific** courses
        """)
    plot_scatterplot(df)

    df.sort_values(by='recommend_1', ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)

    st.header("🥇 Courses Ranked by  Professor's Average Rating")
    st.info("👉 Scroll right for course url on my.harvard.edu")
    df_with_previous = df[
        ['Professor_1', 'Course.Name', 'recommend_1', 'accessible_1', 'n_courses', 'Professor_1.Link', 'Section.Content', 'Course.ID', 'Time']].sort_values(
        by=['recommend_1', 'n_courses'], ascending=[False, True]).reset_index(drop=True)
    st.write(df_with_previous.dropna(subset=['recommend_1']))

    st.header("📈 New Courses")
    st.info("👉 Scroll right for course url on my.harvard.edu")
    df_new_professors = df_with_previous[df_with_previous['recommend_1'].isna()].reset_index(drop=True)
    df_new_professors = df_new_professors.drop(columns=['recommend_1', 'accessible_1', 'n_courses'])
    st.write(df_new_professors)