import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta
import math

# ============================================================
# CẤU HÌNH TRANG
# ============================================================

st.set_page_config(
    page_title="Tính tiền lãi tiền gửi tiết kiệm",
    page_icon="💰",
    layout="wide"
)

st.title("💰 TÍNH TIỀN LÃI KHÁCH HÀNG GỬI TIẾT KIỆM")
st.caption("Quy ước: 1 năm = 365 ngày | Ngày gửi được tính lãi | Ngày rút không tính lãi")


# ============================================================
# HÀM ĐỊNH DẠNG TIỀN
# ============================================================

def format_money(value):
    return f"{value:,.0f} VNĐ"


# ============================================================
# HÀM TÍNH SỐ NGÀY
# ============================================================

def calculate_days(start_date, end_date):
    """
    Tính số ngày hưởng lãi.

    Ví dụ:
    Gửi 01/01
    Rút 02/01

    Khách hàng hưởng lãi:
    ngày 01/01

    => 1 ngày

    Vì ngày rút không tính lãi.
    """
    return (end_date - start_date).days


# ============================================================
# HÀM TÍNH LÃI THEO THÁNG
# ============================================================

def get_month_periods(start_date, end_date):
    """
    Chia khoảng thời gian gửi tiền thành từng tháng.

    Nguyên tắc:
    - Ngày gửi được tính.
    - Ngày rút không tính.
    """

    periods = []

    current_start = start_date

    while current_start < end_date:

        # Ngày cùng kỳ tháng tiếp theo
        next_month = current_start + relativedelta(months=1)

        # Không vượt quá ngày rút
        current_end = min(next_month, end_date)

        # Số ngày của khoảng hiện tại
        days = (current_end - current_start).days

        if days > 0:
            periods.append({
                "start": current_start,
                "end": current_end,
                "days": days
            })

        current_start = current_end

    return periods


# ============================================================
# HÀM TÍNH LÃI ĐƠN
# ============================================================

def calculate_simple_interest(principal, annual_rate, start_date, end_date):
    """
    Lãi đơn:

    Tiền lãi = Gốc × Lãi suất năm × Số ngày / 365

    Không nhập lãi vào gốc.
    """

    periods = get_month_periods(start_date, end_date)

    monthly_results = []

    total_interest = 0

    for i, period in enumerate(periods, start=1):

        interest = (
            principal
            * annual_rate
            * period["days"]
            / 365
        )

        total_interest += interest

        monthly_results.append({
            "Tháng": i,
            "Từ ngày": period["start"].strftime("%d/%m/%Y"),
            "Đến trước ngày": period["end"].strftime("%d/%m/%Y"),
            "Số ngày": period["days"],
            "Tiền gốc": principal,
            "Tiền lãi": interest
        })

    return total_interest, monthly_results


# ============================================================
# HÀM TÍNH LÃI KÉP
# ============================================================

def calculate_compound_interest(
    principal,
    annual_rate,
    start_date,
    end_date
):
    """
    Lãi kép.

    Lãi được nhập vào gốc theo từng tháng.

    Công thức tháng:

    Lãi tháng = Gốc hiện tại × lãi suất năm × số ngày / 365

    Sau đó:

    Gốc mới = Gốc cũ + Lãi tháng

    Chỉ sử dụng khi nhận lãi cuối kỳ.
    """

    periods = get_month_periods(start_date, end_date)

    monthly_results = []

    current_principal = principal
    total_interest = 0

    for i, period in enumerate(periods, start=1):

        interest = (
            current_principal
            * annual_rate
            * period["days"]
            / 365
        )

        total_interest += interest

        ending_principal = current_principal + interest

        monthly_results.append({
            "Tháng": i,
            "Từ ngày": period["start"].strftime("%d/%m/%Y"),
            "Đến trước ngày": period["end"].strftime("%d/%m/%Y"),
            "Số ngày": period["days"],
            "Tiền gốc đầu kỳ": current_principal,
            "Tiền lãi": interest,
            "Gốc + lãi cuối tháng": ending_principal
        })

        current_principal = ending_principal

    return total_interest, monthly_results, current_principal


