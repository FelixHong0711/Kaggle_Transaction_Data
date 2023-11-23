import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import base64
import io

info_lines = [
    'Data Period: 01 January, 2023 - 14 October, 2023 <br>',
    'Data Source: [Kaggle - Customer Transaction](https://www.kaggle.com/datasets/bkcoban/customer-transactions/data) <br>',
    'Author: Huu Phuc (Felix) Hong <br>',
    'Last Update: 21 November, 2023'
]
info = ''.join(info_lines)
st.markdown(info, unsafe_allow_html=True)

# Load the data
df = pd.read_csv("sample_dataset.csv")

# Preprocessing
df.replace(np.nan, "Unidentified", inplace=True)
df['Gender'] = df['Gender'].replace({'F': 'Female', 'M': 'Male'})
df.columns = df.columns.str.replace(' ', '') 
df["CustomerID"] = df["CustomerID"].astype(str)
df["Birthdate"] = pd.to_datetime(df["Birthdate"])
df["Date"] = pd.to_datetime(df["Date"])
df["Age"] = df["Date"].dt.year - df["Birthdate"].dt.year
df.drop(["Birthdate"], axis=1, inplace=True)
df["TransactionMonth"] = df["Date"].dt.strftime('%B')

# Function to categorize age into groups
def categorize_age(age):
    if age >= 18 and age <= 35:
        return "18-35"
    elif age > 35 and age <= 60:
        return "35-60"
    else:
        return "60+"

df['AgeGroup'] = df['Age'].apply(categorize_age)

# Fetch unique values for each filter option
gender_options = df['Gender'].unique().tolist()
category_options = df['Category'].unique().tolist()
age_group_options = df['AgeGroup'].unique().tolist()
month_options = df['TransactionMonth'].unique().tolist()

# Create checkbox filters in the sidebar
st.sidebar.header('Filters')

gender_filter = st.sidebar.checkbox('All Genders', value=True)
if not gender_filter:
    selected_genders = st.sidebar.multiselect('Select Gender', gender_options)
    if selected_genders:
        df = df[df['Gender'].isin(selected_genders)]

category_filter = st.sidebar.checkbox('All Categories', value=True)
if not category_filter:
    selected_categories = st.sidebar.multiselect('Select Category', category_options)
    if selected_categories:
        df = df[df['Category'].isin(selected_categories)]

age_filter = st.sidebar.checkbox('All Age Groups', value=True)
if not age_filter:
    selected_age_groups = st.sidebar.multiselect('Select Age Group', age_group_options)
    if selected_age_groups:
        df = df[df['AgeGroup'].isin(selected_age_groups)]

month_filter = st.sidebar.checkbox('All Months', value=True)
if not month_filter:
    selected_months = st.sidebar.multiselect('Select Transaction Month', month_options)
    if selected_months:
        df = df[df['TransactionMonth'].isin(selected_months)]

st.title('Summary')

# Calculate the statistics
num_customers = df['CustomerID'].nunique()
num_merchants = df['MerchantName'].nunique()
num_categories = df['Category'].nunique()
total_transaction_amount = df['TransactionAmount'].sum()
average_transaction_amount = df['TransactionAmount'].mean()

# Create a summary table with commas as separators
summary_table_overall = pd.DataFrame({
    'Summary': ['Number of Customers', 'Number of Merchants', 'Number of Categories', 'Total Transaction Amount', 'Average Transaction Amount Per Person'],
    'Value': [f'{num_customers:,.0f}', f'{num_merchants:,.0f}', f'{num_categories:,.0f}', f'{total_transaction_amount:,.0f}', f'{average_transaction_amount:,.0f}']
})

# Display the summary table
st.write(summary_table_overall)

# Group the data by 'Gender' and calculate summary statistics
gender_groups = df.groupby('Gender')

