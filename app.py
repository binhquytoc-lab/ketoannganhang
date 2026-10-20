
import streamlit as st
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta

# ============================================================
# 1. CẤU HÌNH TRANG
# ============================================================

st.set_page_config(
    page_title="Tính tiền lãi tiền gửi tiết kiệm",
    page_icon="💰",
    layout="wide"
)

try:
    st.image("KETOAN.jpg", use_container_width=True)
except Exception:
    st.warning("Không tìm thấy ảnh KETOAN.jpg. Hãy đặt ảnh cùng thư mục app.py.")

st.title("💰 PHẦN MỀM TÍNH TIỀN GỬI TIẾT KIỆM - TS. VŨ ĐỨC BÌNH")

st.caption(
    "Ngày gửi được tính lãi | Ngày rút không tính lãi | "
    "Lãi suất năm chia 365 ngày | Lãi suất tháng chia 30 ngày"
)


# ============================================================
# 2. CÁC HÀM DÙNG CHUNG
# ============================================================

def format_money(value):
    return f"{value:,.0f} VNĐ"


def get_denominator(rate_unit):
    """Quy đổi mẫu số theo đơn vị lãi suất đã chọn."""
    return 365 if rate_unit == "Năm" else 30


def calculate_interest(principal, rate, days, rate_unit):
    """
    rate là lãi suất dạng số thập phân.
    Ví dụ 6% = 0.06.

    Lãi suất năm:  Gốc x lãi suất năm  x ngày / 365.
    Lãi suất tháng: Gốc x lãi suất tháng x ngày / 30.
    """
    denominator = get_denominator(rate_unit)
    return principal * rate * days / denominator