# ============================================================
# HÀM TÍNH LÃI HÀNG THÁNG
# ============================================================

def calculate_monthly_interest(
    principal,
    annual_rate,
    start_date,
    end_date
):
    """
    Trường hợp nhận lãi hàng tháng.

    Lãi của từng tháng được tính trên số tiền gốc ban đầu.
    Lãi không nhập vào gốc.
    """

    periods = get_month_periods(start_date, end_date)

    monthly_results = []

    total_interest = 0

    for i, period in enumerate(periods, start=1):

        interest = (
            principal
            * annual_rate
            * period["days"]
            / 365
        )

        total_interest += interest

        monthly_results.append({
            "Tháng": i,
            "Từ ngày": period["start"].strftime("%d/%m/%Y"),
            "Đến trước ngày": period["end"].strftime("%d/%m/%Y"),
            "Số ngày": period["days"],
            "Tiền gốc": principal,
            "Tiền lãi": interest
        })

    return total_interest, monthly_results


# ============================================================
# HÀM TÍNH LÃI ĐẦU KỲ
# ============================================================

def calculate_upfront_interest(
    principal,
    annual_rate,
    total_days
):
    """
    Nhận lãi đầu kỳ.

    Về bản chất, tổng tiền lãi vẫn được tính
    theo công thức lãi đơn trên số tiền gửi.

    Tiền lãi được trả ngay khi gửi.
    """

    interest = (
        principal
        * annual_rate
        * total_days
        / 365
    )

    return interest


# ============================================================
# GIAO DIỆN NHẬP DỮ LIỆU
# ============================================================

st.subheader("1️⃣ Thông tin khoản tiền gửi")

col1, col2 = st.columns(2)

with col1:

    principal = st.number_input(
        "💵 Số tiền gửi (VNĐ)",
        min_value=1000.0,
        value=100_000_000.0,
        step=1_000_000.0,
        format="%.0f"
    )

    annual_rate_percent = st.number_input(
        "📈 Lãi suất (%/năm)",
        min_value=0.0,
        max_value=100.0,
        value=6.0,
        step=0.01,
        format="%.2f"
    )

    annual_rate = annual_rate_percent / 100

with col2:

    term_months = st.number_input(
        "📅 Kỳ hạn (tháng)",
        min_value=1,
        max_value=120,
        value=12,
        step=1
    )

    interest_payment = st.selectbox(
        "💳 Hình thức nhận lãi",
        [
            "Cuối kỳ",
            "Hàng tháng",
            "Đầu kỳ"
        ]
    )


# ============================================================
# CHỌN LÃI ĐƠN / LÃI KÉP
# ============================================================

st.subheader("2️⃣ Phương pháp tính lãi")

if interest_payment == "Cuối kỳ":

    interest_type = st.radio(
        "Chọn phương pháp tính:",
        [
            "Lãi đơn",
            "Lãi kép"
        ],
        horizontal=True
    )

else:

    interest_type = "Lãi đơn"

    st.info(
        "ℹ️ Lãi kép chỉ áp dụng cho hình thức nhận lãi cuối kỳ. "
        "Khoản tiền nhận lãi hàng tháng hoặc đầu kỳ được tính theo lãi đơn."
    )


# ============================================================
# NGÀY GỬI / NGÀY RÚT
# ============================================================

st.subheader("3️⃣ Thời gian gửi tiền")

col3, col4 = st.columns(2)

with col3:

    start_date = st.date_input(
        "📥 Ngày khách hàng gửi tiền",
        value=date.today(),
        format="DD/MM/YYYY"
    )

