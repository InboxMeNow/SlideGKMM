import os
import sys
import io
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
import pypdf

# 1. Colors matching Beamer UET theme
uetblue = colors.HexColor('#12375C')
uetdarkblue = colors.HexColor('#0C2642')
uetcyan = colors.HexColor('#4A6B8A')
uetgreen = colors.HexColor('#2E6C61')
uetdarkgreen = colors.HexColor('#22544B')
uetgreenbg = colors.HexColor('#F1F6F5')
uetdark = colors.HexColor('#262E38')
uetgray = colors.HexColor('#64707D')
uetlightgray = colors.HexColor('#F6F7F9')
uetborder = colors.HexColor('#D4DCE4')
uetaccentbg = colors.HexColor('#F0F4F8')
uetred = colors.HexColor('#9E343E')
white = colors.HexColor('#FFFFFF')

# 2. Register TTF fonts
pdfmetrics.registerFont(TTFont('SegoeUI', r'C:\Windows\Fonts\segoeui.ttf'))
pdfmetrics.registerFont(TTFont('SegoeUI-Bold', r'C:\Windows\Fonts\segoeuib.ttf'))
pdfmetrics.registerFont(TTFont('SegoeUI-Italic', r'C:\Windows\Fonts\segoeuii.ttf'))
pdfmetrics.registerFont(TTFont('SegoeUISymbol', r'C:\Windows\Fonts\seguisym.ttf'))
pdfmetrics.registerFont(TTFont('Consolas', r'C:\Windows\Fonts\consola.ttf'))
pdfmetrics.registerFont(TTFont('Consolas-Bold', r'C:\Windows\Fonts\consolab.ttf'))

PW = 453.543
PH = 255.118

SYM_CHARS = set(['✓', '✗', '⟷', '⟶', '→', '•', '−', '×', '–', '—', '≤', '≥', '≠', '≈'])

def draw_mixed_string(c, x, y, text, default_font='SegoeUI', font_size=10, color=None, align='left'):
    if color:
        c.setFillColor(color)
        
    runs = []
    chunk = ''
    is_sym = False
    for ch in text:
        ch_sym = ch in SYM_CHARS
        if ch_sym != is_sym:
            if chunk:
                fn = 'SegoeUISymbol' if is_sym else default_font
                runs.append((chunk, fn))
            chunk = ch
            is_sym = ch_sym
        else:
            chunk += ch
    if chunk:
        fn = 'SegoeUISymbol' if is_sym else default_font
        runs.append((chunk, fn))
        
    total_w = sum(c.stringWidth(txt, fn, font_size) for txt, fn in runs)
    
    cur_x = x
    if align == 'center':
        cur_x = x - total_w / 2.0
    elif align == 'right':
        cur_x = x - total_w
        
    for txt, fn in runs:
        c.setFont(fn, font_size)
        c.drawString(cur_x, y, txt)
        cur_x += c.stringWidth(txt, fn, font_size)
    return total_w

def draw_header_footer(c, title, current_slide, total_slides=36, section_head="10. Mật Mã Hậu Lượng Tử (PQ-TLS)"):
    # Header Title
    f_size = 11.0
    if len(title) > 38:
        f_size = 9.8
    c.setFont('SegoeUI-Bold', f_size)
    c.setFillColor(uetblue)
    c.drawString(22.68, PH - 21.0, title)
    
    # Section head
    c.setFont('SegoeUI-Bold', 5.6)
    c.setFillColor(uetgray)
    c.drawRightString(PW - 22.68, PH - 19.5, section_head)
    
    # Header Accent Rules
    c.setLineWidth(0.6)
    c.setStrokeColor(uetborder)
    c.line(22.68, PH - 26.5, PW - 22.68, PH - 26.5)
    
    c.setLineWidth(1.8)
    c.setStrokeColor(uetblue)
    c.line(22.68, PH - 26.5, 22.68 + 73.7, PH - 26.5)
    
    # Footer separator line
    c.setLineWidth(0.5)
    c.setStrokeColor(uetborder)
    c.line(0, 13.0, PW, 13.0)
    
    # Logo
    logo_path = r'assets\uet_logo.png'
    if os.path.exists(logo_path):
        c.drawImage(logo_path, 22.68, 2.0, height=9.5, preserveAspectRatio=True, mask='auto')
    
    # University name
    c.setFont('SegoeUI-Bold', 6.8)
    c.setFillColor(uetblue)
    c.drawString(35.5, 4.2, "Trường Đại học Công nghệ – Đại học Quốc gia Hà Nội")
    
    # Short topic
    c.setFont('SegoeUI', 6.0)
    c.setFillColor(uetgray)
    c.drawRightString(423.0, 4.2, "Kiến trúc & Bảo mật SSL/TLS")
    
    # Badge
    badge_x = 428.0
    badge_y = 1.3
    badge_w = 24.5
    badge_h = 9.8
    c.setFillColor(uetlightgray)
    c.setStrokeColor(uetborder)
    c.setLineWidth(0.6)
    c.rect(badge_x, badge_y, badge_w, badge_h, fill=1, stroke=1)
    
    c.setFont('SegoeUI-Bold', 5.8)
    c.setFillColor(uetblue)
    badge_txt = f"{current_slide} / {total_slides}"
    c.drawCentredString(badge_x + badge_w / 2.0, badge_y + 2.5, badge_txt)

