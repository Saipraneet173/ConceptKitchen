import streamlit as st
from chains import RestaurantConceptGenerator
from pdf_generator import RestaurantPDFGenerator
import json
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="ConceptKitchen - Restaurant Generator",
    page_icon="🍳",
    layout="wide"
)

# Initialize session state
if 'current_restaurant' not in st.session_state:
    st.session_state.current_restaurant = None
if 'restaurant_history' not in st.session_state:
    st.session_state.restaurant_history = []

# Demo restaurant data for users without API key
DEMO_RESTAURANT = {
    'concept': {
        'name': 'The Quantum Fork',
        'tagline': 'Where molecular gastronomy meets comfort food',
        'concept': 'A revolutionary dining experience that deconstructs familiar comfort foods and rebuilds them using cutting-edge culinary techniques. Every dish tells a story of transformation while maintaining the soul of home cooking.',
        'unique_selling_points': [
            'Live molecular transformation table-side experiences',
            'AI-powered flavor pairing recommendations',
            'Zero-waste kitchen with full ingredient utilization'
        ],
        'ambiance': 'Industrial chic meets cozy library - exposed brick walls lined with cookbook shelves, Edison bulb chandeliers, and an open laboratory-style kitchen with viewing windows',
        'target_audience': 'Adventurous foodies, tech professionals, and couples seeking unique date night experiences',
        'signature_dish': 'Deconstructed Mac & Cheese: Aged cheddar sphere, truffle-infused pasta crisps, molecular milk foam'
    },
    'menu': {
        'appetizers': [
            {'name': 'Levitating Soup Dumpling', 'description': 'Magnetic plate creates floating dumpling illusion',
             'price': '$18', 'dietary': []},
            {'name': 'Garden Patch Terrarium', 'description': 'Edible soil, micro vegetables, truffle mushrooms',
             'price': '$16', 'dietary': ['vegetarian']},
            {'name': 'Smoke & Mirrors Bruschetta', 'description': 'Tomato glass, basil oil, mozzarella snow',
             'price': '$14', 'dietary': ['gluten-free']}
        ],
        'mains': [
            {'name': 'Time-Lapse Beef Wellington', 'description': 'Watch puff pastry bloom in custom heating dome',
             'price': '$48', 'dietary': []},
            {'name': 'Schrödingers Salmon', 'description': 'Cooked and raw preparations in quantum superposition',
             'price': '$42', 'dietary': ['gluten-free']},
            {'name': 'The Impossible Garden', 'description': 'Plant-based meats grown from vegetable proteins',
             'price': '$38', 'dietary': ['vegan']},
            {'name': 'Memory Lane Meatloaf', 'description': 'Childhood favorite elevated with wagyu and foie gras',
             'price': '$36', 'dietary': []}
        ],
        'desserts': [
            {'name': 'Backwards Tiramisu', 'description': 'Coffee foam base with mascarpone dust', 'price': '$14',
             'dietary': []},
            {'name': 'Childhood Dreams', 'description': 'Cotton candy cloud with pop rocks and gold dust',
             'price': '$12', 'dietary': ['gluten-free']}
        ],
        'beverages': [
            {'name': 'Color-Changing Cocktail', 'description': 'pH-reactive spirits shift from purple to pink',
             'price': '$16', 'dietary': []},
            {'name': 'Nitro Cold Brew Float', 'description': 'Coffee, vanilla bean ice cream, caramel dust',
             'price': '$12', 'dietary': []}
        ]
    },
    'metadata': {
        'cuisine': 'Modern American',
        'style': 'Fine Dining',
        'price_range': '$$$'
    }
}


# Initialize generator
@st.cache_resource
def get_generator():
    return RestaurantConceptGenerator()


# Custom CSS
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

# Check for API key and show demo mode if not available
api_key_available = os.getenv("GROQ_API_KEY") is not None

if not api_key_available:
    st.warning("🔐 No API key detected. Running in demo mode.")
    st.info("💡 To use with your own API key, create a `.env` file with `GROQ_API_KEY=your_key_here`")

# Sidebar
with st.sidebar:
    st.header("🎨 Design Your Restaurant")

    # Demo mode section if no API key
    if not api_key_available:
        st.markdown("### 🎭 Demo Mode")
        if st.button("Load Sample Restaurant", type="primary", use_container_width=True):
            st.session_state.current_restaurant = DEMO_RESTAURANT
            st.success("✅ Demo restaurant loaded!")
            st.rerun()

        st.markdown("---")
        st.caption("In demo mode, you can explore a pre-generated restaurant concept and test all export features.")
        st.markdown("---")

    # Restaurant configuration
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

    # Generate button (disabled in demo mode without API key)
    generate_btn = st.button(
        "✨ Generate Concept",
        type="primary",
        use_container_width=True,
        disabled=(not api_key_available)
    )

    if not api_key_available and generate_btn:
        st.error("API key required for generation. Use demo mode instead.")

    # History section
    if st.session_state.restaurant_history:
        st.markdown("---")
        st.markdown("### 📚 Recent Concepts")

        # Show last 5 restaurants
        for item in reversed(st.session_state.restaurant_history[-5:]):
            timestamp_str = item['timestamp'].strftime("%I:%M %p")
            button_label = f"🍽️ {item['name'][:20]}... - {timestamp_str}"

            if st.button(button_label, key=f"history_{item['timestamp']}"):
                st.session_state.current_restaurant = item['data']
                st.rerun()

        # Clear history button
        st.markdown("---")
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.restaurant_history = []
            st.session_state.current_restaurant = None
            st.rerun()

# Main content - Generation
if generate_btn and api_key_available:
    generator = get_generator()

    with st.spinner("🎨 Crafting your unique restaurant concept..."):
        try:
            result = generator.generate_full_restaurant(cuisine, style, price_range)
            st.session_state.current_restaurant = result

            # Add to history
            st.session_state.restaurant_history.append({
                'timestamp': datetime.now(),
                'name': result['concept']['name'],
                'cuisine': cuisine,
                'data': result
            })

            # Keep only last 10 restaurants
            if len(st.session_state.restaurant_history) > 10:
                st.session_state.restaurant_history.pop(0)

        except Exception as e:
            st.error(f"Error generating concept: {str(e)}")
            st.info("Please check your API key and try again.")
            st.stop()

# Display the restaurant
if st.session_state.current_restaurant:
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
        # PDF Export
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

    if not api_key_available:
        st.warning("Or try the Demo Mode to see a sample restaurant concept!")

    # Show some stats or features
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Cuisines Available", "10+")
    with col2:
        st.metric("Restaurant Styles", "7")
    with col3:
        st.metric("Unique Concepts", "∞")