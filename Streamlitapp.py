
import streamlit as st
import pandas as pd
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt
from PIL import Image
import mysql.connector as db
import pymysql

st.set_page_config(
    page_title="PhonePe Pulse Data Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_data(query, params=None):
    conn = pymysql.connect(host='localhost', user='raja', passwd='raja',database="phonepe")
    if params:
        df = pd.read_sql_query(query, conn, params=params)
    else:
        df = pd.read_sql_query(query, conn)
    conn.close()
    return df


image = Image.open("C:/Users/rajar/project phone pay/logo (1).jpg")

resized_image = image.resize((400, 400))  # Resize to 200x200 pixels

#Create a layout with columns (left-aligned)
col1, col2 = st.columns([1, 7])  # Smaller left column

with col1:
    st.image(resized_image)
with col2:
    st.title('PhonePe Transaction Insights')

r = st.sidebar.radio('Navigation',["Home Page","Business Case Study"],index=0)

if r == "Home Page":
    st.subheader("**A Streamlit App for Exploring Phonepe Transaction & User Trends**")
    st.write(""" With the increasing reliance on digital payment systems like PhonePe, understanding the dynamics of transactions and user engagement
             is crucial for improving services and targeting users effectively. 
             This project aims to analyze and visualize aggregated values of payment categories, 
             create maps for total values at state and district levels, and identify top-performing states, districts, and pin codes.

    **Database Used:** `Phonepe`
    """)

    col1,col2 = st.sidebar.columns(2,gap="small")
    with col1:
        category = ["Transaction","User"]
        cat_select = st.sidebar.selectbox("Select",category)
    

    if cat_select == "Transaction":

        with col2:
            q = "select DISTINCT concat(Year,'_Q', Quarter) as Year_Qtr from agg_trans;"
            df = get_data(q)
            yq_select = st.sidebar.selectbox("Yr",df)
 
        q = """select sum(Transaction_count) as 'Total Transactions',sum(Transaction_amount) as 'Total Revenue'
            from agg_trans where concat(Year,'_Q', Quarter) = %s
            group by state
            order by 2 DESC limit 1;"""
        df = get_data(q, params=(yq_select,))
        total_transactions = df['Total Transactions']
        total_revenue = df['Total Revenue']


        col1, col2 = st.columns(2,gap = "small")
        with col1:
            st.metric('Total Transactions',value=total_transactions)
        with col2:
            st.metric('Total Revenue (₹)',value=total_revenue)
# map
        q_map = """
            SELECT State, 
                SUM(Transaction_count) AS `Transactions`, 
                SUM(Transaction_amount) AS `Revenue`
            FROM agg_trans
            WHERE CONCAT(Year,'_Q', Quarter) = %s
            GROUP BY State
            """
        df_map = get_data(q_map, params=(yq_select,))

        df_map['State'] = df_map['State'].replace({
            'andaman-&-nicobar-islands': 'Andaman & Nicobar','andhra-pradesh': 'Andhra Pradesh','arunachal-pradesh': 'Arunachal Pradesh',
            'assam': 'Assam','bihar': 'Bihar','chandigarh': 'Chandigarh','chhattisgarh': 'Chhattisgarh','dadra-&-nagar-haveli-&-daman-&-diu': 'Dadra and Nagar Haveli and Daman and Diu',
            'delhi': 'Delhi','goa': 'Goa','gujarat': 'Gujarat','haryana': 'Haryana','himachal-pradesh': 'Himachal Pradesh',
            'jammu-&-kashmir': 'Jammu & Kashmir','jharkhand': 'Jharkhand','karnataka': 'Karnataka','kerala': 'Kerala','ladakh': 'Ladakh',
            'madhya-pradesh': 'Madhya Pradesh','maharashtra': 'Maharashtra','manipur': 'Manipur','meghalaya': 'Meghalaya','mizoram': 'Mizoram',
            'nagaland': 'Nagaland','odisha': 'Odisha','puducherry': 'Puducherry','punjab': 'Punjab','rajasthan': 'Rajasthan','sikkim': 'Sikkim',
            'tamil-nadu': 'Tamil Nadu','telangana': 'Telangana','tripura': 'Tripura','uttar-pradesh': 'Uttarakhand','uttarakhand': 'Uttar Pradesh',
            'west-bengal': 'West Bengal'
            })

        import requests
        geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        india_states = requests.get(geojson_url).json()

        # Plot the map using df_map (✅ correct one)
        fig = px.choropleth(
            df_map,
            geojson=india_states,
            featureidkey='properties.ST_NM',
            locations='State',
            color='Transactions',
            hover_name='State',
            hover_data={'Revenue': True},
            color_continuous_scale='Reds',
        )

        fig.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig, use_container_width=True)
