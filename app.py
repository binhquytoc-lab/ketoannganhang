import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta
st.image("KETOAN.jpg")
# ============================================================
# CẤU HÌNH TRANG
# ============================================================

st.set_page_config(
    page_title="Tính tiền lãi tiền gửi tiết kiệm",
    page_icon="💰",
    layout="wide"
)

st.title("💰 PHẦN MỀM TÍNH TIỀN GỬI TIẾT KIỆM_TS. VŨ ĐỨC BÌNH")

st.caption(
    "Quy ước: 1 năm = 365 ngày | Ngày gửi được tính lãi | "
    "Ngày rút không tính lãi"
)


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

    Ngày gửi được tính.
    Ngày rút không tính.

    Ví dụ:
    Gửi 01/01
    Rút 05/01

    Số ngày hưởng lãi = 4 ngày:
    01/01, 02/01, 03/01, 04/01
    """

    return (end_date - start_date).days


# ============================================================
# HÀM CHIA THỜI GIAN THEO THÁNG
# ============================================================

def get_month_periods(start_date, end_date):
    """
    Chia khoảng thời gian gửi tiền thành từng khoảng tháng.

    Ngày gửi được tính.
    Ngày rút không tính.
    """

    periods = []

    current_start = start_date

    while current_start < end_date:

        next_month = current_start + relativedelta(months=1)

        current_end = min(next_month, end_date)

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

def calculate_simple_interest(
    principal,
    annual_rate,
    start_date,
    end_date
):
    """
    Lãi đơn:

    Lãi = Gốc × Lãi suất năm × Số ngày / 365

    Lãi không nhập vào gốc.
    """

    periods = get_month_periods(
        start_date,
        end_date
    )

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

    Lãi mỗi tháng được nhập vào gốc.

    Chỉ sử dụng cho trường hợp nhận lãi cuối kỳ
    và KHÔNG rút trước hạn.
    """

    periods = get_month_periods(
        start_date,
        end_date
    )

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

        ending_principal = (
            current_principal
            + interest
        )

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

    return (
        total_interest,
        monthly_results,
        current_principal
    )


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
    Tính lãi hàng tháng.

    Tiền lãi không nhập vào gốc.
    """

    periods = get_month_periods(
        start_date,
        end_date
    )

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
    Tính tiền lãi đầu kỳ.

    Lãi được tính theo lãi đơn.
    """

    interest = (
        principal
        * annual_rate
        * total_days
        / 365
    )

    return interest


# ============================================================
# 1. THÔNG TIN KHOẢN TIỀN GỬI
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
        "📈 Lãi suất có kỳ hạn (%/năm)",
        min_value=0.0,
        max_value=100.0,
        value=6.0,
        step=0.01,
        format="%.2f"
    )

    annual_rate = annual_rate_percent / 100


with col2:

    non_term_rate_percent = st.number_input(
        "📉 Lãi suất không kỳ hạn (%/năm)",
        min_value=0.0,
        max_value=100.0,
        value=0.50,
        step=0.01,
        format="%.2f"
    )

    non_term_rate = non_term_rate_percent / 100

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
# 2. PHƯƠNG PHÁP TÍNH LÃI
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
        "Hàng tháng và đầu kỳ sử dụng lãi đơn."
    )


# ============================================================
# 3. NGÀY GỬI VÀ NGÀY RÚT
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

    # Ngày đáo hạn theo kỳ hạn
    maturity_date = (
        start_date
        + relativedelta(months=int(term_months))
    )

    end_date = st.date_input(
        "📤 Ngày khách hàng rút tiền",
        value=maturity_date,
        format="DD/MM/YYYY"
    )


# ============================================================
# 4. KIỂM TRA NGÀY RÚT
# ============================================================

if end_date <= start_date:

    st.error(
        "❌ Ngày rút tiền phải lớn hơn ngày gửi tiền."
    )

    st.stop()


# ============================================================
# 5. XÁC ĐỊNH TRẠNG THÁI KHOẢN TIỀN GỬI
# ============================================================

total_days = calculate_days(
    start_date,
    end_date
)


# Rút trước ngày đáo hạn
is_early_withdrawal = end_date < maturity_date

# Rút đúng ngày đáo hạn
is_on_maturity = end_date == maturity_date

# Rút sau ngày đáo hạn
is_after_maturity = end_date > maturity_date


# ============================================================
# 6. HIỂN THỊ NGÀY ĐÁO HẠN
# ============================================================