summary_table = gender_groups.agg(
    Number_of_Customers=('CustomerID', 'nunique'),
    Number_of_Merchants=('MerchantName', 'nunique'),
    Number_of_Categories=('Category', 'nunique'),
    Total_Transaction_Amount=('TransactionAmount', 'sum'),
    Average_Transaction_Amount_Per_Customer=('TransactionAmount', 'mean')
)

# Format the summary table to include commas as separators
summary_table['Number_of_Customers'] = summary_table['Number_of_Customers'].apply('{:,.0f}'.format)
summary_table['Number_of_Merchants'] = summary_table['Number_of_Merchants'].apply('{:,.0f}'.format)
summary_table['Number_of_Categories'] = summary_table['Number_of_Categories'].apply('{:,.0f}'.format)
summary_table['Total_Transaction_Amount'] = summary_table['Total_Transaction_Amount'].apply('{:,.0f}'.format)
summary_table['Average_Transaction_Amount_Per_Customer'] = summary_table['Average_Transaction_Amount_Per_Customer'].apply('{:,.0f}'.format)

# Rename the columns
summary_table_gender = summary_table.rename(columns=lambda x: x.replace('_', ' '))

# Group the data by 'AgeGroup' and calculate summary statistics
age_groups = df.groupby('AgeGroup')

summary_table = age_groups.agg(
    Number_of_Customers=('CustomerID', 'nunique'),
    Number_of_Merchants=('MerchantName', 'nunique'),
    Number_of_Categories=('Category', 'nunique'),
    Total_Transaction_Amount=('TransactionAmount', 'sum'),
    Average_Transaction_Amount_Per_Customer=('TransactionAmount', 'mean')
)

# Format the summary table to include commas as separators
summary_table['Number_of_Customers'] = summary_table['Number_of_Customers'].apply('{:,.0f}'.format)
summary_table['Number_of_Merchants'] = summary_table['Number_of_Merchants'].apply('{:,.0f}'.format)
summary_table['Number_of_Categories'] = summary_table['Number_of_Categories'].apply('{:,.0f}'.format)
summary_table['Total_Transaction_Amount'] = summary_table['Total_Transaction_Amount'].apply('{:,.0f}'.format)
summary_table['Average_Transaction_Amount_Per_Customer'] = summary_table['Average_Transaction_Amount_Per_Customer'].apply('{:,.0f}'.format)

# Rename the columns
summary_table_age_group = summary_table.rename(columns=lambda x: x.replace('_', ' '))

# Group the data by 'TransactionMonth' and other cols for downloading
transaction_amount_month_gender = df.groupby(['TransactionMonth', 'Gender'])['TransactionAmount'].sum().reset_index()
transaction_amount_gender_category = df.groupby(['Gender', 'Category'])['TransactionAmount'].sum().reset_index()
transaction_amount_age_category = df.groupby(['AgeGroup', 'Category'])['TransactionAmount'].sum().reset_index()

# Transaction Analysis
st.title('Transaction Analysis')

st.subheader('By Gender')

# Compute statistics for displaying
gender_groups = df.groupby('Gender')['TransactionAmount'].sum().divide(10**6).round(2)
mean_transaction_amount = gender_groups.mean()

# Create a bar chart using Plotly Express
fig1 = px.bar(gender_groups, x=gender_groups.index, y='TransactionAmount', title='Total Transaction Amount')
fig1.update_xaxes(title_text='Gender')
fig1.update_yaxes(title_text='Total Transaction Amount (million $)')
fig1.update_traces(
    hovertemplate='<b>%{x}</b><br>' +
                  'Transaction Amount: $%{y:.2f}M<br>'
)
fig1.update_traces(marker_color='darkred')

# Add a horizontal line for the mean value
fig1.add_shape(
    type='line',
    x0=-1,
    x1=len(gender_groups),
    y0=mean_transaction_amount,
    y1=mean_transaction_amount,
    line=dict(color='gray', dash='dash')
)