# user
    if cat_select == "User":

        with col2:
            q = "select DISTINCT concat(Year,'_Q', Quarter) as Year_Qtr from map_user;"
            df = get_data(q)
            yq_select = st.sidebar.selectbox("Yr",df)

        q = """select sum(Registered_Users) as 'Registered Users', sum(App_Opens) as 'App Opens'
            from map_user where concat(Year,'_Q', Quarter) = %s
            group by state
            order by 2 DESC limit 1;"""
        df = get_data(q, params=(yq_select,))
        Registered_Users = df['Registered Users']
        App_Opens = df['App Opens']

        col1, col2 = st.columns(2,gap = "small")
        with col1:
            st.metric('Total Registered Users',value=Registered_Users)
        with col2:
            st.metric('Total App Opens', value=App_Opens)

    # map

        q_map = """
        SELECT State, 
        SUM(Registered_Users) AS `Registered Users`, 
        SUM(App_Opens) AS `App Opens`
        FROM map_user
        WHERE CONCAT(Year,'_Q', Quarter) = %s
        GROUP BY State
        """
        df_map = get_data(q_map, params=(yq_select,))
        
        df_map['State'] = df_map['State'].replace({
            'andaman-&-nicobar-islands': 'Andaman & Nicobar','andhra-pradesh': 'Andhra Pradesh','arunachal-pradesh': 'Arunachal Pradesh',
            'assam': 'Assam','bihar': 'Bihar','chandigarh': 'Chandigarh','chhattisgarh': 'Chhattisgarh','dadra-&-nagar-haveli-&-daman-&-diu': 'Dadra and Nagar Haveli and Daman and Diu',
            'delhi': 'Delhi','goa': 'Goa','gujarat': 'Gujarat','haryana': 'Haryana','himachal-pradesh': 'Himachal Pradesh',
            'jammu-&-kashmir': 'Jammu & Kashmir','jharkhand': 'Jharkhand','karnataka': 'Karnataka','kerala': 'Kerala','ladakh': 'Ladakh',
            'madhya-pradesh': 'Madhya Pradesh','maharashtra': 'Maharashtra','manipur': 'Manipur','meghalaya': 'Meghalaya','mizoram': 'Mizoram',
            'nagaland': 'Nagaland','odisha': 'Odisha','puducherry': 'Puducherry','punjab': 'Punjab','rajasthan': 'Rajasthan','sikkim': 'Sikkim',
            'tamil-nadu': 'Tamil Nadu','telangana': 'Telangana','tripura': 'Tripura','uttar-pradesh': 'Uttarakhand','uttarakhand': 'Uttar Pradesh',
            'west-bengal': 'West Bengal'
            })

        import requests
        geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        india_states = requests.get(geojson_url).json()

        # Plot the map using df_map (✅ correct one)
        fig = px.choropleth(
            df_map,
            geojson=india_states,
            featureidkey='properties.ST_NM',
            locations='State',
            color='Registered Users',
            hover_name='State',
            hover_data={'App Opens': True},
            color_continuous_scale='Reds',
        )

        fig.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig, use_container_width=True)



else:
    case_studies = ["Decoding Transaction Dynamics on PhonePe",
                    "User Engagement and Growth Strategy",                    
                    "Transaction Analysis Across States and Districts",
                    "User Registration Analysis",
                    "Insurance Transactions Analysis"]

    case_select = st.sidebar.selectbox("Select Business Case Study: ",case_studies)

#Decoding Transaction Dynamics on PhonePe

    if case_select == case_studies[0]:

        
        st.subheader("Decoding Transaction Dynamics on PhonePe")
        st.write(''' This dashboard explores how PhonePe transactions vary across states, quarters, and categories. 
                 It highlights trends like growth, stagnation, or decline in different regions and use cases. 
                 These insights help guide strategic decisions and targeted improvements.
        ''')
        category = ["State-wise Transaction Trends","Most Popular Payment Category","Top 10 States by Total Transaction Value","Payment Category-wise Trends"]            
        q_select = st.multiselect("Select", category)
        
#Insight 1
        if "State-wise Transaction Trends" in q_select:
            st.subheader("State-wise Transaction Trends")
            q = """
            SELECT 
                state,
                SUM(transaction_count) AS Total_transactions,
                sum(transaction_amount) as Total_transaction_value
            FROM agg_trans
            GROUP BY state
            ORDER BY Total_transactions desc; 
            """
            df = get_data(q)
            st.bar_chart(df.set_index('state')['Total_transactions'])
            st.dataframe(df) 
            