with col4:

    # Mặc định ngày rút = ngày gửi + kỳ hạn
    default_end_date = start_date + relativedelta(
        months=int(term_months)
    )

    end_date = st.date_input(
        "📤 Ngày khách hàng rút tiền",
        value=default_end_date,
        format="DD/MM/YYYY"
    )


# ============================================================
# KIỂM TRA NGÀY
# ============================================================

if end_date <= start_date:

    st.error(
        "❌ Ngày rút tiền phải lớn hơn ngày gửi tiền."
    )

    st.stop()


# ============================================================
# TÍNH SỐ NGÀY
# ============================================================

total_days = calculate_days(
    start_date,
    end_date
)


# ============================================================
# HIỂN THỊ THÔNG TIN THỜI GIAN
# ============================================================

st.subheader("4️⃣ Thông tin thời gian gửi")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Số ngày hưởng lãi",
        f"{total_days} ngày"
    )

with c2:
    st.metric(
        "Ngày bắt đầu tính lãi",
        start_date.strftime("%d/%m/%Y")
    )

with c3:
    st.metric(
        "Ngày cuối cùng tính lãi",
        (end_date - relativedelta(days=1)).strftime("%d/%m/%Y")
    )


st.caption(
    f"Lãi được tính từ ngày {start_date.strftime('%d/%m/%Y')} "
    f"đến hết ngày {(end_date - relativedelta(days=1)).strftime('%d/%m/%Y')}. "
    f"Ngày {end_date.strftime('%d/%m/%Y')} là ngày rút tiền nên không tính lãi."
)


# ============================================================
# NÚT TÍNH
# ============================================================

st.divider()

calculate_button = st.button(
    "🧮 TÍNH TIỀN LÃI",
    type="primary",
    use_container_width=True
)


# ============================================================
# KẾT QUẢ
# ============================================================

