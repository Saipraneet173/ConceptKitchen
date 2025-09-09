# import streamlit as st
# from app import langchain_helper

# st.title("Restaurant Name Generator")
# cuisine = st.sidebar.selectbox("Pick a Cuisine", ("Indian", "Italian","Mexican","Korean","Japanese","Lebanese"))
#
# if cuisine:
#     response = langchain_helper.generate_restaurant_name_items(cuisine)
#     st.header(response['restaurant_name'].strip())
#     menu_items = response['menu_items'].strip().split(",")
#     st.write("**Menu Items**")
#     for item in menu_items:
#         st.write("-", item)

import streamlit as st
import chains

st.title("🍳 ConceptKitchen")
st.subheader("*AI-Powered Restaurant Concept Generator*")

cuisine = st.sidebar.selectbox(
    "Pick a Cuisine",
    ("Indian", "Italian", "Mexican", "Korean", "Japanese", "Lebanese", "French", "Thai")
)

# Add a toggle for advanced features
use_advanced = st.sidebar.checkbox("✨ Generate with tagline", value=True)

if cuisine:
    with st.spinner(f"Crafting your {cuisine} restaurant concept..."):
        if use_advanced:
            # Use the new parallel generation
            response = langchain_helper.generate_restaurant_name_items_parallel(cuisine)
        else:
            # Use basic generation
            response = langchain_helper.generate_restaurant_name_items(cuisine)

    # Display the restaurant name with better styling
    st.header(response['restaurant_name'].strip())

    # Display tagline if available
    if 'tagline' in response and response['tagline']:
        st.caption(f"*\"{response['tagline']}\"*")

    # Display menu items with better formatting
    st.write("**🍽️ Signature Menu Items**")

    # Split by comma and clean up each item
    menu_items = [item.strip() for item in response['menu_items'].split(",") if item.strip()]

    # Create two columns for menu display
    col1, col2 = st.columns(2)
    for i, item in enumerate(menu_items):
        if i % 2 == 0:
            col1.write(f"• {item}")
        else:
            col2.write(f"• {item}")