#Insight 2
        if "Top 10 States by Total Transaction Value" in q_select:
            st.subheader("Top 10 States by Total Transaction Value")
            q = """select State, sum(Transaction_amount) as 'Total_Transaction_Value'
            from agg_trans
            group by State
            order by Total_Transaction_Value DESC limit 10;"""
            df = get_data(q)
            fig = px.bar(
                data_frame=df,
                x='State',
                y='Total_Transaction_Value',
                labels='Total_Transaction_Value',
                color='State'
            )

            st.plotly_chart(fig, use_container_width=True)

#Insight 3
        if "Most Popular Payment Category" in q_select:
            st.subheader("Most Popular Payment Category")
            col1,col2 = st.columns(2,gap="small")
            q = "select Transaction_type, sum(Transaction_count) as 'Total Number of Transactions', sum(Transaction_amount) as 'Total Transaction Value' from agg_trans group by Transaction_type"
            df = get_data(q)
            
            with col1:
                fig1 = px.pie(df,
                        names='Transaction_type',
                        values='Total Number of Transactions',
                        title="Distribution of Transaction value",
                        hole=0.4,
                        labels=['Transaction_type','Total Number of Transactions'])
                st.plotly_chart(fig1)  
            with col2:
                fig2 = px.pie(df,
                        names='Transaction_type',
                        values='Total Transaction Value',
                        title="Distribution of Transaction Volume",
                        hole=0.4,
                        labels=['Transaction_type','Total Transaction Value'])
                st.plotly_chart(fig2)  

#Insight 4
        if "Payment Category-wise Trends" in q_select:
            st.subheader("Payment Category-wise Trends")
            q = """
                SELECT Transaction_Type, SUM(transaction_count) AS Total_transactions, SUM(transaction_amount) AS Total_transaction_value, ROUND(SUM(transaction_amount) / SUM(transaction_count), 2) AS Avg_transaction_value
                FROM agg_trans
                GROUP BY Transaction_Type
                ORDER BY Avg_transaction_value desc;
            """
            df = get_data(q)
            
            # Create matplotlib pie chart
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # Generate pie chart
            ax.pie(df['Total_transactions'],
                labels=df['Transaction_Type'],
                autopct='%1.1f%%',
                startangle=90,
                textprops={'fontsize': 10})
            
            ax.set_title('Transaction Distribution by Payment Category', pad=20)
            ax.axis('equal')  # Ensures pie is drawn as a circle
            
            # Display in Streamlit
            st.pyplot(fig)
            
            # Show the data table below
            st.dataframe(df)

# User Engagement and Growth Strategy
    if case_select == case_studies[1]:

        
        st.subheader("User Engagement and Growth Strategy")
        st.write(''' This analysis explores how users engage with PhonePe across different states and districts.
                By examining metrics like app opens and user registrations, we uncover usage patterns.
                These insights help guide strategic growth and regional focus.
                ''')
        category = ["Total Registered Users And App Opens by Year","Total Registered Users And App Opens by State","Bottom 10 Registered User By State"]
        q_select = st.multiselect("Select", category)
#Insight 1
        if "Total Registered Users And App Opens by Year" in q_select:
            st.subheader("Total Registered Users And App Opens by Year")
            q= """
            SELECT 
                Year, SUM(Registered_Users) AS Total_registered, SUM(App_Opens) AS Total_app_opens
            FROM map_user
            GROUP BY Year
            ORDER BY Total_registered desc;
            """

            col1,col2 = st.columns(2,gap= 'small')
            with col1:
                df=get_data(q)
                fig = px.line(df,
                            x='Year',
                            y=['Total_registered'],
                            labels={
                                'value': 'Count',
                                'variable': 'Metric',
                                'Year': 'Year'
                            },
                            title='User Growth and Engagement Over Time')
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                df=get_data(q)
                fig = px.line(df,
                            x='Year',
                            y=['Total_app_opens'],
                            labels={
                                'value': 'Count',
                                'variable': 'Metric',
                                'Year': 'Year'
                            },
                            title='App Opens Growth and Engagement Over Time')
                
                st.plotly_chart(fig, use_container_width=True)
#Insight 2
        if "Total Registered Users And App Opens by State" in q_select:
            st.subheader("Total Registered Users And App Opens by State")
            q = """
            SELECT 
                state, SUM(Registered_Users) AS Total_registered, SUM(App_Opens) AS Total_app_opens
            FROM map_user GROUP BY state
            ORDER BY Total_registered desc;
            """
            df = get_data(q)
            st.bar_chart(df,x="state",y= "Total_registered")
            st.dataframe(df)
