import streamlit as st
from chains import RestaurantConceptGenerator
import json
from pdf_generator import RestaurantPDFGenerator
# Page configuration
st.set_page_config(
    page_title="ConceptKitchen - Restaurant Generator",
    page_icon="🍳",
    layout="wide"
)


# Initialize generator
@st.cache_resource
def get_generator():
    return RestaurantConceptGenerator()


# Custom CSS for better styling
st.markdown("""
    <style>
    .restaurant-header { 
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .menu-item {
        background: #f7f7f7;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("🍳 ConceptKitchen")
st.markdown("*Transform your culinary dreams into a complete restaurant concept*")

# Sidebar
with st.sidebar:
    st.header("🎨 Design Your Restaurant")

    cuisine = st.selectbox(
        "Cuisine Type",
        ["Italian", "Japanese", "Mexican", "Indian", "French",
         "Thai", "Mediterranean", "Korean", "American", "Chinese"]
    )

    style = st.selectbox(
        "Restaurant Style",
        ["Casual Dining", "Fine Dining", "Fast Casual",
         "Bistro", "Food Truck", "Cafe", "Buffet"]
    )

    price_range = st.select_slider(
        "Price Range",
        options=["$", "$$", "$$$", "$$$$"],
        value="$$",
        help="$ = Budget, $$ = Moderate, $$$ = Upscale, $$$$ = Luxury"
    )

    generate_btn = st.button(
        "✨ Generate Concept",
        type="primary",
        use_container_width=True
    )

# Main content
if generate_btn:
    generator = get_generator()

    with st.spinner("🎨 Crafting your unique restaurant concept..."):
        try:
            result = generator.generate_full_restaurant(cuisine, style, price_range)
            st.session_state.current_restaurant = result
        except Exception as e:
            st.error(f"Error generating concept: {str(e)}")
            st.stop()

# Display the restaurant
if 'current_restaurant' in st.session_state:
    restaurant = st.session_state.current_restaurant
    concept = restaurant['concept']
    menu = restaurant['menu']

    # Restaurant Header
    col1, col2 = st.columns([2, 1])
    with col1:
        st.header(f"✨ {concept['name']}")
        st.caption(f"*{concept['tagline']}*")
    with col2:
        st.metric("Style", restaurant['metadata']['style'])
        st.metric("Price Range", restaurant['metadata']['price_range'])

    # Concept Details
    st.markdown("### 📖 Concept")
    st.write(concept['concept'])

    # USPs and Details in columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**🎯 Unique Selling Points**")
        for usp in concept['unique_selling_points']:
            st.write(f"• {usp}")

    with col2:
        st.markdown("**🎨 Ambiance**")
        st.info(concept['ambiance'])

    with col3:
        st.markdown("**👥 Target Audience**")
        st.info(concept['target_audience'])

    # Signature Dish Highlight
    st.markdown("### ⭐ Signature Dish")
    st.success(concept['signature_dish'])

    # Menu Section
    st.markdown("### 🍽️ Menu")

    tab1, tab2, tab3, tab4 = st.tabs(["Appetizers", "Main Courses", "Desserts", "Beverages"])

    with tab1:
        for item in menu.get('appetizers', []):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{item['name']}** - {item['price']}")
                st.caption(item['description'])
                if item.get('dietary'):
                    st.caption(f"🌱 {', '.join(item['dietary'])}")
            with col2:
                st.write("")  # Spacing

    with tab2:
        for item in menu.get('mains', []):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{item['name']}** - {item['price']}")
                st.caption(item['description'])
                if item.get('dietary'):
                    st.caption(f"🌱 {', '.join(item['dietary'])}")

    with tab3:
        for item in menu.get('desserts', []):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{item['name']}** - {item['price']}")
                st.caption(item['description'])
                if item.get('dietary'):
                    st.caption(f"🌱 {', '.join(item['dietary'])}")

    with tab4:
        for item in menu.get('beverages', []):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{item['name']}** - {item['price']}")
                st.caption(item['description'])

    # Export Options
    st.markdown("### 💾 Export Options")
    col1, col2, col3 = st.columns(3)

    with col1:
        # PDF export
        pdf_generator = RestaurantPDFGenerator()
        pdf_buffer = pdf_generator.generate_pdf(restaurant)

        st.download_button(
            label="📑 Download as PDF",
            data=pdf_buffer,
            file_name=f"{concept['name'].replace(' ', '_')}_concept.pdf",
            mime="application/pdf"
        )

    with col2:
        # JSON Export
        json_str = json.dumps(restaurant, indent=2)
        st.download_button(
            label="📄 Download as JSON",
            data=json_str,
            file_name=f"{concept['name'].replace(' ', '_')}_concept.json",
            mime="application/json"
        )
    with col3:
        if st.button("🔄 Generate New Concept"):
            st.session_state.current_restaurant = None
            st.rerun()

else:
    # Welcome screen
    st.info("👈 Configure your restaurant preferences and click 'Generate Concept' to begin!")

    # Show some stats or features
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Cuisines Available", "10+")
    with col2:
        st.metric("Restaurant Styles", "7")
    with col3:
        st.metric("Unique Concepts", "∞")