st.subheader("4️⃣ Thông tin kỳ hạn")

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(
        "Ngày gửi",
        start_date.strftime("%d/%m/%Y")
    )

with c2:

    st.metric(
        "Ngày đáo hạn",
        maturity_date.strftime("%d/%m/%Y")
    )

with c3:

    st.metric(
        "Ngày rút",
        end_date.strftime("%d/%m/%Y")
    )

with c4:

    st.metric(
        "Số ngày hưởng lãi",
        f"{total_days} ngày"
    )


# ============================================================
# 7. HIỂN THỊ TRẠNG THÁI RÚT TIỀN
# ============================================================

if is_early_withdrawal:

    st.error(
        f"""
🚨 **KHÁCH HÀNG RÚT TRƯỚC HẠN**

Ngày đáo hạn: **{maturity_date.strftime('%d/%m/%Y')}**

Ngày rút tiền: **{end_date.strftime('%d/%m/%Y')}**

Do khách hàng rút trước hạn nên khoản tiền gửi
**không được hưởng lãi suất có kỳ hạn {annual_rate_percent:.2f}%/năm**.

Khoản tiền gửi sẽ được tính theo:

### Lãi suất không kỳ hạn: {non_term_rate_percent:.2f}%/năm
"""
    )

elif is_on_maturity:

    st.success(
        f"""
✅ **KHÁCH HÀNG RÚT ĐÚNG HẠN**

Ngày đáo hạn: **{maturity_date.strftime('%d/%m/%Y')}**

Ngày rút tiền: **{end_date.strftime('%d/%m/%Y')}**

Khách hàng được hưởng:

### Lãi suất có kỳ hạn: {annual_rate_percent:.2f}%/năm
"""
    )

else:

    st.warning(
        f"""
⚠️ **KHÁCH HÀNG RÚT SAU NGÀY ĐÁO HẠN**

Ngày đáo hạn: **{maturity_date.strftime('%d/%m/%Y')}**

Ngày rút tiền: **{end_date.strftime('%d/%m/%Y')}**

Theo quy tắc của ứng dụng, vì khoản tiền không rút trước hạn
nên hệ thống đang tính theo lãi suất có kỳ hạn
**{annual_rate_percent:.2f}%/năm** cho thời gian thực tế.

Nếu ngân hàng có quy định riêng về tái tục sau đáo hạn,
cần bổ sung quy tắc tái tục tương ứng.
"""
    )


# ============================================================
# 8. XÁC ĐỊNH LÃI SUẤT THỰC TẾ ĐƯỢC ÁP DỤNG
# ============================================================

if is_early_withdrawal:

    actual_rate = non_term_rate
    actual_rate_percent = non_term_rate_percent

    rate_type_display = "Lãi suất không kỳ hạn"

else:

    actual_rate = annual_rate
    actual_rate_percent = annual_rate_percent

    rate_type_display = "Lãi suất có kỳ hạn"


# ============================================================
# 9. THÔNG TIN CÁCH TÍNH
# ============================================================

st.subheader("5️⃣ Lãi suất thực tế áp dụng")

rate_col1, rate_col2, rate_col3 = st.columns(3)

with rate_col1:

    st.metric(
        "Lãi suất đăng ký",
        f"{annual_rate_percent:.2f}%/năm"
    )

with rate_col2:

    st.metric(
        "Lãi suất không kỳ hạn",
        f"{non_term_rate_percent:.2f}%/năm"
    )

with rate_col3:

    st.metric(
        "Lãi suất thực tế",
        f"{actual_rate_percent:.2f}%/năm"
    )


st.info(
    f"📌 **Lãi suất được sử dụng để tính:** "
    f"{rate_type_display} — **{actual_rate_percent:.2f}%/năm**"
)


# ============================================================
# 10. NÚT TÍNH TIỀN
# ============================================================

st.divider()

calculate_button = st.button(
    "🧮 TÍNH TIỀN LÃI",
    type="primary",
    use_container_width=True
)


# ============================================================
# 11. TÍNH KẾT QUẢ
# ============================================================