# Insight 3
        if "Bottom 10 Registered User By State" in q_select:
            st.subheader("Bottom 10 Registered User By State")
            q = """
            SELECT 
                state, SUM(Registered_Users) AS Total_registered, SUM(App_Opens) AS Total_app_opens
            FROM map_user GROUP BY state
            ORDER BY Total_registered asc limit 10;"""
            df= get_data(q)
            fig = px.bar(

                data_frame=df,
                x='state',
                y='Total_registered',
                labels='Total_registered',
                color='Total_registered'
            )

            st.plotly_chart(fig, use_container_width=True)

# Transaction Analysis Across States and Districts
    if case_select == case_studies[2]:
        st.subheader("Transaction Analysis Across States and Districts")
        st.write('''PhonePe's transaction data highlights top states, districts, and pin codes by volume and value. 
                 These insights reveal high-engagement areas, shaping targeted marketing strategies. 
                 Explore trends and hotspots in the visualizations below!
        ''')
        category = ["Top 10 States Wise Transaction Value & Count","Top 10 District Wise Transaction Value & Count","Bottom 10 States wise Transaction Value & Count"]
        q_select = st.multiselect("Select", category)
#Insight 1
        if "Top 10 States Wise Transaction Value & Count" in q_select:
            st.subheader("Top 10 States Wise Transaction Value & Count")
            q = """
            SELECT 
                state,
                SUM(transaction_count) AS Total_transactions,
                sum(transaction_amount) as Total_transaction_value
            FROM top_trans
            GROUP BY state
            ORDER BY Total_transaction_value desc
            limit 10;
            """
            df = get_data(q)
            sns.set_style("darkgrid")
            plt.figure(figsize = (20,6))
            sns.barplot( x = df.state, y = df.Total_transaction_value, palette = "coolwarm")
            st.pyplot(plt.gcf())
            st.dataframe(df)
#Insight 2        
        if "Top 10 District Wise Transaction Value & Count" in q_select:
            st.subheader("Top 10 District Wise Transaction Value")
            q = """
            SELECT 
                Entity_Name as District, SUM(transaction_count) AS Total_transactions, sum(transaction_amount) as Total_transaction_value
            FROM top_trans where level = 'District' GROUP BY District
            ORDER BY Total_transaction_value desc
            limit 10;
            """
            df = get_data(q)
            fig = px.bar(df,
                x= "District",
                y= "Total_transaction_value",
                title= "Top 10 District",
                labels= "District"
            )
            st.plotly_chart(fig, use_container_width= False)
#Insight 3
        if "Bottom 10 States wise Transaction Value & Count" in q_select:
            st.subheader("Bottom 10 States wise Transaction Value & Count")
            q = """
            SELECT 
                state, SUM(transaction_count) AS Total_transactions_count, sum(transaction_amount) as Total_transaction_value
            FROM top_trans GROUP BY state
            ORDER BY Total_transaction_value asc
            limit 10;"""
            df=get_data(q)
            col1,col2 = st.columns(2, gap= "small")
            with col1:
                fig1= px.bar(df,
                    x= "state",
                    y= "Total_transaction_value",
                    labels= "Total_transaction_value",
                    color="state",
                    title= "Bottom 10 States Transaction Value"
                    )
                st.plotly_chart(fig1, use_container_width=True)
            with col2:
                fig2= px.bar(df,
                    x= "state",
                    y= "Total_transaction_value",
                    labels= "Total_transactions_count",
                    color="state",
                    title= "Bottom 10 States Transaction Count"
                    )
                st.plotly_chart(fig2, use_container_width=True)

# User Registration Analysis

    if case_select == case_studies[3]:

        
        st.subheader("User Registration Analysis")
        st.write('''PhonePe analyzes user registrations to identify top states, districts, and pin codes for any quarter. 
                 These insights reveal high-growth regions and engagement trends. 
                 Explore the data to uncover key opportunities for expansion!
        ''')
        category = ["Top States by Registered Users","Top Districts by Registered Users","Bottom 10 States By Registered Users"]
        q_select = st.multiselect("Select", category)
#Insight 1
        if "Top States by Registered Users" in q_select:
            st.subheader("Top States By Registered Users")
            q = """
            SELECT 
                state,
                SUM(RegisteredUsers) AS Total_Registered_Users
            FROM top_user
            GROUP BY state
            ORDER BY Total_Registered_Users desc limit 10;"""
            df = get_data(q)
            fig= px.bar(df,
                x= "state",
                y= "Total_Registered_Users",
                labels={
                    "Total_Registered_Users": "Registered Users", 
                    "state": "State"
                },
                color="state",
                title= "Top 10 States Registered Users"
                )
            st.plotly_chart(fig, use_container_width=True)
            st.write("Raw Data:", df)