fig1.add_annotation(
    x=-0.8,
    y=mean_transaction_amount + mean_transaction_amount/20,
    text="Mean",
    showarrow=False,
)

mean_gender_groups = df.groupby('Gender')['TransactionAmount'].mean().round(2)

# Create a bar chart using Plotly Express
fig2 = px.bar(mean_gender_groups, x=mean_gender_groups.index, y='TransactionAmount', title='Average Transaction Amount')
fig2.update_xaxes(title_text='Gender')
fig2.update_yaxes(title_text='Average Transaction Amount ($)')
fig2.update_traces(
    hovertemplate='<b>%{x}</b><br>' +
                  'Avg Transaction Amount Per Person: $%{y:.2f}<br>'
)
fig2.update_traces(marker_color='darkred')

# Display the charts in the same row
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig1, use_container_width=True)
with col2:
    st.plotly_chart(fig2, use_container_width=True)


st.subheader('By Age Group')
# Compute statistics for displaying
age_groups = df.groupby('AgeGroup')['TransactionAmount'].sum().divide(10**6).round(2)

# Calculate the mean of the TransactionAmount
mean_transaction_amount = age_groups.mean()

# Create a bar chart using Plotly Express
fig3 = px.bar(age_groups, x=age_groups.index, y='TransactionAmount', title='Total Transaction Amount')
fig3.update_xaxes(title_text='Age Group')
fig3.update_yaxes(title_text='Total Transaction Amount (million $)')
fig3.update_traces(
    hovertemplate='<b>%{x}</b><br>' +
                  'Transaction Amount: $%{y:.2f}M<br>'
)
fig3.update_traces(marker_color='darkred')

# Add a horizontal line for the mean value
fig3.add_shape(
    type='line',
    x0=-1,
    x1=len(age_groups),
    y0=mean_transaction_amount,
    y1=mean_transaction_amount,
    line=dict(color='gray', dash='dash'),
    name='Mean Transaction Amount'
)

fig3.add_annotation(
    x=-0.8,
    y=mean_transaction_amount + mean_transaction_amount/20,
    text="Mean",
    showarrow=False,
)

mean_age_groups = df.groupby('AgeGroup')['TransactionAmount'].mean().round(2)

# Create a bar chart using Plotly Express
fig4 = px.bar(mean_age_groups, x=mean_age_groups.index, y='TransactionAmount', title='Average Transaction Amount')
fig4.update_xaxes(title_text='Age Group')
fig4.update_yaxes(title_text='Average Transaction Amount ($)')
fig4.update_traces(
    hovertemplate='<b>%{x}</b><br>' +
                  'Avg Transaction Amount Per Person: $%{y:.2f}<br>'
)
fig4.update_traces(marker_color='darkred')

# Display the charts in the same row
col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(fig3, use_container_width=True)
with col4:
    st.plotly_chart(fig4, use_container_width=True)

st.subheader("By Merchant")
# Compute statistics for displaying
merchant_groups = df.groupby('MerchantName')['TransactionAmount'].sum().divide(10**3).round(2).nlargest(20)
mean_transaction_amount = merchant_groups.mean()

# Create a bar chart using Plotly Express
fig5 = px.bar(merchant_groups, x=merchant_groups.index, y='TransactionAmount', title='Top 20 Merchants with highest Transaction Amount')
fig5.update_xaxes(title_text='Merchant Name')
fig5.update_yaxes(title_text='Total Transaction Amount (thousand $)')

fig5.update_traces(
    hovertemplate='<b>%{x}</b><br>' +
                  'Transaction Amount: $%{y:.2f} thousands<br>'
)
fig5.update_traces(marker_color='darkred')

# Add a horizontal line for the mean value
fig5.add_shape(
    type='line',
    x0=-1,
    x1=len(merchant_groups),
    y0=mean_transaction_amount,
    y1=mean_transaction_amount,
    line=dict(color='gray', dash='dash'),
    name='Mean Transaction Amount'
)
fig5.add_annotation(
    x=-0.9,
    y=mean_transaction_amount + mean_transaction_amount/20,
    text="Mean",
    showarrow=False,
)

