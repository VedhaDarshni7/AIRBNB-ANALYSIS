from gettext import install
from pymongo import MongoClient
from urllib.parse import quote_plus


import pandas as pd

from collections import Counter

import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import base64

import plotly.express as px
import seaborn as sb

from bson.decimal128 import Decimal128

# ========================
# MongoDB Atlas Connection
# ========================
username = "vedhadarshnisr"
password = "airbnb123"
cluster_url = "cluster0.otazxov.mongodb.net"
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)

connection = f"mongodb+srv://{encoded_username}:{encoded_password}@{cluster_url}/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(connection)
db = client.get_database("airbnb_data")
col = db["listings"]


# Data Retrieval from  MongoDB collection

datas = []
try:
    for document in col.find():
        data = {
            "Id": document.get("_id"),
            "Name": document.get("name"),
            "Description": document.get("description"),
            "Country": document.get("address", {}).get("country"),
            "Longitude": document.get("address", {}).get("location", {}).get("coordinates", [None, None])[0],
            "Latitude": document.get("address", {}).get("location", {}).get("coordinates", [None, None])[1],
            "Property_Type": document.get("property_type"),
            "Room_Type": document.get("room_type"),
            "Bed_Type": document.get("bed_type"),
            "Amentities": document.get("amenities", []),
            "Minimum_Nights": document.get("minimum_nights"),
            "Maximum_Nights": document.get("maximum_nights"),
            "Cancellation_Policy": document.get("cancellation_policy"),
            "Cleaning Fees": document.get('cleaning_fee', 0),
            "Price": document.get("price"),
            "Host_Id": document.get("host", {}).get("host_id"),
            "Host_Name": document.get("host", {}).get("host_name"),
            "Listing URL": document.get("listing_url"),
            "Availability_30": document.get("availability", {}).get("availability_30"),
            "Availability_60": document.get("availability", {}).get("availability_60"),
            "Availability_90": document.get("availability", {}).get("availability_90"),
            "Availability_365": document.get("availability", {}).get("availability_365"),
            "Number_of_Reviews": document.get("number_of_reviews"),
            "Review_Count": document.get("review_scores", {}).get("review_scores_rating", 0),
            "Review_Score": document.get("review_scores", {}).get("review_scores_value", 0)
        }
        datas.append(data)
except Exception as e:
    print("An error occurred while retrieving data from MongoDB:", e)


# DataFrame Setup

df = pd.DataFrame(datas)
df.drop_duplicates(subset=['Id'], inplace=True)
df.reset_index(drop=True, inplace=True)
df.to_csv("airbnb_cleaned.csv", index=False)



def extract_countries():
    countries=[]
    for i in col.find({},{"address.country":1}):
        countries.append(i["address"].get("country"))
        unique_countries=sorted(set(countries))
    return unique_countries



def property():
    property=[]
    for i in col.find({},{"property_type":1}):
        property.append(i["property_type"])
        unique_property=sorted(set(property))
    return unique_property



def amentities():
    s1={"$unwind":"$amenities"}
    s2={"$project":{"_id":0,"Amenity":"$amenities"}}
    result=[i["Amenity"] for i in col.aggregate([s1,s2])]
    return result



def max_nights(days,country,propertytype):
    s1={"$match":{"minimum_nights":str(days),"address.country":country,"property_type":propertytype}}
    s2={"$project":{"_id":0,"name":1,"property_type":1,"room_type":1,"price":1,"country":"$address.country","review_scores_value":{
        "$ifNull":["$review_scores.review_scores_value", "No Rating"]
    }}}
    result=[i for i in col.aggregate([s1,s2])]
    return result



def amenity_based(sel_amen,country,propertytype):
    s1={"$match":{"amenities":sel_amen,"address.country":country,"property_type":propertytype}}
    s2={"$project":{"_id":0,"name":1,"property_type":1,"room_type":1,"price":1,"country":"$address.country","review_scores_value":{
        "$ifNull":["$review_scores.review_scores_value", "No Rating"]
    }}}
    result=[i for i in col.aggregate([s1,s2])]
    return result