def draw_accentcard(c, x, y, w, h, title, color=uetblue, title_size=7.6):
    c.setFillColor(white)
    c.setStrokeColor(uetborder)
    c.setLineWidth(0.6)
    c.rect(x, y, w, h, fill=1, stroke=1)
    
    c.setFillColor(color)
    c.rect(x, y, 2.8, h, fill=1, stroke=0)
    
    c.setFont('SegoeUI-Bold', title_size)
    c.setFillColor(color)
    c.drawString(x + 6.0, y + h - 11.5, title)

def draw_bullet_text(c, x, y, max_w, parts, font_size=6.0, line_spacing=7.8):
    """parts is list of (text, is_bold, is_code, color)"""
    cur_y = y
    space_w = c.stringWidth(' ', 'SegoeUI', font_size)
    
    words = []
    for text, is_bold, is_code, col in parts:
        f_name = 'Consolas-Bold' if (is_code and is_bold) else ('Consolas' if is_code else ('SegoeUI-Bold' if is_bold else 'SegoeUI'))
        f_size = font_size - 0.4 if is_code else font_size
        col = col if col else (uetdark if not is_bold else colors.HexColor('#000000'))
        
        raw_tokens = text.split(' ')
        for i, tok in enumerate(raw_tokens):
            if tok:
                has_space = (i < len(raw_tokens) - 1) or text.endswith(' ')
                words.append((tok, f_name, f_size, col, has_space))
            elif i < len(raw_tokens) - 1 and words:
                prev = words[-1]
                words[-1] = (prev[0], prev[1], prev[2], prev[3], True)
    
    line_words = []
    line_w = 0.0
    lines = []
    
    def get_token_w(tok, fn, fs):
        w = 0.0
        for ch in tok:
            f = 'SegoeUISymbol' if ch in SYM_CHARS else fn
            w += c.stringWidth(ch, f, fs)
        return w
    
    for tok, f_name, f_size, col, has_space in words:
        w = get_token_w(tok, f_name, f_size)
        w_with_space = w + (space_w if has_space else 0)
        
        if line_w + w > max_w and line_words:
            lines.append(line_words)
            line_words = [(tok, f_name, f_size, col, has_space)]
            line_w = w_with_space
        else:
            line_words.append((tok, f_name, f_size, col, has_space))
            line_w += w_with_space
    if line_words:
        lines.append(line_words)
    
    for l in lines:
        lx = x
        for tok, f_name, f_size, col, has_space in l:
            c.setFillColor(col)
            for ch in tok:
                fn = 'SegoeUISymbol' if ch in SYM_CHARS else f_name
                c.setFont(fn, f_size)
                c.drawString(lx, cur_y, ch)
                lx += c.stringWidth(ch, fn, f_size)
            if has_space:
                lx += space_w
        cur_y -= line_spacing
    return cur_y

