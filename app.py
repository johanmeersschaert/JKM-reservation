
import streamlit as st
import datetime
import uuid

# Theme & Styling
st.set_page_config(page_title="Arbrå Horse Arena Booking", page_icon="🐴", layout="centered")

# Blue & White Huisstijl Injection
st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
    }
    h1, h2, h3 {
        color: #0033aa !important;
    }
    .stButton>button {
        background-color: #0033aa;
        color: white;
        border-radius: 5px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #002288;
        color: white;
    }
    </style>
""", unsafe_index=True)

# Initialize Session State for DB simulation
if 'bookings' not in st.session_state:
    st.session_state.bookings = []
if 'admin_email' not in st.session_state:
    st.session_state.admin_email = "admin@arbrastables.se"
if 'promo_codes' not in st.session_state:
    st.session_state.promo_codes = ["ARBRA2026", "FREEPASS", "STALBLAUWWIT"]

st.title("🐴 Arbrå Horse Arena Booking")
st.caption("Phase 1 Prototype - Location: Arbrå, Sweden | Huisstijl: Blue & White")

tabs = st.tabs(["🔒 Customer Booking", "⚙️ Admin Dashboard"])

with tabs[0]:
    st.header("Book an Arena Slot")
    
    # 1. Arena Selection
    arena = st.radio("Select Arena:", ["Indoor Arena", "Outdoor Arena"], horizontal=True)
    
    # 2. Date and Time Selection
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Select Date:", datetime.date.today())
    with col2:
        # Business hours 08:00 - 22:00
        hours = [f"{h:02d}:00" for h in range(8, 23)]
        time_slot = st.selectbox("Select Time Slot (1 Hour):", hours)
        
    # Check current capacity for the selection
    existing_slots = [b for b in st.session_state.bookings if b['date'] == str(date) and b['time'] == time_slot and b['arena'] == arena]
    
    is_private_booked = any(b['type'] == "100% Private" for b in existing_slots)
    current_shared_count = sum(1 for b in existing_slots if b['type'] == "Shared Slot")
    
    if is_private_booked:
        st.error("❌ This slot is fully booked as a 100% Private session. Please select another time.")
        can_proceed = False
    elif current_shared_count >= 5:
        st.error("❌ This slot has reached its maximum shared capacity (5/5 combinations). Please select another time.")
        can_proceed = False
    else:
        can_proceed = True
        if current_shared_count > 0:
            st.warning(f"ℹ️ Shared active: Currently {current_shared_count}/5 horse combinations booked for this hour.")
        else:
            st.success("✅ This hour is fully available.")

    if can_proceed:
        # 3. Rental Type
        # If shared slots exist, you cannot book it 100% private
        if current_shared_count > 0:
            rental_type = st.radio("Rental Type:", ["Shared Slot"])
            st.info("Note: '100% Private' is unavailable because others have already booked spots in this slot.")
        else:
            rental_type = st.radio("Rental Type:", ["Shared Slot", "100% Private"])
            
        # 4. Mandatory Info
        st.subheader("Contact Information")
        name = st.text_input("Full Name *")
        email = st.text_input("Email Address *")
        phone = st.text_input("Mobile Phone Number (GSM) *")
        
        # 5. Payment or Bypass
        st.subheader("Checkout & Payment")
        payment_method = st.radio("Choose payment way:", ["Online via Swish (Sweden)", "Administrator Bypass Code"])
        
        code_validated = False
        if payment_method == "Administrator Bypass Code":
            entered_code = st.text_input("Enter Admin Promo Code:")
            if entered_code:
                if entered_code in st.session_state.promo_codes:
                    st.success("✅ Code valid! Booking is 100% free.")
                    code_validated = True
                else:
                    st.error("❌ Invalid Code. Please pay via Swish or ask the administrator.")
        
        # Complete button
        if st.button("Complete Reservation"):
            if not name or not email or not phone:
                st.error("⚠️ Please fill in all mandatory contact information fields (Name, Email, GSM).")
            elif payment_method == "Administrator Bypass Code" and not code_validated:
                st.error("⚠️ You must provide a valid Administrator Bypass Code to finish for free.")
            else:
                # Successfully booked!
                booking_id = str(uuid.uuid4())[:8].upper()
                new_booking = {
                    "id": booking_id,
                    "arena": arena,
                    "date": str(date),
                    "time": time_slot,
                    "type": rental_type,
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "payment": "Bypass Code" if payment_method == "Administrator Bypass Code" else "Swish API Approved"
                }
                st.session_state.bookings.append(new_booking)
                
                st.balloons()
                st.success(f"🎉 Booking Confirmed! Code: **{booking_id}**")
                
                # Notification Logs simulation
                st.info("📧 **Automated Emails Sent Successfully!**")
                st.markdown(f"""
                * **To Customer ({email}):** Confirmation for {arena} on {date} at {time_slot} ({rental_type}).
                * **To Administrator ({st.session_state.admin_email}):** Alert! New booking {booking_id} by {name} ({phone}).
                """)

with tabs[1]:
    st.header("Admin Control Panel")
    
    # Settings: Admin Email
    st.session_state.admin_email = st.text_input("Configure Administrator Notification Email:", st.session_state.admin_email)
    
    # Active Bookings
    st.subheader("Active Bookings List")
    if len(st.session_state.bookings) == 0:
        st.info("No bookings recorded yet.")
    else:
        df = pd.DataFrame(st.session_state.bookings)
        st.dataframe(df[["id", "arena", "date", "time", "type", "name", "email", "phone", "payment"]])
        
        # Delete functional log
        st.subheader("Manage / Remove Bookings")
        booking_to_delete = st.selectbox("Select Booking to Delete:", options=[b['id'] for b in st.session_state.bookings])
        if st.button("Permanently Delete Booking"):
            st.session_state.bookings = [b for b in st.session_state.bookings if b['id'] != booking_to_delete]
            st.success(f"🗑️ Booking {booking_to_delete} was successfully removed by administrator.")
            st.rerun()