def room_list(country):
    rooms=[i["name"] for i in col.find({"address.country":country},{"name":1})]
    unique_rooms=sorted(set(rooms))
    return unique_rooms



def days(user_data,country,propertytype):
    s1={"$match":{"$or":[
        {"availability.availability_30":user_data},
        {"availability.availability_60":user_data},
        {"availability.availability_90":user_data},
        {"availability.availability_365":user_data}],
        "address.country":country,"property_type":propertytype}}
    s2={"$project":{"_id":0,"name":1,"property_type":1,"room_type":1,"price":1,"country":"$address.country","review_scores_value":{
        "$ifNull":["$review_scores.review_scores_value", "No Rating"]
    }}}
    result=[i for i in col.aggregate([s1,s2])]
    return result



def location(country):
    s1={"$match":{"address.country":country}}
    s2={"$group": {"_id": "$property_type", "count": {"$sum": 1},"name": {"$first": "$name"},"room_type": {"$first": "$room_type"},"price": {"$first": "$price"},
        "country": {"$first": "$address.country"},"review_scores_value": {"$first": "$review_scores.review_scores_value"}}}
    s3={"$project":{"_id":0,"name":1,"property_type":1,"room_type":1,"price":1,"country":"$address.country","review_scores_value":{
        "$ifNull":["$review_scores.review_scores_value", "No Rating"]
    }}}
    result=[i for i in col.aggregate([s1,s2,s3])]
    return result



def group_property_type(country):
    doc=col.find({"address.country":country})
    p_types=[i["property_type"] for i in doc]
    p_types_counts=Counter(p_types)
    result = [{"property_type": pt, "count": count} for pt, count in p_types_counts.items()]
    return result



def top_10_property(country):
    doc = col.find({"address.country": country})
    p_types = [i["property_type"] for i in doc]
    p_types_counts = Counter(p_types)
    top_10 = p_types_counts.most_common(10)
    result = [{"property_type": pt, "count": count} for pt, count in top_10]
    return result




def top_10_host(country):
    pipeline = [
        {"$match": {"address.country": country}},
        {"$group": {"_id": "$host.host_name", "host_listings_count": {"$sum": "$host.host_total_listings_count"}}},
        {"$sort": {"host_listings_count": -1}},
        {"$limit": 10}]
    result = list(col.aggregate(pipeline))
    return result



def price(country):
    pipeline=[
    {"$match":{"address.country": country}},
    {"$project":{"_id":0,"name":1,"price":1,"cleaning_fee":1,"security_deposit":1}},
    {"$addFields": {"Total": {"$sum": ["$price", "$cleaning_fee", "$security_deposit"]}}}]
    result = list(col.aggregate(pipeline))
    return result


#streamlit
logo=Image.open("i1.png")
st.set_page_config(page_title="Airbnb",
                   page_icon=logo,
                   layout="wide")




img = Image.open(r"/Users/ayushii/Desktop/AirBnB/Renting-out-on-Air-BnB-1080x675.jpg")
img = img.resize((350, 150))  
img.save(r"/Users/ayushii/Desktop/AirBnB/resized_i1.png")

with st.sidebar:
    st.image("i1.png") # Display i1.png directly here (ensure i1.png is in the same directory as your script)
    selected=option_menu("",
            ["Home","Property","Locations","Analysis"],
            icons=["house","building","map","filter"],
            orientation="vertical")
if selected=="Home":
    airbnb_url = "https://www.airbnb.com"
    st.markdown(f"""
        <div style="text-align: center;">
            <a href="{airbnb_url}" target="_blank" style="text-decoration: none; color: red; font-size: 2em; font-weight: bold;">
                AIRBNB DATA VISUALIZATION AND ANALYSIS 
            </a>
        </div>
    """, unsafe_allow_html=True)

    custom_css = """
        <style>

        .custom-text {
            color: white;
        }
        </style>
        """
    st.markdown(custom_css, unsafe_allow_html=True)

    airbnb_url = "https://www.airbnb.com" 

    st.markdown(f'''
                    <div class="custom-text">
                        <h5 class="custom-text">Airbnb is a global online marketplace that connects travelers with hosts offering unique accommodations. It provides a range of services including:</h5>
                        <ul>
                            <li><strong>Short-Term Rentals:</strong> Renting private homes, apartments, and rooms for vacations or business trips.</li>
                            <li><strong>Experiences:</strong> Booking local tours, activities, and classes hosted by locals.</li>
                            <li><strong>Long-Term Stays:</strong> Finding accommodations for extended stays, including monthly rentals.</li>
                            <li><strong>Unique Stays:</strong> Staying in unconventional properties like treehouses, castles, and houseboats.</li>
                            <li><strong>Luxury Rentals:</strong> Booking high-end and luxury accommodations for a premium experience.</li>
                        </ul>
                        <p>Airbnb operates through a website and mobile app that allow users to search for accommodations and experiences, book them directly, and communicate with hosts.</p>
                    </div>   
                    ''', unsafe_allow_html=True)