if calculate_button:

    # --------------------------------------------------------
    # LÃI ĐƠN
    # --------------------------------------------------------

    if interest_type == "Lãi đơn":

        if interest_payment == "Cuối kỳ":

            total_interest, monthly_results = calculate_simple_interest(
                principal,
                annual_rate,
                start_date,
                end_date
            )

        elif interest_payment == "Hàng tháng":

            total_interest, monthly_results = calculate_monthly_interest(
                principal,
                annual_rate,
                start_date,
                end_date
            )

        else:

            total_interest = calculate_upfront_interest(
                principal,
                annual_rate,
                total_days
            )

            monthly_results = []

            periods = get_month_periods(
                start_date,
                end_date
            )

            for i, period in enumerate(periods, start=1):

                interest = (
                    principal
                    * annual_rate
                    * period["days"]
                    / 365
                )

                monthly_results.append({
                    "Tháng": i,
                    "Từ ngày": period["start"].strftime("%d/%m/%Y"),
                    "Đến trước ngày": period["end"].strftime("%d/%m/%Y"),
                    "Số ngày": period["days"],
                    "Tiền gốc": principal,
                    "Tiền lãi": interest
                })

        final_amount = principal + total_interest

    # --------------------------------------------------------
    # LÃI KÉP
    # --------------------------------------------------------

    else:

        total_interest, monthly_results, final_amount = calculate_compound_interest(
            principal,
            annual_rate,
            start_date,
            end_date
        )


    # ========================================================
    # KẾT QUẢ TỔNG QUAN
    # ========================================================

    st.divider()

    st.subheader("5️⃣ KẾT QUẢ TÍNH TIỀN")

    result1, result2, result3 = st.columns(3)

    with result1:

        st.metric(
            "💵 Tiền gốc",
            format_money(principal)
        )

    with result2:

        st.metric(
            "📈 Tổng tiền lãi",
            format_money(total_interest)
        )

    with result3:

        st.metric(
            "💰 Tổng tiền nhận",
            format_money(final_amount)
        )


    # ========================================================
    # THÔNG TIN HÌNH THỨC NHẬN LÃI
    # ========================================================

    st.info(
        f"""
**Hình thức nhận lãi:** {interest_payment}

**Phương pháp tính:** {interest_type}

**Số tiền gửi:** {format_money(principal)}

**Lãi suất:** {annual_rate_percent:.2f}%/năm

**Số ngày thực tế hưởng lãi:** {total_days} ngày

**Ngày gửi:** {start_date.strftime('%d/%m/%Y')}

**Ngày rút:** {end_date.strftime('%d/%m/%Y')}
"""
    )


    # ========================================================
    # TIỀN LÃI HÀNG THÁNG
    # ========================================================

    st.subheader("6️⃣ Chi tiết tiền lãi theo từng tháng")

    if interest_payment == "Đầu kỳ":

        st.success(
            f"💰 Tiền lãi khách hàng được nhận ngay đầu kỳ: "
            f"**{format_money(total_interest)}**"
        )

    if monthly_results:

        # Tạo bảng dữ liệu hiển thị đẹp hơn
        display_data = []

        for row in monthly_results:

            item = {
                "Tháng": row["Tháng"],
                "Từ ngày": row["Từ ngày"],
                "Đến trước ngày": row["Đến trước ngày"],
                "Số ngày": row["Số ngày"],
            }

            if interest_type == "Lãi kép":

                item["Gốc đầu kỳ"] = format_money(
                    row["Tiền gốc đầu kỳ"]
                )

                item["Tiền lãi"] = format_money(
                    row["Tiền lãi"]
                )

                item["Gốc + lãi cuối tháng"] = format_money(
                    row["Gốc + lãi cuối tháng"]
                )

            else:

                item["Tiền gốc"] = format_money(
                    row["Tiền gốc"]
                )

                item["Tiền lãi"] = format_money(
                    row["Tiền lãi"]
                )

            display_data.append(item)

        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )


    # ========================================================
    # THÔNG TIN TỔNG KẾT
    # ========================================================

    st.subheader("7️⃣ Tổng kết khoản tiền gửi")

    summary_col1, summary_col2 = st.columns(2)

    with summary_col1:

        st.write("**Tiền gốc ban đầu:**")
        st.write(f"### {format_money(principal)}")

        st.write("**Tổng tiền lãi:**")
        st.write(f"### {format_money(total_interest)}")

    with summary_col2:

        st.write("**Tổng số tiền khách hàng nhận:**")
        st.write(f"### {format_money(final_amount)}")

        st.write("**Ngày nhận tiền:**")
        st.write(f"### {end_date.strftime('%d/%m/%Y')}")


    # ========================================================
    # CÔNG THỨC
    # ========================================================

    with st.expander("📐 Xem công thức tính"):

        st.markdown(
            """
### Lãi đơn

**Tiền lãi = Tiền gốc × Lãi suất năm × Số ngày / 365**

Trong đó:

- Tiền gốc: số tiền khách hàng gửi
- Lãi suất năm: lãi suất nhập vào / 100
- Số ngày: từ ngày gửi đến trước ngày rút
- 365: số ngày quy ước trong một năm

### Lãi kép

Mỗi kỳ:

**Tiền lãi kỳ = Tiền gốc hiện tại × Lãi suất năm × Số ngày / 365**

Sau đó:

**Tiền gốc mới = Tiền gốc cũ + Tiền lãi**

Lãi kỳ sau được tính trên số tiền gốc mới.

### Quy tắc ngày

Ví dụ:

Khách hàng gửi **01/10/2026** và rút **05/10/2026**.

Các ngày được tính lãi:

- 01/10
- 02/10
- 03/10
- 04/10

Ngày **05/10** là ngày rút tiền nên **không tính lãi**.

=> Tổng cộng **4 ngày hưởng lãi**.
"""
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "💰 Ứng dụng tính lãi tiền gửi tiết kiệm | Quy ước 365 ngày/năm"
)