st.plotly_chart(fig5)

st.subheader('By Category')
# Compute statistics for displaying
category_groups = df.groupby('Category')['TransactionAmount'].sum().divide(10**6).round(2).sort_values(ascending=False)
mean_transaction_amount = category_groups.mean()

# Create a bar chart using Plotly Express
fig6 = px.bar(category_groups, x=category_groups.index, y='TransactionAmount', title='Total Transaction Amount')
fig6.update_xaxes(title_text='Category')
fig6.update_yaxes(title_text='Total Transaction Amount (million $)')

fig6.update_traces(
    hovertemplate='<b>%{x}</b><br>' +
                  'Transaction Amount: $%{y:.2f}M<br>'
)

fig6.update_traces(marker_color='darkred')
# Add a horizontal line for the mean value
fig6.add_shape(
    type='line',
    x0=-1,
    x1=len(category_groups),
    y0=mean_transaction_amount,
    y1=mean_transaction_amount,
    line=dict(color='gray', dash='dash'),
    name='Mean Transaction Amount'
)

fig6.add_annotation(
    x=-0.8,
    y=mean_transaction_amount + mean_transaction_amount/10,
    text='Mean',
    showarrow=False
)

st.plotly_chart(fig6)

st.subheader('By Transaction Month')
# Define the correct order of months
month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October"]

# Convert the 'TransactionMonth' column to a categorical data type with the specified order
df['TransactionMonth'] = pd.Categorical(df['TransactionMonth'], categories=month_order, ordered=True)

# Compute statistics for displaying
monthly_totals = df.groupby('TransactionMonth')['TransactionAmount'].sum().divide(10**6).round(2).reset_index()

# Create line chart using Plotly express
fig7 = px.line(monthly_totals, x='TransactionMonth', y='TransactionAmount')

fig7.update_layout(
    xaxis_title='Transaction Month',
    yaxis_title='Transaction Amount (million $)',
    title='Monthly Transaction Amount (2023)'
)

fig7.update_traces(
    hovertemplate='<b>%{x}</b><br>' +
                  'Transaction Amount: $%{y:.2f}M<br>'
)

fig7.update_traces(line=dict(color='darkred'))

st.plotly_chart(fig7)

# Download summary button
# Function for creating the download link
def get_binary_file_downloader_html(bin_data, file_label='File'):
    b64 = base64.b64encode(bin_data).decode()
    custom_css = """ 
        <style>
            .download-link {
                color: white;
                text-decoration: none;
                display: inline-block;
            }
            .download-link:hover {
                background-color: #ff4d7a;
            }
        </style>
    """
    html = custom_css + f'<a href="data:file/csv;base64,{b64}" download="{file_label}.csv" class="download-link">{file_label}</a>'
    return html

# Create StringIO object to store CSV file in memory
csv_file = io.StringIO()

# Write DataFrames to the StringIO object in CSV format
summary_table_overall.to_csv(csv_file, index=False, lineterminator='\n')
summary_table_gender.to_csv(csv_file, index=False, lineterminator='\n')
summary_table_age_group.to_csv(csv_file, index=False, lineterminator='\n')
transaction_amount_gender_category.to_csv(csv_file, index=False, lineterminator='\n')
transaction_amount_month_gender.to_csv(csv_file, index=False, lineterminator='\n')
transaction_amount_age_category.to_csv(csv_file, index=False, lineterminator='\n')

# Convert StringIO object to binary data
csv_binary = csv_file.getvalue().encode()

# Display download link
if st.sidebar.button('Download Summary Data'):
    st.sidebar.markdown(get_binary_file_downloader_html(csv_binary, 'summary_data'), unsafe_allow_html=True)