def get_month_periods(start_date, end_date):
    """
    Chia khoảng thời gian thành các đoạn theo tháng lịch.
    Ngày rút không tính lãi.
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


def get_term_periods(start_date, end_date, term_months):
    """
    Chia tiền gửi thành các kỳ theo đúng kỳ hạn đăng ký.

    Ví dụ gửi ngày 31/01, kỳ hạn 1 tháng:
    Các ngày đáo hạn được tính từ ngày gửi ban đầu,
    tránh việc ngày đáo hạn bị trôi qua các tháng.
    """
    periods = []
    index = 0

    while True:
        period_start = start_date + relativedelta(
            months=index * term_months
        )
        period_end = start_date + relativedelta(
            months=(index + 1) * term_months
        )

        if period_start >= end_date:
            break

        actual_end = min(period_end, end_date)

        if actual_end <= period_start:
            break

        periods.append({
            "start": period_start,
            "end": actual_end,
            "days": (actual_end - period_start).days,
            "full_term": actual_end == period_end,
            "term_number": index + 1
        })

        if actual_end >= end_date:
            break

        index += 1

    return periods


def calculate_simple_interest(
    principal, rate, start_date, end_date, rate_unit
):
    """Tính lãi đơn theo từng đoạn tháng lịch."""
    results = []
    total_interest = 0.0

    for i, period in enumerate(
        get_month_periods(start_date, end_date), start=1
    ):
        interest = calculate_interest(
            principal, rate, period["days"], rate_unit
        )
        total_interest += interest

        results.append({
            "Tháng": i,
            "Từ ngày": period["start"].strftime("%d/%m/%Y"),
            "Đến trước ngày": period["end"].strftime("%d/%m/%Y"),
            "Số ngày": period["days"],
            "Tiền gốc": principal,
            "Tiền lãi": interest
        })

    return total_interest, results


def calculate_compound_interest(
    principal, rate, start_date, end_date, rate_unit
):
    """
    Lãi kép trong trường hợp chưa vượt qua ngày đáo hạn:
    lãi từng tháng được nhập vào gốc để tính lãi tháng tiếp theo.
    """
    results = []
    current_principal = principal
    total_interest = 0.0

    for i, period in enumerate(
        get_month_periods(start_date, end_date), start=1
    ):
        interest = calculate_interest(
            current_principal,
            rate,
            period["days"],
            rate_unit
        )

        ending_principal = current_principal + interest
        total_interest += interest

        results.append({
            "Tháng": i,
            "Từ ngày": period["start"].strftime("%d/%m/%Y"),
            "Đến trước ngày": period["end"].strftime("%d/%m/%Y"),
            "Số ngày": period["days"],
            "Tiền gốc đầu kỳ": current_principal,
            "Tiền lãi": interest,
            "Gốc + lãi cuối kỳ": ending_principal
        })

        current_principal = ending_principal

    return total_interest, results, current_principal


def calculate_rollover(
    principal,
    term_rate,
    start_date,
    end_date,
    term_months,
    term_rate_unit,
    non_term_rate,
    non_term_rate_unit
):
    """
    Tự động tái tục theo kỳ hạn ban đầu.

    Kỳ hoàn tất:
        - Tính lãi theo lãi suất có kỳ hạn.
        - Nhập toàn bộ lãi vào gốc để tái tục kỳ tiếp theo.

    Kỳ cuối chưa hoàn tất:
        - Tính lãi theo lãi suất không kỳ hạn.
        - Không phát sinh tái tục mới.
    """
    current_principal = principal
    total_interest = 0.0
    results = []

    periods = get_term_periods(
        start_date, end_date, term_months
    )

    for period in periods:
        if period["full_term"]:
            applied_rate = term_rate
            applied_rate_unit = term_rate_unit
            rate_type = "Lãi suất có kỳ hạn"
            status = "Đã đáo hạn - nhập lãi vào gốc"
        else:
            applied_rate = non_term_rate
            applied_rate_unit = non_term_rate_unit
            rate_type = "Lãi suất không kỳ hạn"
            status = "Kỳ chưa hoàn tất - tính lãi không kỳ hạn"

        interest = calculate_interest(
            current_principal,
            applied_rate,
            period["days"],
            applied_rate_unit
        )

        ending_principal = current_principal + interest
        total_interest += interest

        results.append({
            "Kỳ tái tục": period["term_number"],
            "Từ ngày": period["start"].strftime("%d/%m/%Y"),
            "Đến trước ngày": period["end"].strftime("%d/%m/%Y"),
            "Số ngày": period["days"],
            "Trạng thái kỳ": status,
            "Lãi suất áp dụng": rate_type,
            "Gốc đầu kỳ": current_principal,
            "Lãi kỳ": interest,
            "Gốc + lãi cuối kỳ": ending_principal
        })

        # Sau kỳ hoàn tất, lãi được nhập vào gốc.
        # Ở kỳ cuối chưa hoàn tất, đây chỉ là số tiền nhận khi rút,
        # không được dùng để tái tục thêm kỳ nào nữa.
        current_principal = ending_principal

    return total_interest, results, current_principal


def calculate_monthly_payout_reclaimed(
    principal, rate, start_date, end_date,
    rate_unit, term_months
):
    """
    Tính lãi có kỳ hạn đã trả hàng tháng và phải thu hồi
    khi khách hàng rút trước hạn.

    Chỉ thu hồi lãi của các kỳ nhận lãi đã đến ngày trả
    và không vượt quá ngày rút.
    """
    reclaimed = 0.0
    payout_rows = []
    index = 1

    while True:
        payout_date = start_date + relativedelta(months=index)

        if payout_date > end_date:
            break

        previous_date = start_date + relativedelta(
            months=index - 1
        )

        days = (payout_date - previous_date).days

        interest = calculate_interest(
            principal, rate, days, rate_unit
        )

        reclaimed += interest

        payout_rows.append({
            "Lần nhận lãi": index,
            "Từ ngày": previous_date.strftime("%d/%m/%Y"),
            "Ngày nhận lãi": payout_date.strftime("%d/%m/%Y"),
            "Số ngày": days,
            "Lãi có kỳ hạn bị thu hồi": interest
        })

        index += 1

    return reclaimed, payout_rows


# ============================================================
# 3. THÔNG TIN KHOẢN TIỀN GỬI
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
        "📈 Lãi suất có kỳ hạn",
        min_value=0.0,
        max_value=100.0,
        value=6.0,
        step=0.01,
        format="%.2f"
    )

    term_rate_unit = st.selectbox(
        "Đơn vị lãi suất có kỳ hạn",
        ["Năm", "Tháng"],
        format_func=lambda x: (
            "Theo năm (%/năm)" if x == "Năm"
            else "Theo tháng (%/tháng)"
        )
    )

    annual_rate = annual_rate_percent / 100

with col2:
    non_term_rate_percent = st.number_input(
        "📉 Lãi suất không kỳ hạn",
        min_value=0.0,
        max_value=100.0,
        value=0.50,
        step=0.01,
        format="%.2f"
    )

    non_term_rate_unit = st.selectbox(
        "Đơn vị lãi suất không kỳ hạn",
        ["Năm", "Tháng"],
        format_func=lambda x: (
            "Theo năm (%/năm)" if x == "Năm"
            else "Theo tháng (%/tháng)"
        )
    )

    non_term_rate = non_term_rate_percent / 100

    term_months = st.number_input(
        "📅 Kỳ hạn gửi (tháng)",
        min_value=1,
        max_value=120,
        value=12,
        step=1
    )


# ============================================================
# 4. HÌNH THỨC NHẬN LÃI VÀ PHƯƠNG PHÁP
# ============================================================

st.subheader("2️⃣ Hình thức nhận lãi")

interest_payment = st.selectbox(
    "💳 Hình thức nhận lãi",
    ["Cuối kỳ", "Hàng tháng", "Đầu kỳ"]
)

if interest_payment == "Cuối kỳ":
    interest_type = st.radio(
        "Phương pháp tính lãi trong kỳ",
        ["Lãi đơn", "Lãi kép"],
        horizontal=True
    )
else:
    interest_type = "Lãi đơn"
    st.info(
        "Hình thức nhận lãi hàng tháng hoặc đầu kỳ sử dụng lãi đơn. "
        "Lãi được trả riêng, không tự động nhập vào gốc."
    )


# ============================================================
# 5. NGÀY GỬI VÀ NGÀY RÚT
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
    maturity_date = start_date + relativedelta(
        months=int(term_months)
    )

    end_date = st.date_input(
        "📤 Ngày khách hàng rút tiền",
        value=maturity_date,
        format="DD/MM/YYYY"
    )

if end_date <= start_date:
    st.error("Ngày rút tiền phải lớn hơn ngày gửi tiền.")
    st.stop()


# ============================================================
# 6. XÁC ĐỊNH TRẠNG THÁI TIỀN GỬI
# ============================================================

total_days = (end_date - start_date).days

is_early_withdrawal = end_date < maturity_date
is_on_maturity = end_date == maturity_date
is_after_maturity = end_date > maturity_date

st.subheader("4️⃣ Thông tin kỳ hạn")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Ngày gửi", start_date.strftime("%d/%m/%Y"))
c2.metric("Ngày đáo hạn kỳ đầu", maturity_date.strftime("%d/%m/%Y"))
c3.metric("Ngày rút", end_date.strftime("%d/%m/%Y"))
c4.metric("Số ngày thực tế", f"{total_days} ngày")

if is_early_withdrawal:
    st.error(
        f"🚨 RÚT TRƯỚC HẠN. Ngày đáo hạn là "
        f"{maturity_date:%d/%m/%Y}. "
        f"Áp dụng lãi suất không kỳ hạn "
        f"{non_term_rate_percent:.2f}%/"
        f"{'năm' if non_term_rate_unit == 'Năm' else 'tháng'}."
    )

elif is_on_maturity:
    st.success(
        "✅ Rút đúng ngày đáo hạn kỳ đầu. "
        "Khách hàng được hưởng lãi suất có kỳ hạn."
    )

else:
    st.warning(
        "⚠️ Ngày rút sau ngày đáo hạn. "
        "Các kỳ đã hoàn tất được tính lãi có kỳ hạn và nhập lãi vào gốc khi tái tục. "
        "Kỳ cuối chưa hoàn tất được tính theo lãi suất không kỳ hạn."
    )


# ============================================================
# 7. LÃI SUẤT THỰC TẾ ÁP DỤNG
# ============================================================

if is_early_withdrawal:
    actual_rate = non_term_rate
    actual_rate_percent = non_term_rate_percent
    actual_rate_unit = non_term_rate_unit
    rate_display = "Lãi suất không kỳ hạn"
else:
    actual_rate = annual_rate
    actual_rate_percent = annual_rate_percent
    actual_rate_unit = term_rate_unit
    rate_display = "Lãi suất có kỳ hạn"

rate_label = (
    "%/năm" if actual_rate_unit == "Năm" else "%/tháng"
)

st.subheader("5️⃣ Lãi suất áp dụng")

r1, r2, r3 = st.columns(3)

r1.metric(
    "Lãi suất có kỳ hạn",
    f"{annual_rate_percent:.2f}%/"
    f"{'năm' if term_rate_unit == 'Năm' else 'tháng'}"
)

r2.metric(
    "Lãi suất không kỳ hạn",
    f"{non_term_rate_percent:.2f}%/"
    f"{'năm' if non_term_rate_unit == 'Năm' else 'tháng'}"
)

r3.metric(
    "Lãi suất thực tế",
    f"{actual_rate_percent:.2f}{rate_label}"
)

st.info(
    f"Đang áp dụng: **{rate_display} — "
    f"{actual_rate_percent:.2f}{rate_label}**. "
    f"Mẫu số tính lãi: **{get_denominator(actual_rate_unit)} ngày**."
)


# ============================================================
# 8. NÚT TÍNH TIỀN
# ============================================================

st.divider()

calculate_button = st.button(
    "🧮 TÍNH TIỀN LÃI",
    type="primary",
    use_container_width=True
)


# ============================================================
# 9. TÍNH TOÁN VÀ HIỂN THỊ KẾT QUẢ
# ============================================================

if calculate_button:

    interest_reclaimed = 0.0
    payout_rows = []
    rollover_results = []
    monthly_results = []
    rollover_used = False

    # --------------------------------------------------------
    # A. RÚT TRƯỚC HẠN
    # --------------------------------------------------------

    if is_early_withdrawal:

        actual_interest_type = "Lãi đơn"

        total_interest, monthly_results = calculate_simple_interest(
            principal,
            non_term_rate,
            start_date,
            end_date,
            non_term_rate_unit
        )

        if interest_payment == "Hàng tháng":
            # Thu hồi lãi có kỳ hạn đã thực trả theo các kỳ tháng
            # mà ngày nhận lãi không vượt quá ngày khách hàng rút.
            interest_reclaimed, payout_rows = (
                calculate_monthly_payout_reclaimed(
                    principal,
                    annual_rate,
                    start_date,
                    end_date,
                    term_rate_unit,
                    int(term_months)
                )
            )

        elif interest_payment == "Đầu kỳ":
            # Lãi đầu kỳ được trả trước cho TOÀN BỘ kỳ hạn đăng ký.
            # Khi rút trước hạn, thu hồi toàn bộ khoản lãi đã trả trước.
            full_term_days = (maturity_date - start_date).days
            interest_reclaimed = calculate_interest(
                principal,
                annual_rate,
                full_term_days,
                term_rate_unit
            )
            payout_rows = [{
                "Lần nhận lãi": 1,
                "Từ ngày": start_date.strftime("%d/%m/%Y"),
                "Ngày nhận lãi": start_date.strftime("%d/%m/%Y"),
                "Số ngày": full_term_days,
                "Lãi có kỳ hạn bị thu hồi": interest_reclaimed
            }]

        final_amount = (
            principal - interest_reclaimed + total_interest
        )

        status_note = "Rút trước hạn - áp dụng lãi không kỳ hạn"

    # --------------------------------------------------------
    # B. CUỐI KỲ - TỰ ĐỘNG TÁI TỤC
    # --------------------------------------------------------

    elif interest_payment == "Cuối kỳ" and is_after_maturity:

        rollover_used = True

        # Theo yêu cầu: mỗi kỳ hoàn tất, toàn bộ lãi kỳ đó
        # được nhập vào vốn gốc khi tái tục.
        # Kỳ cuối chưa hoàn tất chỉ tính lãi trên gốc hiện tại.
        total_interest, rollover_results, final_amount = (
            calculate_rollover(
                principal,
                annual_rate,
                start_date,
                end_date,
                int(term_months),
                term_rate_unit,
                non_term_rate,
                non_term_rate_unit
            )
        )

        monthly_results = []
        actual_interest_type = "Tái tục theo kỳ; kỳ lẻ tính lãi không kỳ hạn"
        status_note = (
            "Các kỳ hoàn tất áp dụng lãi có kỳ hạn và nhập lãi vào gốc; "
            "kỳ chưa hoàn tất áp dụng lãi không kỳ hạn"
        )

    # --------------------------------------------------------
    # C. KHÔNG RÚT TRƯỚC HẠN, CHƯA CÓ TÁI TỤC
    # --------------------------------------------------------

    else:

        if interest_payment == "Cuối kỳ" and interest_type == "Lãi kép":

            total_interest, monthly_results, final_amount = (
                calculate_compound_interest(
                    principal,
                    annual_rate,
                    start_date,
                    end_date,
                    term_rate_unit
                )
            )

            actual_interest_type = "Lãi kép"
        else:
            total_interest, monthly_results = calculate_simple_interest(
                principal,
                annual_rate,
                start_date,
                end_date,
                term_rate_unit
            )

            actual_interest_type = "Lãi đơn"

            if interest_payment == "Đầu kỳ":
                # Tiền lãi đầu kỳ trả ngay; số tiền gốc nhận lại
                # khi rút vẫn bằng gốc ban đầu.
                final_amount = principal
            else:
                final_amount = principal + total_interest

        status_note = "Áp dụng lãi suất có kỳ hạn"

    # --------------------------------------------------------
    # D. KẾT QUẢ TỔNG QUAN
    # --------------------------------------------------------

    st.divider()
    st.subheader("6️⃣ KẾT QUẢ TÍNH TIỀN")

    if is_early_withdrawal and interest_payment in ["Hàng tháng", "Đầu kỳ"]:
        result1, result2, result3, result4 = st.columns(4)

        result1.metric("Gốc ban đầu", format_money(principal))
        result2.metric("Lãi có kỳ hạn thu hồi", format_money(interest_reclaimed))
        result3.metric("Lãi không kỳ hạn", format_money(total_interest))
        result4.metric("Tiền thực nhận", format_money(final_amount))

        if interest_payment == "Đầu kỳ":
            st.warning(
                "Rút trước hạn với hình thức nhận lãi đầu kỳ: toàn bộ lãi "
                "có kỳ hạn đã trả trước cho cả kỳ hạn đăng ký được thu hồi. "
                "Khách hàng chỉ được hưởng lãi không kỳ hạn tính lại."
            )

    elif interest_payment == "Đầu kỳ" and not is_early_withdrawal:
        result1, result2, result3 = st.columns(3)

        result1.metric("Gốc nhận khi rút", format_money(final_amount))
        result2.metric("Lãi đã nhận đầu kỳ", format_money(total_interest))
        result3.metric(
            "Tổng lợi ích gốc + lãi",
            format_money(final_amount + total_interest)
        )

    else:
        result1, result2, result3 = st.columns(3)

        result1.metric("Gốc ban đầu", format_money(principal))
        result2.metric("Tổng lãi tính trong thời gian gửi", format_money(total_interest))
        result3.metric("Tổng tiền nhận khi rút", format_money(final_amount))

    # --------------------------------------------------------
    # E. THÔNG TIN CHI TIẾT
    # --------------------------------------------------------

    st.subheader("7️⃣ Thông tin khoản tiền gửi")

    st.markdown(
        f"""