def draw_pqc_slides(output_path):
    c = canvas.Canvas(output_path, pagesize=(PW, PH))
    
    # =========================================================================
    # SLIDE 29 (trang_29.md)
    # Header: # Nguy Cơ Lượng Tử Với TLS
    # ## Tác Động Của Thuật Toán Lượng Tử Trên TLS (Shor vs. Grover)
    # =========================================================================
    draw_header_footer(c, "Nguy Cơ Lượng Tử Với TLS", 29)
    
    draw_accentcard(c, 22.68, 62.0, 408.18, 158.0, "Tác Động Của Thuật Toán Lượng Tử Trên TLS (Shor vs. Grover)", uetblue, 8.0)
    
    # Verbatim headers from trang_29.md:
    # | Thành phần mật mã trong TLS | Thuật toán cổ điển | Thuật toán lượng tử đe dọa | Mức độ tác động |
    col_x = [28.0, 114.0, 172.0, 260.0]
    col_w = [82.0, 54.0, 84.0, 165.0]
    
    ty = 191.0
    c.setFillColor(uetaccentbg)
    c.rect(26.0, ty - 3.0, 401.5, 13.0, fill=1, stroke=0)
    c.setFont('SegoeUI-Bold', 5.5)
    c.setFillColor(uetblue)
    c.drawString(col_x[0], ty, "Thành phần mật mã trong TLS")
    c.drawString(col_x[1], ty, "Thuật toán cổ điển")
    c.drawString(col_x[2], ty, "Thuật toán lượng tử đe dọa")
    c.drawString(col_x[3], ty, "Mức độ tác động")
    
    rows_s29 = [
        (
            [("Trao đổi khóa", True, False, uetdark)],
            [("(EC)DHE, DH", False, True, uetblue)],
            [("Thuật toán Shor", True, False, uetred), (" (Phá logarit rời rạc)", False, False, uetgray)],
            [("Bị phá vỡ hoàn toàn → ", True, False, uetred), ("Kẻ tấn công thu thập dữ liệu hôm nay để giải mã tương lai (Store now, decrypt later).", False, False, uetdark)],
            29.0,
            white
        ),
        (
            [("Chữ ký số", True, False, uetdark)],
            [("RSA, ECDSA,\nEd25519", False, True, uetblue)],
            [("Thuật toán Shor", True, False, uetred), (" (Phá phân tích số nguyên & ECC)", False, False, uetgray)],
            [("Bị phá vỡ hoàn toàn → ", True, False, uetred), ("Nguy cơ giả mạo chữ ký và danh tính CA/Server.", False, False, uetdark)],
            28.0,
            uetlightgray
        ),
        (
            [("Mã hóa đối xứng", True, False, uetdark)],
            [("AES-128, AES-256,\nChaCha20", False, True, uetblue)],
            [("Thuật toán Grover", True, False, uetblue), (" (Tìm kiếm lượng tử)", False, False, uetgray)],
            [("Bị suy giảm độ an toàn: O(2ⁿ) → O(2ⁿ/²). ", True, False, uetblue), ("Chỉ cần nâng chiều dài khóa lên 256-bit (AES-256).", False, False, uetdark)],
            28.0,
            white
        ),
        (
            [("Hàm băm & MAC", True, False, uetdark)],
            [("SHA-256, SHA-384,\nHMAC", False, True, uetblue)],
            [("Thuật toán Grover", True, False, uetblue), (" (Tìm nghịch ảnh)", False, False, uetgray)],
            [("Ảnh hưởng nhẹ / Vẫn an toàn thực tế: ", True, False, uetdarkgreen), ("Khó bị khai thác do chi phí tính toán cao. Chỉ cần nâng kích thước băm (SHA-384).", False, False, uetdark)],
            28.0,
            uetlightgray
        )
    ]
    
    cur_y = 184.0
    for c1, c2, c3, c4, rh, bg_c in rows_s29:
        if bg_c != white:
            c.setFillColor(bg_c)
            c.rect(26.0, cur_y - rh + 1.0, 401.5, rh, fill=1, stroke=0)
        c.setLineWidth(0.4)
        c.setStrokeColor(uetborder)
        c.line(26.0, cur_y + 1.0, 427.5, cur_y + 1.0)
        
        draw_bullet_text(c, col_x[0], cur_y - 7.0, col_w[0] - 4.0, c1, font_size=5.4, line_spacing=6.8)
        draw_bullet_text(c, col_x[1], cur_y - 7.0, col_w[1] - 4.0, c2, font_size=5.2, line_spacing=6.6)
        draw_bullet_text(c, col_x[2], cur_y - 7.0, col_w[2] - 4.0, c3, font_size=5.4, line_spacing=6.8)
        draw_bullet_text(c, col_x[3], cur_y - 7.0, col_w[3] - 4.0, c4, font_size=5.3, line_spacing=6.8)
        cur_y -= rh
        
    c.line(26.0, cur_y + 1.0, 427.5, cur_y + 1.0)
    
    # Bottom Card: Kết luận verbatim from trang_29.md
    c.setFillColor(uetaccentbg)
    c.setStrokeColor(uetborder)
    c.setLineWidth(0.6)
    c.rect(22.68, 20.0, 408.18, 36.0, fill=1, stroke=1)
    
    c.setFont('SegoeUI-Bold', 6.5)
    c.setFillColor(uetblue)
    c.drawString(29.0, 44.0, "Kết luận:")
    c.setFont('SegoeUI', 6.2)
    c.setFillColor(uetdark)
    c.drawString(62.0, 44.0, "Trọng tâm là handshake: trao đổi khóa và chữ ký.")
    c.drawString(29.0, 31.0, "Record protocol chỉ cần chỉnh tham số.")
    
    c.showPage()
    
    # =========================================================================
    # SLIDE 30 (trang_30.md)
    # Header: # Định Nghĩa Post-Quantum Cryptography (PQC)
    # Verbatim content ONLY from trang_30.md
    # =========================================================================
    draw_header_footer(c, "Định Nghĩa Post-Quantum Cryptography (PQC)", 30)
    
    # Top Card: Post-Quantum Cryptography (PQC) definition verbatim
    draw_accentcard(c, 22.68, 142.0, 408.18, 78.0, "Định Nghĩa Post-Quantum Cryptography (PQC)", uetblue, 8.0)
    s30_def = [
        ("• ", True, False, uetblue),
        ("Post-Quantum Cryptography (PQC): ", True, False, uetblue),
        ("là nhóm thuật toán mật mã được thiết kế dựa trên các bài toán toán học được tin rằng vẫn khó giải đối với cả máy tính cổ điển và máy tính lượng tử quy mô lớn.", False, False, uetdark)
    ]
    draw_bullet_text(c, 30.0, 185.0, 390.0, s30_def, font_size=6.8, line_spacing=10.0)
    
    # Bottom Card: ## Ba Hướng Giải Pháp PQC Cho TLS verbatim
    draw_accentcard(c, 22.68, 20.0, 408.18, 114.0, "Ba Hướng Giải Pháp PQC Cho TLS", uetgreen, 8.0)
    
    s30_directions = [
        [
            ("• ", True, False, uetblue),
            ("Hướng 1: PQ Authentication: ", True, False, uetblue),
            ("Thay chữ ký cổ điển bằng chữ ký hậu lượng tử (", False, False, uetdark),
            ("ML-DSA", False, True, uetblue),
            ("/", False, False, uetdark),
            ("SLH-DSA", False, True, uetblue),
            (") để xác thực.", False, False, uetdark)
        ],
        [
            ("• ", True, False, uetblue),
            ("Hướng 2: PQ Key Exchange: ", True, False, uetblue),
            ("Thay trao đổi khóa truyền thống (", False, False, uetdark),
            ("DH/ECDH", False, True, uetblue),
            (") bằng cơ chế ", False, False, uetdark),
            ("KEM", True, True, uetblue),
            (" hậu lượng tử (", False, False, uetdark),
            ("ML-KEM", False, True, uetblue),
            (").", False, False, uetdark)
        ],
        [
            ("• ", True, False, uetdarkgreen),
            ("Hướng 3: PQ-AKE: ", True, False, uetdarkgreen),
            ("Kết hợp trao đổi khóa và xác thực hậu lượng tử trong cùng một thiết kế (", False, False, uetdark),
            ("KEMTLS", True, True, uetdarkgreen),
            (").", False, False, uetdark)
        ]
    ]
    
    by = 104.0
    for b in s30_directions:
        by = draw_bullet_text(c, 30.0, by, 390.0, b, font_size=6.5, line_spacing=8.8)
        by -= 4.0
        
    # Note at bottom verbatim: **Mỗi loại lại chia thuần hậu lượng tử (pure) và lai (hybrid: cổ điển + hậu lượng tử).**
    c.setFillColor(uetaccentbg)
    c.setStrokeColor(uetborder)
    c.setLineWidth(0.5)
    c.rect(30.0, 28.0, 393.5, 18.0, fill=1, stroke=1)
    c.setFont('SegoeUI-Bold', 6.0)
    c.setFillColor(uetblue)
    c.drawCentredString(226.77, 34.0, "Mỗi loại lại chia thuần hậu lượng tử (pure) và lai (hybrid: cổ điển + hậu lượng tử).")
    
    c.showPage()
    
    # =========================================================================
    # SLIDE 31 (trang_31.md)
    # Header: # Hướng 1: Post-Quantum Authentication
    # Verbatim content ONLY from trang_31.md
    # =========================================================================
    draw_header_footer(c, "Hướng 1: Post-Quantum Authentication", 31)
    
    card_w = 199.5
    card_h = 200.0
    
    # Left Card: ### Các thuật toán thuần PQ
    draw_accentcard(c, 22.68, 20.0, card_w, card_h, "Các Thuật Toán Thuần PQ", uetblue, 7.8)
    
    s31_left_bullets = [
        [("• Hai vị trí dùng chữ ký số trong TLS:", True, False, uetdark)],
        [("   1. Chữ ký của CA trên chứng chỉ.", False, False, uetdark)],
        [("   2. Chữ ký ", False, False, uetdark), ("CertificateVerify", False, True, uetblue), (" trong Handshake.", False, False, uetdark)],
        [("• Thách thức: ", True, False, uetdark), ("Cân bằng an toàn và hiệu năng, đặc biệt là kích thước khóa và chữ ký.", False, False, uetdark)],
    ]
    by = 194.0
    for b in s31_left_bullets:
        by = draw_bullet_text(c, 28.0, by, card_w - 12.0, b, font_size=5.8, line_spacing=7.4)
        by -= 2.0
        
    # Subtitle: Bảng so sánh các thuật toán chữ ký số hậu lượng tử
    c.setFont('SegoeUI-Bold', 5.8)
    c.setFillColor(uetblue)
    c.drawString(28.0, 138.0, "Bảng so sánh các thuật toán chữ ký số hậu lượng tử")
    
    ty = 124.0
    c.setFillColor(uetaccentbg)
    c.rect(28.0, ty - 3.0, 187.5, 11.0, fill=1, stroke=0)
    c.setFont('SegoeUI-Bold', 5.2)
    c.setFillColor(uetblue)
    c.drawString(30.0, ty, "Thuật toán")
    c.drawString(88.0, ty, "PK (Byte)")
    c.drawString(124.0, ty, "Chữ ký (Byte)")
    c.drawString(172.0, ty, "Hệ số chậm")
    
    sig_rows = [
        ("Falcon (L1)", "897", "666", "0,98×", white),
        ("Dilithium (L2)", "1 312", "2 420", "1,02×", uetlightgray),
        ("SPHINCS+ (L1)", "32", "7 856", "1,58×", white)
    ]
    cur_y = 114.0
    for a_name, pk, sig, slow, bg_col in sig_rows:
        if bg_col != white:
            c.setFillColor(bg_col)
            c.rect(28.0, cur_y - 8.0, 187.5, 10.5, fill=1, stroke=0)
        c.setLineWidth(0.4)
        c.setStrokeColor(uetborder)
        c.line(28.0, cur_y + 2.5, 215.5, cur_y + 2.5)
        
        c.setFont('SegoeUI-Bold' if a_name.startswith('Dilithium') else 'SegoeUI', 5.2)
        c.setFillColor(uetdarkgreen if slow.startswith('0,98') else (uetdark if not slow.startswith('1,58') else uetred))
        c.drawString(30.0, cur_y - 4.5, a_name)
        c.drawString(92.0, cur_y - 4.5, pk)
        c.drawString(128.0, cur_y - 4.5, sig)
        c.drawString(178.0, cur_y - 4.5, slow)
        cur_y -= 10.5
    c.line(28.0, cur_y + 2.5, 215.5, cur_y + 2.5)
    
    # Note verbatim from trang_31.md:
    c.setFont('SegoeUI-Italic', 4.5)
    c.setFillColor(uetgray)
    c.drawString(28.0, 70.0, "*Nguồn [14] (Phụ lục A, bảng 4–6): Hệ số = kết nối/giây(Ed25519) ÷ kết")
    c.drawString(28.0, 62.0, "nối/giây(thuật toán ký); lớn hơn 1 là chậm hơn Ed25519 (OQS-OpenSSL).")
    
    # Right Card: Nhận xét & Các thuật toán lai verbatim from trang_31.md
    draw_accentcard(c, 231.36, 20.0, card_w, card_h, "Đánh Giá & Thuật Toán Lai", uetgreen, 7.8)
    
    # Box 1: Nhận xét verbatim from trang_31.md
    c.setFillColor(uetaccentbg)
    c.setStrokeColor(uetborder)
    c.setLineWidth(0.5)
    c.rect(237.0, 108.0, 188.0, 92.0, fill=1, stroke=1)
    
    c.setFont('SegoeUI-Bold', 6.2)
    c.setFillColor(uetblue)
    c.drawString(243.0, 187.0, "Nhận xét:")
    
    s31_eval = [
        [
            ("• ", True, False, uetdark),
            ("Nhận xét: ", True, False, uetdark),
            ("Dilithium ", True, True, uetblue),
            ("(ML-DSA / FIPS 204) ", True, False, uetblue),
            ("và ", False, False, uetdark),
            ("Falcon", True, False, uetdark),
            (" cân bằng tốt nhất; ", False, False, uetdark),
            ("SPHINCS+ ", True, True, uetblue),
            ("(SLH-DSA / FIPS 205) ", True, False, uetblue),
            ("có chữ ký lớn.", False, False, uetdark)
        ]
    ]
    draw_bullet_text(c, 243.0, 172.0, 176.0, s31_eval[0], font_size=5.8, line_spacing=8.0)
    
    # Box 2: ### Các thuật toán lai verbatim from trang_31.md
    c.setFillColor(uetgreenbg)
    c.setStrokeColor(uetborder)
    c.setLineWidth(0.5)
    c.rect(237.0, 28.0, 188.0, 72.0, fill=1, stroke=1)
    
    c.setFont('SegoeUI-Bold', 6.2)
    c.setFillColor(uetdarkgreen)
    c.drawString(243.0, 86.0, "Các thuật toán lai:")
    
    s31_hyb = [
        ("• ", True, False, uetdarkgreen),
        ("Hybrid authentication: ", True, False, uetdarkgreen),
        ("Ghép chữ ký cổ điển + hậu lượng tử; mức chậm thay đổi tùy cặp thuật toán kết hợp [14].", False, False, uetdark)
    ]
    draw_bullet_text(c, 243.0, 72.0, 176.0, s31_hyb, font_size=5.8, line_spacing=8.0)
    
    c.showPage()
    
    # =========================================================================
    # SLIDE 32 (trang_32.md)
    # Header: # Hướng 2: Post-Quantum Key Exchange  (RFC 10024)
    # Verbatim content ONLY from trang_32.md
    # =========================================================================
    draw_header_footer(c, "Hướng 2: Post-Quantum Key Exchange  (RFC 10024)", 32)
    
    # Left Card: ### Các thuật toán thuần PQ
    draw_accentcard(c, 22.68, 20.0, card_w, card_h, "Các Thuật Toán Thuần PQ (KEM)", uetblue, 7.8)
    
    s32_left_intro = [
        ("Chuyển từ Diffie-Hellman sang KEM (Key Encapsulation Mechanism).", False, False, uetdark)
    ]
    draw_bullet_text(c, 28.0, 192.0, card_w - 12.0, s32_left_intro, font_size=5.6, line_spacing=7.2)
    
    s32_flow = [
        ("• ", True, False, uetblue),
        ("Luồng gần giống DH: ", True, False, uetdark),
        ("client gửi khóa công khai tạm thời → server đóng gói ra (ciphertext, bí mật chung) và gửi ciphertext → client giải đóng gói lấy bí mật chung.", False, False, uetdark)
    ]
    draw_bullet_text(c, 28.0, 178.0, card_w - 12.0, s32_flow, font_size=5.3, line_spacing=6.7)
    
    # Table verbatim from trang_32.md:
    # | KEM (mức 1) | Khóa công khai (byte) | Ciphertext (byte) | Hệ số chậm đi* |
    ty = 138.0
    c.setFillColor(uetaccentbg)
    c.rect(28.0, ty - 3.0, 187.5, 11.0, fill=1, stroke=0)
    c.setFont('SegoeUI-Bold', 5.2)
    c.setFillColor(uetblue)
    c.drawString(30.0, ty, "KEM (mức 1)")
    c.drawString(78.0, ty, "Khóa công khai (byte)")
    c.drawString(136.0, ty, "Ciphertext (byte)")
    c.drawString(180.0, ty, "Hệ số chậm đi*")
    
    kem_rows = [
        ("Kyber", "800", "768", "1,06", uetgreenbg, uetdarkgreen),
        ("Saber", "672", "736", "1,07", white, uetdark),
        ("NTRU", "930", "930", "1,13", uetlightgray, uetdark),
        ("HQC", "2 249", "4 481", "1,23", white, uetdark),
        ("FrodoKEM", "9 616", "9 720", "2,53", uetlightgray, uetred),
        ("BIKE", "1 540", "1 572", "2,55", white, uetred)
    ]
    cur_y = 128.0
    for kname, pk, ct, sl, bg_col, txt_col in kem_rows:
        c.setFillColor(bg_col)
        c.rect(28.0, cur_y - 7.5, 187.5, 9.5, fill=1, stroke=0)
        c.setLineWidth(0.4)
        c.setStrokeColor(uetborder)
        c.line(28.0, cur_y + 2.0, 215.5, cur_y + 2.0)
        
        c.setFont('SegoeUI-Bold' if kname == 'Kyber' else 'SegoeUI', 5.0)
        c.setFillColor(txt_col)
        c.drawString(30.0, cur_y - 4.0, kname)
        c.drawString(88.0, cur_y - 4.0, pk)
        c.drawString(142.0, cur_y - 4.0, ct)
        c.drawString(186.0, cur_y - 4.0, sl)
        cur_y -= 9.5
    c.line(28.0, cur_y + 2.0, 215.5, cur_y + 2.0)
    
    # Note verbatim from trang_32.md:
    c.setFont('SegoeUI-Bold', 5.6)
    c.setFillColor(uetdarkgreen)
    c.drawString(28.0, 58.0, "Một thuật toán KEM tiêu biểu là Kyber (nhanh nhất)")
    
    # Right Card: ### Các thuật toán lai verbatim from trang_32.md
    draw_accentcard(c, 231.36, 20.0, card_w, card_h, "Các Thuật Toán Lai", uetgreen, 7.8)
    
    s32_hyb = [
        ("• ", True, False, uetdarkgreen),
        ("Hybrid key exchange: ", True, False, uetdarkgreen),
        ("ghép DH cổ điển + KEM hậu lượng tử, nối khóa/ciphertext thành một phần tử duy nhất– đã được triển khai và thử nghiệm nhiều nhất (ví dụ: ", False, False, uetdark),
        ("x25519 + Kyber", True, False, uetdarkgreen),
        (").", False, False, uetdark)
    ]
    draw_bullet_text(c, 237.0, 194.0, card_w - 12.0, s32_hyb, font_size=5.8, line_spacing=7.8)
    
    # Box for Thực tế verbatim from trang_32.md
    c.setFillColor(uetgreenbg)
    c.setStrokeColor(uetborder)
    c.setLineWidth(0.5)
    c.rect(237.0, 110.0, 188.0, 48.0, fill=1, stroke=1)
    
    c.setFont('SegoeUI-Bold', 6.0)
    c.setFillColor(uetdarkgreen)
    c.drawString(243.0, 144.0, "Thực tế:")
    
    s32_reality = [
        ("Google và Cloudflare đã thử nghiệm (CECPQ1, CECPQ2), và từ Chrome 116 (08/2023) trình duyệt hỗ trợ lai x25519 + Kyber‑768.", False, False, uetdark)
    ]
    draw_bullet_text(c, 243.0, 133.0, 176.0, s32_reality, font_size=5.6, line_spacing=7.2)
    
    c.showPage()
    
    # =========================================================================
    # SLIDE 33 (trang_33.md)
    # Header: # Hướng 3: Post-Quantum Authenticated Key Exchange
    # Verbatim content ONLY from trang_33.md
    # =========================================================================
    draw_header_footer(c, "Hướng 3: Post-Quantum Authenticated Key Exchange", 33)
    
    # Left Column:
    # Card 1: ## Bản Chất AKE & ## Giải Pháp PQ-AKE: Giao Thức KEMTLS
    draw_accentcard(c, 22.68, 118.0, 204.0, 102.0, "Bản Chất AKE & Giao Thức KEMTLS", uetblue, 7.8)
    
    c.setFont('SegoeUI-Bold', 5.6)
    c.setFillColor(uetdark)
    c.drawString(28.0, 200.0, "Bản Chất AKE:")
    
    s33_nature = [
        ("Do chữ ký PQ có kích thước khá to trong quá trình handshake, vì vậy đề xuất sử dụng KEM cho cả trao đổi khóa và xác thực danh tính.", False, False, uetdark)
    ]
    draw_bullet_text(c, 28.0, 192.0, 192.0, s33_nature, font_size=4.9, line_spacing=6.2)
    
    c.setFont('SegoeUI-Bold', 5.6)
    c.setFillColor(uetblue)
    c.drawString(28.0, 175.0, "Giải Pháp PQ-AKE: Giao Thức KEMTLS:")
    
    s33_sol = [
        [("• Ý tưởng cốt lõi: ", True, False, uetdark), ("Ký thông điệp là một cách xác thực, nhưng ", False, False, uetdark), ("không phải cách duy nhất.", True, False, uetdark)],
        [("• Cơ chế KEMTLS: ", True, False, uetdark), ("Thay vì dùng chữ ký số chứng minh danh tính Server, Client dùng khóa công khai KEM trong chứng chỉ để đóng gói một bí mật và thông qua thông điệp mới gửi cho server. Chỉ Server nắm khóa bí mật mới giải đóng gói được và tính ra khóa đúng khớp với khóa chung.", False, False, uetdark)],
    ]
    by = 166.0
    for b in s33_sol:
        by = draw_bullet_text(c, 28.0, by, 192.0, b, font_size=4.7, line_spacing=5.8)
        by -= 2.0
        
    c.setFont('SegoeUI-Bold', 5.2)
    c.setFillColor(uetred)
    c.drawString(28.0, 124.0, "Không có CertificateVerify (khác TLS 1.3)")
    
    # Card 2: ## Hạn chế verbatim from trang_33.md
    draw_accentcard(c, 22.68, 20.0, 204.0, 93.0, "Hạn chế", uetred, 7.8)
    
    s33_lim = [
        [("• Vẫn dùng ", False, False, uetdark), ("chữ ký cho chứng chỉ", True, False, uetdark), (", nên chưa bỏ hẳn được chữ ký PQ.", False, False, uetdark)],
        [("• Cần KEM ", False, False, uetdark), ("IND-CCA.", True, False, uetdark)],
        [("• Thêm một lượt thông điệp (Finished của Server bị hoãn); xác thực hai chiều cần thêm một round trip.", False, False, uetdark)],
        [("• Với cặp Kyber/Dilithium hiệu năng gần như không khác cách ghép riêng.", False, False, uetdark)],
    ]
    by = 93.0
    for b in s33_lim:
        by = draw_bullet_text(c, 28.0, by, 192.0, b, font_size=5.0, line_spacing=6.3)
        by -= 1.5
        
    # Bottom conclusion verbatim from trang_33.md:
    c.setFillColor(uetaccentbg)
    c.setStrokeColor(uetborder)
    c.setLineWidth(0.4)
    c.rect(26.0, 23.0, 197.5, 17.0, fill=1, stroke=1)
    c.setFont('SegoeUI-Bold', 5.0)
    c.setFillColor(uetdarkgreen)
    c.drawString(28.0, 32.5, "Kết luận: KEMTLS có ích nhất khi băng thông hoặc thiết bị bị hạn")
    c.drawString(28.0, 26.0, "chế (mạng kém, IoT).")
    
    # Right Column: Flow comparison verbatim from trang_33.md
    draw_accentcard(c, 233.0, 20.0, 198.0, 200.0, "So Sánh Luồng Handshake: TLS 1.3 vs KEMTLS", uetgreen, 7.8)
    
    c.setFont('SegoeUI-Bold', 6.2)
    c.setFillColor(uetblue)
    c.drawCentredString(282.0, 197.0, "TLS 1.3")
    c.setFillColor(uetdarkgreen)
    c.drawCentredString(380.0, 197.0, "KEMTLS")
    
    c.setLineWidth(0.4)
    c.setStrokeColor(uetborder)
    c.line(331.0, 202.0, 331.0, 24.0)
    
    # Lifelines TLS 1.3
    c.setFont('SegoeUI', 5.0)
    c.setFillColor(uetdark)
    c.drawString(245.0, 187.0, "Client")
    c.drawString(308.0, 187.0, "Server")
    c.setLineWidth(0.5)
    c.setStrokeColor(colors.HexColor('#CBD5E1'))
    c.line(253.0, 183.0, 253.0, 28.0)
    c.line(316.0, 183.0, 316.0, 28.0)
    
    # TLS 1.3 arrows verbatim
    tls_steps = [
        (168.0, "ClientHello", True, uetblue),
        (148.0, "ServerHello", False, uetblue),
        (131.0, "Certificate", False, uetblue),
        (112.0, "CertificateVerify", False, uetred),
        (92.0, "Finished", False, uetblue),
        (72.0, "Finished", True, uetblue)
    ]
    for sy, sname, is_c2s, scol in tls_steps:
        c.setStrokeColor(scol)
        c.setLineWidth(0.6)
        x1 = 253.0 if is_c2s else 316.0
        x2 = 316.0 if is_c2s else 253.0
        c.line(x1, sy, x2, sy)
        p_arr = c.beginPath()
        p_arr.moveTo(x2, sy)
        p_arr.lineTo(x2 - 2.5 if is_c2s else x2 + 2.5, sy + 1.5)
        p_arr.lineTo(x2 - 2.5 if is_c2s else x2 + 2.5, sy - 1.5)
        p_arr.close()
        c.drawPath(p_arr, fill=1, stroke=0)
        
        if sname == "CertificateVerify":
            draw_mixed_string(c, 284.5, sy + 2.0, "CertificateVerify ✗ bỏ", 'SegoeUI-Bold', 4.3, scol, align='center')
        else:
            c.setFont('SegoeUI', 4.4)
            c.setFillColor(scol)
            c.drawCentredString(284.5, sy + 2.0, sname)
        
    # Lifelines KEMTLS
    c.setFont('SegoeUI', 5.0)
    c.setFillColor(uetdark)
    c.drawString(340.0, 187.0, "Client")
    c.drawString(405.0, 187.0, "Server")
    c.setLineWidth(0.5)
    c.setStrokeColor(colors.HexColor('#CBD5E1'))
    c.line(348.0, 183.0, 348.0, 28.0)
    c.line(413.0, 183.0, 413.0, 28.0)
    
    # KEMTLS arrows verbatim
    kem_steps = [
        (168.0, "ClientHello (khóa KEM tạm)", True, uetdarkgreen),
        (148.0, "ServerHello (ciphertext tạm)", False, uetdarkgreen),
        (131.0, "Certificate (khóa KEM tĩnh)", False, uetdarkgreen),
        (112.0, "(không có CertificateVerify)", None, uetdarkgreen),
        (85.0, "ClientKemCiphertext + Finished ← mới", True, uetdarkgreen),
        (58.0, "Finished (gửi sau)", False, uetdarkgreen)
    ]
    for sy, sname, is_c2s, scol in kem_steps:
        if is_c2s is None:
            c.setFillColor(uetgreenbg)
            c.setStrokeColor(uetgreen)
            c.setLineWidth(0.4)
            c.rect(350.0, sy - 4.0, 61.0, 9.0, fill=1, stroke=1)
            c.setFont('SegoeUI-Bold', 4.1)
            c.setFillColor(uetdarkgreen)
            c.drawCentredString(380.5, sy - 1.5, "(không có CertificateVerify)")
            continue
            
        c.setStrokeColor(scol)
        c.setLineWidth(0.6)
        x1 = 348.0 if is_c2s else 413.0
        x2 = 413.0 if is_c2s else 348.0
        c.line(x1, sy, x2, sy)
        p_arr = c.beginPath()
        p_arr.moveTo(x2, sy)
        p_arr.lineTo(x2 - 2.5 if is_c2s else x2 + 2.5, sy + 1.5)
        p_arr.lineTo(x2 - 2.5 if is_c2s else x2 + 2.5, sy - 1.5)
        p_arr.close()
        c.drawPath(p_arr, fill=1, stroke=0)
        c.setFont('SegoeUI-Bold' if '←' in sname else 'SegoeUI', 4.2)
        c.setFillColor(scol)
        c.drawCentredString(380.5, sy + 2.0, sname)
        
    c.showPage()
    
    # =========================================================================
    # SLIDE 34 (trang_34.md)
    # Header: # Các Vấn Đề Còn Mở
    # Verbatim content ONLY from trang_34.md (3 items)
    # =========================================================================
    draw_header_footer(c, "Các Vấn Đề Còn Mở", 34)
    
    # 3 elegant full-width structured cards for the 3 points in trang_34.md
    items_s34 = [
        (
            "1. Phân Tích Hình Thức:",
            "Chưa có phân tích đầy đủ cho TLS với KEM làm trao đổi khóa (đặc biệt hybrid) và TLS với nhiều chữ ký (hybrid authentication).",
            uetblue,
            uetaccentbg,
            152.0,
            55.0
        ),
        (
            "2. Đa Dạng Hóa Giải Pháp:",
            "Cần bổ sung các giải pháp mật mã hậu lượng tử có chi phí truyền thông thấp cho những môi trường mạng kém.",
            uetblue,
            uetaccentbg,
            88.0,
            55.0
        ),
        (
            "3. Trạng Thái Chuẩn Hóa:",
            "phiên bản TLS tương lai cần hỗ trợ KEM cho trao đổi khóa và nhiều chữ ký/nhiều trao đổi khóa song song để lai.",
            uetdarkgreen,
            uetgreenbg,
            24.0,
            55.0
        )
    ]
    
    for title_txt, body_txt, col, bg_col, cy, ch in items_s34:
        c.setFillColor(bg_col)
        c.setStrokeColor(uetborder)
        c.setLineWidth(0.6)
        c.rect(26.0, cy, 401.5, ch, fill=1, stroke=1)
        
        c.setFillColor(col)
        c.rect(26.0, cy, 3.5, ch, fill=1, stroke=0)
        
        c.setFont('SegoeUI-Bold', 7.4)
        c.setFillColor(col)
        c.drawString(36.0, cy + ch - 16.0, title_txt)
        
        # Body text
        draw_bullet_text(c, 36.0, cy + ch - 30.0, 380.0, [(body_txt, False, False, uetdark)], font_size=6.4, line_spacing=8.6)
        
    c.showPage()
    c.save()
    print("pqc_slides.pdf created successfully.")