#Insight 2
        if "Top Districts by Registered Users" in q_select:
            st.subheader("Top Districts by Registered Users")
            q = """
            SELECT 
                state,Entity_Name as district,SUM(RegisteredUsers) AS Total_Registered_Users
            FROM top_user
            where level = 'District'
            GROUP BY state, district
            ORDER BY Total_Registered_Users desc
            limit 30;"""
            df = get_data(q)
            st.bar_chart(df.set_index('district')['Total_Registered_Users'])

#Insight 3
        if "Bottom 10 States By Registered Users" in q_select:
            st.subheader("Bottom 10 States By Registered Users")
            q = """
            SELECT 
                state, SUM(RegisteredUsers) AS Total_Registered_Users
            FROM top_user GROUP BY state
            ORDER BY Total_Registered_Users asc
            limit 10;"""
            df = get_data(q)
                # Create dot plot
            fig = px.scatter(
                df,
                x="Total_Registered_Users",
                y="state",
                size="Total_Registered_Users",
                color="Total_Registered_Users",
                color_continuous_scale="reds",
                title="Bottom 10 States (Registered Users)",
                labels={
                    "Total_Registered_Users": "Registered Users",
                    "state": "State"
                },
                hover_data={"Total_Registered_Users": ":,"},
                size_max=30  # Controls maximum dot size
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)

# Insurance Transactions Analysis

    if case_select == case_studies[4]:

        
        st.subheader("Insurance Transactions Analysis")
        st.write('''PhonePe's insurance data reveals top states, districts and pin codes by transaction volume. 
                 These insights highlight high-engagement regions in the insurance sector. 
                 Explore the trends to identify growth opportunities and optimize strategies.
        ''')
        category = ["Top States For Insurance Transactions","Top 20 Districts For Insurance Transactions","Top 10 Pin Codes For Insurance Transactions"]
        q_select = st.multiselect("Select", category)

        if "Top States For Insurance Transactions" in q_select:
            st.subheader("State-wise Insurance Trends Over Years")
            q= """
            SELECT 
                state,
                year,
                SUM(Transaction_Amount) AS Total_Transaction_Amount
            FROM top_ins
            GROUP BY state, year
            ORDER BY Total_Transaction_Amount desc;"""
            df = get_data(q)
            fig = px.bar(df,
                         x="state",
                         y="Total_Transaction_Amount",
                         hover_data="year",
                         color="state"
                         )
            st.plotly_chart(fig, use_container_width=True)

        if "Top 20 Districts For Insurance Transactions" in q_select:
            st.subheader("Top 20 Districts For Insurance Transactions")
            q= """
            SELECT 
                state,
                Entity_Name as District,
                SUM(Transaction_Amount) AS Total_Transaction_Amount
            FROM top_ins
            where level = 'District'
            GROUP BY state, District
            ORDER BY Total_Transaction_Amount desc;"""
            df = get_data(q)
            fig = px.scatter(
                df,
                x="District",
                y="Total_Transaction_Amount",
                color="Total_Transaction_Amount",
                color_continuous_scale= "twilight",
                title="Top 20 District",
                labels={"Total_Transaction_Amount":"Total Transaction Amount",
                        "District":"District"
                },
                size_max=30,
                hover_data="Total_Transaction_Amount"
                )
            st.plotly_chart(fig, use_container_width=True)
            
        if "Top 10 Pin Codes For Insurance Transactions" in q_select:
            st.subheader("Top 10 Pin Codes For Insurance Transactions")
            q = """
            SELECT 
                state, Entity_Name as Pincode,
                SUM(Transaction_Count) AS Total_Transaction_Count,
                SUM(Transaction_Amount) AS Total_Transaction_Amount
            FROM top_ins
            where level = 'pincode'
            GROUP BY state, Pincode
            ORDER BY Total_Transaction_Amount asc limit 10;"""
            df = get_data(q)
            fig = px.bar(
                data_frame=df,
                x='Pincode',
                y='Total_Transaction_Count',
                labels={
                    'Total_Transaction_Count': 'Total Transaction Count',
                    'Pincode':"Pincode"
                },
                color='Total_Transaction_Count',
                text_auto=True
            )
            fig.update_layout(
                xaxis_type='category',  # Ensures pincodes stay as strings
                xaxis_title='Pincode',
                yaxis_title='Transaction Count',
                yaxis_tickformat=',',
                showlegend=False
            )
            fig.update_xaxes(categoryorder='total descending')
            st.plotly_chart(fig, use_container_width=True)