- **Số tiền gửi ban đầu:** {format_money(principal)}
- **Kỳ hạn đăng ký:** {term_months} tháng
- **Ngày gửi:** {start_date:%d/%m/%Y}
- **Ngày đáo hạn kỳ đầu:** {maturity_date:%d/%m/%Y}
- **Ngày rút:** {end_date:%d/%m/%Y}
- **Số ngày gửi thực tế:** {total_days} ngày
- **Hình thức nhận lãi:** {interest_payment}
- **Phương pháp tính lãi:** {actual_interest_type}
- **Lãi suất có kỳ hạn:** {annual_rate_percent:.2f}%/{'năm' if term_rate_unit == 'Năm' else 'tháng'}
- **Lãi suất không kỳ hạn:** {non_term_rate_percent:.2f}%/{'năm' if non_term_rate_unit == 'Năm' else 'tháng'}
- **Trạng thái:** {status_note}
"""
    )

    if is_early_withdrawal:
        st.markdown(
            f"""
- **Lãi không kỳ hạn tính lại:** {format_money(total_interest)}
- **Lãi có kỳ hạn đã thu hồi:** {format_money(interest_reclaimed)}
- **Công thức tiền thực nhận:** {format_money(principal)} - {format_money(interest_reclaimed)} + {format_money(total_interest)} = {format_money(final_amount)}
"""
        )

    if rollover_used:
        st.info(
            "Các kỳ đã hoàn tất được tính theo lãi suất có kỳ hạn và nhập lãi vào gốc. "
            "Kỳ cuối chưa hoàn tất được tính theo lãi suất không kỳ hạn trên số gốc "
            "đã tích lũy từ các kỳ trước."
        )

    # --------------------------------------------------------
    # F. BẢNG CHI TIẾT TÁI TỤC
    # --------------------------------------------------------

    if rollover_used and rollover_results:
        st.subheader("8️⃣ Chi tiết từng kỳ tái tục")

        display_rollover = []

        for row in rollover_results:
            display_rollover.append({
                "Kỳ": row["Kỳ tái tục"],
                "Từ ngày": row["Từ ngày"],
                "Đến trước ngày": row["Đến trước ngày"],
                "Số ngày": row["Số ngày"],
                "Trạng thái": row["Trạng thái kỳ"],
                "Lãi suất áp dụng": row["Lãi suất áp dụng"],
                "Gốc đầu kỳ": format_money(row["Gốc đầu kỳ"]),
                "Lãi kỳ": format_money(row["Lãi kỳ"]),
                "Gốc + lãi cuối kỳ": format_money(row["Gốc + lãi cuối kỳ"])
            })

        st.dataframe(
            pd.DataFrame(display_rollover),
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # G. CHI TIẾT LÃI HÀNG THÁNG
    # --------------------------------------------------------

    elif monthly_results:
        st.subheader("8️⃣ Chi tiết tiền lãi theo tháng")

        display_data = []

        for row in monthly_results:
            item = {
                "Tháng": row["Tháng"],
                "Từ ngày": row["Từ ngày"],
                "Đến trước ngày": row["Đến trước ngày"],
                "Số ngày": row["Số ngày"]
            }

            if "Tiền gốc đầu kỳ" in row:
                item["Gốc đầu kỳ"] = format_money(row["Tiền gốc đầu kỳ"])
                item["Tiền lãi"] = format_money(row["Tiền lãi"])
                item["Gốc + lãi cuối kỳ"] = format_money(
                    row["Gốc + lãi cuối kỳ"]
                )
            else:
                item["Tiền gốc"] = format_money(row["Tiền gốc"])
                item["Tiền lãi"] = format_money(row["Tiền lãi"])

            display_data.append(item)

        st.dataframe(
            pd.DataFrame(display_data),
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # H. CHI TIẾT LÃI BỊ THU HỒI
    # --------------------------------------------------------

    if payout_rows:
        st.subheader("9️⃣ Đối soát lãi có kỳ hạn đã trả")

        display_payout = []

        for row in payout_rows:
            display_payout.append({
                "Lần nhận lãi": row["Lần nhận lãi"],
                "Từ ngày": row["Từ ngày"],
                "Ngày nhận lãi": row["Ngày nhận lãi"],
                "Số ngày": row["Số ngày"],
                "Lãi bị thu hồi": format_money(
                    row["Lãi có kỳ hạn bị thu hồi"]
                )
            })

        st.dataframe(
            pd.DataFrame(display_payout),
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # I. CÔNG THỨC TÍNH
    # --------------------------------------------------------

    with st.expander("📐 Xem công thức tính lãi"):

        st.markdown(
            f"""