# Check what's coming from MongoDB
df = pd.DataFrame(list(col.find()))


# ✅ Flatten nested fields to new columns
df["Country"] = df["address"].apply(lambda x: x.get("country") if isinstance(x, dict) else None)
df["Latitude"] = df["location"].apply(lambda x: x.get("latitude") if isinstance(x, dict) else None)
df["Longitude"] = df["location"].apply(lambda x: x.get("longitude") if isinstance(x, dict) else None)

# ✅ Now build the choropleth
choropleth_data = df[["Country", "Latitude", "Longitude"]].dropna()

fig = px.scatter_geo(
    choropleth_data,
    locations="Country",
    hover_name="Country",
    locationmode='country names',
    projection="natural earth",
    title="World Wide Airbnb",
    size_max=50
)
st.plotly_chart(fig, use_container_width=True)


def get_base64_of_bin_file(bin_file):
    """Reads a binary file and returns its Base64-encoded string."""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

#background image
background_image_path = 'airbnb1.jpg'  # Path to your background image file

#Base64-encoded image
base64_image = get_base64_of_bin_file(background_image_path)

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/jpeg;base64,{base64_image}");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}
[data-testid="stAppViewContainer"]::before {{
content: "";
position: absolute;
top: 0;
left: 0;
width: 100%;
height: 100%;
background: rgba(0, 0, 0, 0.3);  /* Black overlay with 30% opacity */
z-index: 1;
}}

