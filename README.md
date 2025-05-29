# AIRBNB-ANALYSIS
## ****Domain**: Travel Industry,Property Management and Tourism**
### **Introduction**
  This project analyzes Airbnb data with MangoDB Atlas,focusing on cleaning the data,creating interactive maps, and visualizing pricing,availability and location trends.
### Table of Contents
* Technologies Used
* Installation
* Import Libraries from Modules
* Usage
* Features
#### Technologies Used:
* Python
* Pandas
* MangoDB Atlas
* Streamlit
* Plotly
* Tableau
#### Installation
* pip install pandas
* pip install pymongo
* pip install streamlit
* pip install plotly
##### Import Libraries from Modules
* import streamlit as st
* from streamlit_option_menu import option_menu
* import base64

* import json
* import pandas as pd
* from pymongo import MongoClientv
* from urllib.parse import quote_plus

* from collections import Counter

* from bson.decimal128 import Decimal128

* import plotly.express as px
* from PIL import Image
#### Usage
Steps to be followed for effectively using the application:
1. Access the Streamlit App: Open the application in your browser
2. Select Analysis Method: Choose from options such as Property, Locations, Analysis, or Tableau Dashboard from the navigation menu.
3. Apply Filters: Depending on your selection, apply filters such as country, property type, or amenities.
4. View Visualizations: The application will display interactive visualizations based on your chosen filters and analysis method.
5. Interact with Data: Use the provided input options to refine your queries and view detailed results
#### Features
- **Data Extraction:** Connects to MangoDB Atlas to retrieve Airbnb data.
- **Data Cleaning:** Process and prepares data using Python and Pandas, including handling missing values and duplicates.
- **Dynamic Analysis:** Performs various analyses like filtering by amenities,availability and pricing.
- **Interactive Visualizations:** Creates interactive maps and charts using Plotly to visualize property locations, types, and trends.
- **Streamlit Integration:** Provides a user-friendly web interface for exploring and analyzing data, with dynamic updates based on user input.