### 1. Lãi suất tính theo năm

**Tiền lãi = Tiền gốc × Lãi suất năm × Số ngày / 365**

Ví dụ: 100.000.000 VNĐ, lãi suất 6%/năm, gửi 30 ngày.

Lãi = 100.000.000 × 6% × 30 / 365.

### 2. Lãi suất tính theo tháng

**Tiền lãi = Tiền gốc × Lãi suất tháng × Số ngày / 30**

Ví dụ: 100.000.000 VNĐ, lãi suất 0,5%/tháng, gửi 30 ngày.

Lãi = 100.000.000 × 0,5% × 30 / 30.

### 3. Rút trước hạn

**Lãi không kỳ hạn = Gốc × Lãi suất không kỳ hạn × Số ngày / mẫu số**

Mẫu số là 365 nếu chọn lãi suất năm và 30 nếu chọn lãi suất tháng.

Nếu nhận lãi hàng tháng, tiền thực nhận được tính:

**Tiền thực nhận = Gốc - Lãi có kỳ hạn bị thu hồi + Lãi không kỳ hạn tính lại.**

Nếu nhận lãi đầu kỳ và rút trước hạn, thu hồi toàn bộ lãi có kỳ hạn đã trả trước cho cả kỳ hạn đăng ký:

**Tiền thực nhận = Gốc - Toàn bộ lãi đầu kỳ đã nhận + Lãi không kỳ hạn tính lại.**