[data-testid="stAppViewContainer"] > * {{
    position: relative;
    z-index: 2;
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)



if selected=="Property":
    st.subheader("Property Search: Amenities, Availability and Features")
    col1,col2,col3,col4=st.columns(4)
    with col4:
        on=st.toggle("Amenities")
    if on:
        with col1:
            amenities=st.radio("Choose Your Amenities",["Wifi","Pets Allowed","Family/kid friendly","Hot water","Pool",
                                    "Hot tub","TV","Laptop friendly workspace","BBQ grill","Air conditioning","Kitchen","Gym"])

        with col2:
            countries_list=extract_countries()
            selected_country=st.selectbox("Select a Country",countries_list)

        with col3:
            property_list=property()
            selected_property=st.selectbox("Select a Property Type",property_list)

        amentities_data=amenity_based(amenities,selected_country,selected_property)
        amentities_data_df=pd.DataFrame(amentities_data) 
        st.dataframe(amentities_data_df)  

    else:
        col1,col2,col3,col4=st.columns(4)     
        with col1:
            l1=st.selectbox("Features",["Number of Nights","Availability of Days","Amenities"])

        if l1=="Number of Nights":
            with col1:
                n_nights=st.slider("Number of Nights",min_value=1,max_value=50)

            with col2:
                countries_list=extract_countries()
                selected_country=st.selectbox("Select a Country",countries_list)

            with col3:
                property_list=property()
                selected_property=st.selectbox("Select a Property Type",property_list)

            night_data=max_nights(n_nights,selected_country,selected_property)
            night_data_df=pd.DataFrame(night_data)    
            st.dataframe(night_data_df)        

        if l1=="Availability of Days":     
            with col1:
                day_count=st.selectbox("Number of days",["30","60","90","365"])

            with col2:
                countries_list=extract_countries()
                selected_country=st.selectbox("Select a Country",countries_list)

            with col3:
                property_list=property()
                selected_property=st.selectbox("Select a Property Type",property_list)

            day_count_int=int(day_count)
            days_data=days(day_count,selected_country,selected_property)
            days_data_df=pd.DataFrame(days_data)
            if not days_data_df.empty:
                st.dataframe(days_data_df)
            else:
                st.error("No results found")
                st.warning("Please modify criteria and search again.")
    

    
elif selected=="Locations":
    st.subheader("Property Types by Country")
    col1,_=st.columns(2)
    with col1:
        countries_list=extract_countries()
        selected_country=st.selectbox("Select a Country",countries_list)

        property_type=property()
        property_types=group_property_type(selected_country)

        if property_types:
            df2=pd.DataFrame(property_types)
            df2.columns=["Property Type","Count"]
            fig=px.bar(df2,title="Properties in each countries",x="Property Type",y="Count",color="Property Type", 
                 color_discrete_sequence=px.colors.qualitative.Plotly)
            st.plotly_chart(fig)
        else:
            st.warning("No Data Available")


    if st.button("Total Airbnb Listing"):
        room_type_counts = df['room_type'].value_counts().reset_index()
        room_type_counts.columns = ['Room Type', 'Total Listings']

        fig = px.pie(room_type_counts, values='Total Listings', names='Room Type', title='Total Airbnb Listings in Each Room Type')
        st.plotly_chart(fig)

    

elif selected=="Analysis":
    l2=st.selectbox("Features",["Top 10 Properties","Host Analysis","Price Analysis"])
    if l2=="Top 10 Properties":
        col1,col2=st.columns(2)
        with col1:
            countries_list=extract_countries()
            selected_country=st.selectbox("Select a Country",countries_list)

        with col2:
            st.write("")
        if selected_country:
            property_types=top_10_property(selected_country)
            if property_types:
                df3=pd.DataFrame(property_types)
                df3.columns=["Property Type","Count"]
                fig=px.bar(df3,title="Top 10 Properties",x="Property Type",y="Count",color="Property Type",color_discrete_sequence=px.colors.qualitative.Plotly)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No Data Available")



    if l2 == "Host Analysis":
        col1, col2, col3 = st.columns(3)
        df = pd.DataFrame(list(col.find({}, {"host.host_name": 1}))) 
        with col1:
            countries_list = extract_countries()
            selected_country = st.selectbox("Select a country", countries_list)

        if selected_country:
            host_analysis = top_10_host(selected_country)
            
            if host_analysis: 
                host_analysis_Df = pd.DataFrame(host_analysis)
                host_analysis_Df.columns = ["Host Name", "Total Listing"]
                fig = px.bar(host_analysis_Df, title="Top 10 Hosts", x="Host Name", y="Total Listing",
                            color="Host Name", color_discrete_sequence=px.colors.qualitative.Plotly)
                
                st.plotly_chart(fig, use_container_width=True)  
            else:
                st.warning("No Data Available")

    if l2=="Price Analysis":
        col1,col2,col3=st.columns(3)
        with col1:
            countries_list=extract_countries()
            selected_country=st.selectbox("Select a Country",countries_list)
            if selected_country:
                price_analysis=price(selected_country)
                price_analysis=[{k:float(str(v)) if isinstance(v,Decimal128) else v for k, v in i.items()} for i in price_analysis]
                df3=pd.DataFrame(price_analysis)
                df3=df3.dropna()
                df3.columns=["Name","Price","Security Deposit","Total","Cleaning Fees"]
        
        with col2:
            selected_name = st.selectbox("Select a Property Name", sorted(df3["Name"].unique()))
            filtered_data = df3[df3["Name"] == selected_name]
        pie_data = pd.DataFrame({
            "Category": ["Price", "Security Deposit", "Cleaning Fees"],
            "Value": [filtered_data["Price"].values[0], filtered_data["Security Deposit"].values[0], filtered_data["Cleaning Fees"].values[0]]
        })
        fig1 = px.pie(pie_data, values="Value", names="Category", title=f"Price Distribution for {selected_name}",hole=0.4,color_discrete_sequence=px.colors.qualitative.Set1)
        st.plotly_chart(fig1)
        st.dataframe(df3)
    


