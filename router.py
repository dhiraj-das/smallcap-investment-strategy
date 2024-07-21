import streamlit as st

PAGES = [
    'Home',
    'Strategy 1: Pause/Withdraw SIP',
    'Strategy 2: Pause/Withdraw SIP + Reinvest',
    'Custom Strategy'
]

def authenticated_sidebar():
    # Show a navigation sidebar menu for authenticated users
    st.sidebar.page_link("home.py", label="Dashboard")
    st.sidebar.page_link("pages/user_profile.py", label="My profile")
    st.sidebar.page_link("login.py", label="Log out")

    if st.session_state.role in ["admin", "super-admin"]:
        st.sidebar.page_link("pages/admin.py", label="Manage users")
        st.sidebar.page_link("pages/super-admin.py", label="Manage admin access", disabled=st.session_state.role != "super-admin")

def unauthenticated_menu():
    # Show a navigation menu for unauthenticated users
    # st.sidebar.page_link("login.py", label="Log in")

    # Bypassing any authentication logic for now
    st.sidebar.title('📈 Smallcap Investment Strategy Explorer')
    st.sidebar.divider()
    st.sidebar.page_link("pages/home.py", label=PAGES[0], icon="🏠")
    st.sidebar.page_link("pages/strategy1.py", label=PAGES[1], icon="♟️")

def sidebar_menu():
    # Determine if a user is logged in or not, then show the correct navigation menu
    set_page_metadata()
    if "role" not in st.session_state or st.session_state.role is None:
        unauthenticated_menu()
        return
    authenticated_menu()


def redirect_unauthorized_users():
    # Redirect users to the main page if not logged in, otherwise continue to render the navigation menu
    if "role" not in st.session_state or st.session_state.role is None:
        st.switch_page("streamlit_app.py")
    sidebar_menu()

def set_page_metadata():
    st.set_page_config(
        page_title="Smallcap Investment Strategy Explorer",
        page_icon="📈",
        initial_sidebar_state="expanded",
        menu_items={
            'Report a bug': "https://github.com/dhiraj-das/smallcap-investment-strategy/issues/new",
            'About': """
            
            Hi there 👋! 
    
            This app has been developed by Dhiraj Das based on relative valuation model to help invest in the NIFTY smallcap index.
            If you found the tool useful, do drop a hi to me on my Email / LinkedIn
            - [Dhiraj Das](https://www.linkedin.com/in/dhiraj-das/) (email: dhiraj.das.05@gmail.com)
            """
        }
    )