### 4. Tự động tái tục khi nhận lãi cuối kỳ

Với mỗi kỳ hạn đã hoàn tất:

**Lãi kỳ = Gốc đầu kỳ × Lãi suất có kỳ hạn × Số ngày / mẫu số**

**Gốc kỳ tiếp theo = Gốc đầu kỳ + Lãi kỳ**

Kỳ hạn tiếp theo bằng đúng kỳ hạn ban đầu ({term_months} tháng).

Nếu rút sau ngày đáo hạn nhưng kỳ cuối chưa hoàn tất:

**Lãi kỳ chưa hoàn tất = Gốc đã tích lũy × Lãi suất không kỳ hạn × Số ngày / mẫu số**

Kỳ chưa hoàn tất không được nhập lãi có kỳ hạn; chỉ áp dụng lãi suất không kỳ hạn cho phần thời gian này.

### 5. Quy tắc ngày

Ngày gửi được tính lãi; ngày rút không tính lãi.

Ngày đáo hạn kỳ đầu: **{maturity_date:%d/%m/%Y}**.

Ngày rút vượt ngày đáo hạn sẽ được xử lý theo quy tắc tái tục nêu trên.
"""
        )


# ============================================================
# 10. FOOTER
# ============================================================

st.divider()

st.caption(
    "💰 Ứng dụng tính lãi tiền gửi tiết kiệm | "
    "Lãi suất năm chia 365 ngày, lãi suất tháng chia 30 ngày | "
    "Ngày gửi tính lãi, ngày rút không tính lãi"
)