def assemble_main3(source_pdf, pqc_pdf, output_pdf):
    src_r = pypdf.PdfReader(source_pdf)
    pqc_r = pypdf.PdfReader(pqc_pdf)
    writer = pypdf.PdfWriter()
    
    total_slides = 36
    print(f"Assembling {output_pdf} with {total_slides} total slides...")
    
    def make_badge_overlay(slide_num):
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(PW, PH))
        badge_x = 428.0
        badge_y = 1.3
        badge_w = 24.5
        badge_h = 9.8
        can.setFillColor(uetlightgray)
        can.setStrokeColor(uetborder)
        can.setLineWidth(0.6)
        can.rect(badge_x, badge_y, badge_w, badge_h, fill=1, stroke=1)
        can.setFont('SegoeUI-Bold', 5.8)
        can.setFillColor(uetblue)
        can.drawCentredString(badge_x + badge_w / 2.0, badge_y + 2.5, f"{slide_num} / {total_slides}")
        can.save()
        packet.seek(0)
        return pypdf.PdfReader(packet).pages[0]
    
    # 1. Slides 1 to 28 from main(2).pdf (with updated badge n / 36)
    for i in range(28):
        p = src_r.pages[i]
        overlay = make_badge_overlay(i + 1)
        p.merge_page(overlay)
        writer.add_page(p)
        
    # 2. Slides 29 to 34 from pqc_slides.pdf
    for i in range(len(pqc_r.pages)):
        writer.add_page(pqc_r.pages[i])
        
    # 3. Slide 35: References (from main(2).pdf page index 33 = slide 34)
    p_ref = src_r.pages[33]
    overlay_ref = make_badge_overlay(35)
    p_ref.merge_page(overlay_ref)
    writer.add_page(p_ref)
    
    # 4. Slide 36: Closing / Q&A (from main(2).pdf page index 34 = slide 35) - plain frame without badge
    p_close = src_r.pages[34]
    writer.add_page(p_close)
    
    with open(output_pdf, 'wb') as f:
        writer.write(f)
    print(f"Successfully generated {output_pdf} with {len(writer.pages)} pages!")

if __name__ == '__main__':
    draw_pqc_slides('pqc_slides.pdf')
    assemble_main3('main(2).pdf', 'pqc_slides.pdf', 'main(3).pdf')