if calculate_button:

    # ========================================================
    # TRƯỜNG HỢP RÚT TRƯỚC HẠN
    # ========================================================

    if is_early_withdrawal:

        # ----------------------------------------------------
        # Rút trước hạn luôn tính theo lãi suất không kỳ hạn
        # ----------------------------------------------------

        # Lãi kép không còn được áp dụng
        actual_interest_type = "Lãi đơn"

        total_interest, monthly_results = (
            calculate_simple_interest(
                principal,
                actual_rate,
                start_date,
                end_date
            )
        )

        final_amount = (
            principal
            + total_interest
        )

        early_withdrawal_note = (
            "Rút trước hạn → tính lãi suất không kỳ hạn"
        )


    # ========================================================
    # TRƯỜNG HỢP ĐÚNG HẠN / KHÔNG TRƯỚC HẠN
    # ========================================================

    else:

        actual_interest_type = interest_type

        # ----------------------------------------------------
        # LÃI ĐƠN
        # ----------------------------------------------------

        if interest_type == "Lãi đơn":

            if interest_payment == "Cuối kỳ":

                total_interest, monthly_results = (
                    calculate_simple_interest(
                        principal,
                        actual_rate,
                        start_date,
                        end_date
                    )
                )

            elif interest_payment == "Hàng tháng":

                total_interest, monthly_results = (
                    calculate_monthly_interest(
                        principal,
                        actual_rate,
                        start_date,
                        end_date
                    )
                )

            else:

                total_interest = calculate_upfront_interest(
                    principal,
                    actual_rate,
                    total_days
                )

                monthly_results = []

                periods = get_month_periods(
                    start_date,
                    end_date
                )

                for i, period in enumerate(
                    periods,
                    start=1
                ):

                    interest = (
                        principal
                        * actual_rate
                        * period["days"]
                        / 365
                    )

                    monthly_results.append({
                        "Tháng": i,
                        "Từ ngày": period["start"].strftime(
                            "%d/%m/%Y"
                        ),
                        "Đến trước ngày": period["end"].strftime(
                            "%d/%m/%Y"
                        ),
                        "Số ngày": period["days"],
                        "Tiền gốc": principal,
                        "Tiền lãi": interest
                    })

            final_amount = (
                principal
                + total_interest
            )

        # ----------------------------------------------------
        # LÃI KÉP
        # ----------------------------------------------------

        else:

            total_interest, monthly_results, final_amount = (
                calculate_compound_interest(
                    principal,
                    actual_rate,
                    start_date,
                    end_date
                )
            )

        early_withdrawal_note = (
            "Không rút trước hạn → áp dụng lãi suất có kỳ hạn"
        )


    # ========================================================
    # 12. KẾT QUẢ TỔNG QUAN
    # ========================================================

    st.divider()

    st.subheader("6️⃣ KẾT QUẢ TÍNH TIỀN")

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
    # 13. THÔNG TIN CHI TIẾT
    # ========================================================

    st.subheader("7️⃣ Thông tin khoản tiền gửi")

    st.info(
        f"""
**Số tiền gửi:** {format_money(principal)}

**Kỳ hạn:** {term_months} tháng

**Ngày gửi:** {start_date.strftime('%d/%m/%Y')}

**Ngày đáo hạn:** {maturity_date.strftime('%d/%m/%Y')}

**Ngày rút:** {end_date.strftime('%d/%m/%Y')}

**Số ngày thực tế hưởng lãi:** {total_days} ngày

**Hình thức nhận lãi:** {interest_payment}

**Phương pháp tính:** {actual_interest_type}

**Lãi suất có kỳ hạn:** {annual_rate_percent:.2f}%/năm

**Lãi suất không kỳ hạn:** {non_term_rate_percent:.2f}%/năm

**Lãi suất thực tế áp dụng:** {actual_rate_percent:.2f}%/năm

**Trạng thái:** {early_withdrawal_note}
"""
    )


    # ========================================================
    # 14. CẢNH BÁO RÚT TRƯỚC HẠN
    # ========================================================

    if is_early_withdrawal:

        st.warning(
            f"""
⚠️ **LƯU Ý RÚT TRƯỚC HẠN**

Khách hàng đã rút tiền vào ngày
**{end_date.strftime('%d/%m/%Y')}**,
trong khi ngày đáo hạn là
**{maturity_date.strftime('%d/%m/%Y')}**.

Do đó:

- Không áp dụng lãi suất có kỳ hạn
  **{annual_rate_percent:.2f}%/năm**.
- Áp dụng lãi suất không kỳ hạn
  **{non_term_rate_percent:.2f}%/năm**.
- Lãi được tính theo **lãi đơn**.
- Nếu người dùng chọn lãi kép thì hệ thống vẫn chuyển
  sang lãi đơn vì khoản tiền đã bị rút trước hạn.
"""
        )


    # ========================================================
    # 15. TIỀN LÃI THEO TỪNG THÁNG
    # ========================================================

    st.subheader(
        "8️⃣ Chi tiết tiền lãi theo từng tháng"
    )

    if interest_payment == "Đầu kỳ":

        if is_early_withdrawal:

            st.warning(
                f"""
Do khách hàng **rút trước hạn**, tiền lãi được tính lại
theo lãi suất không kỳ hạn.

Tổng tiền lãi được tính lại:

### {format_money(total_interest)}
"""
            )

        else:

            st.success(
                f"""
💰 Tiền lãi nhận đầu kỳ:

### {format_money(total_interest)}
"""
            )


    if monthly_results:

        display_data = []

        for row in monthly_results:

            item = {
                "Tháng": row["Tháng"],
                "Từ ngày": row["Từ ngày"],
                "Đến trước ngày": row["Đến trước ngày"],
                "Số ngày": row["Số ngày"]
            }

            # ----------------------------------------------
            # LÃI KÉP
            # ----------------------------------------------

            if (
                actual_interest_type == "Lãi kép"
                and "Tiền gốc đầu kỳ" in row
            ):

                item["Gốc đầu kỳ"] = format_money(
                    row["Tiền gốc đầu kỳ"]
                )

                item["Tiền lãi"] = format_money(
                    row["Tiền lãi"]
                )

                item["Gốc + lãi cuối tháng"] = format_money(
                    row["Gốc + lãi cuối tháng"]
                )

            # ----------------------------------------------
            # LÃI ĐƠN
            # ----------------------------------------------

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
    # 16. TỔNG KẾT
    # ========================================================

    st.subheader("9️⃣ Tổng kết khoản tiền gửi")

    summary_col1, summary_col2 = st.columns(2)

    with summary_col1:

        st.write("**Tiền gốc ban đầu:**")
        st.write(
            f"### {format_money(principal)}"
        )

        st.write("**Tổng tiền lãi:**")
        st.write(
            f"### {format_money(total_interest)}"
        )

    with summary_col2:

        st.write(
            "**Tổng số tiền khách hàng nhận:**"
        )

        st.write(
            f"### {format_money(final_amount)}"
        )

        st.write("**Ngày nhận tiền:**")

        st.write(
            f"### {end_date.strftime('%d/%m/%Y')}"
        )


    # ========================================================
    # 17. CÔNG THỨC
    # ========================================================

    with st.expander("📐 Xem công thức tính"):

        st.markdown(
            f"""
### 1. Trường hợp rút đúng hạn

Lãi suất áp dụng:

**{annual_rate_percent:.2f}%/năm**

Công thức lãi đơn:

**Tiền lãi = Tiền gốc × Lãi suất × Số ngày / 365**

---

### 2. Trường hợp rút trước hạn

Lãi suất áp dụng:

**{non_term_rate_percent:.2f}%/năm**

Công thức:

**Tiền lãi = Tiền gốc × Lãi suất không kỳ hạn × Số ngày / 365**

Khi rút trước hạn, hệ thống **không sử dụng lãi suất có kỳ hạn**.

Nếu người dùng chọn **lãi kép**, hệ thống cũng chuyển sang
**lãi đơn** vì khoản tiền đã rút trước hạn.

---

### 3. Quy tắc ngày

Ngày gửi **được tính lãi**.

Ngày rút **không tính lãi**.

Ví dụ:

Gửi:

**01/10/2026**

Rút:

**05/10/2026**

Các ngày được tính:

- 01/10
- 02/10
- 03/10
- 04/10

Tổng cộng:

**4 ngày**

---

### 4. Quy tắc xác định trước hạn

Ngày đáo hạn được tính:

**Ngày đáo hạn = Ngày gửi + Kỳ hạn**

Ví dụ:

Ngày gửi: **01/01/2026**

Kỳ hạn: **12 tháng**

Ngày đáo hạn:

**01/01/2027**

Nếu ngày rút:

**31/12/2026**

→ Rút trước hạn.

Nếu ngày rút:

**01/01/2027**

→ Rút đúng hạn.

"""
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "💰 Ứng dụng tính lãi tiền gửi tiết kiệm | "
    "Quy ước 365 ngày/năm | "
    "Ngày gửi tính lãi, ngày rút không tính lãi"
)
