#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lich_am.py - In ra ngay am lich Viet Nam cho hom nay (hoac ngay chi dinh).

Thuat toan Ho Ngoc Duc (am lich Viet Nam, mui gio +7).
Chay:
    python3 lich_am.py              -> ngay am cua hom nay
    python3 lich_am.py 10/11/2026   -> ngay am cua ngay duong chi dinh
Chi dung thu vien chuan (math, sys, datetime) nen chay duoc ngay
trong container Home Assistant tai /config/lich_am.py.
"""

import math
import sys
from datetime import date

TIME_ZONE = 7  # Viet Nam GMT+7

CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]


def jd_from_date(dd, mm, yy):
    """Ngay Julian tu ngay duong dd/mm/yy."""
    a = (14 - mm) // 12
    y = yy + 4800 - a
    m = mm + 12 * a - 3
    jd = dd + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    if jd < 2299161:
        jd = dd + (153 * m + 2) // 5 + 365 * y + y // 4 - 32083
    return jd


def new_moon_day(k, time_zone):
    """Ngay Julian (so nguyen, theo mui gio) cua ngay soc thu k."""
    T = k / 1236.85
    T2 = T * T
    T3 = T2 * T
    dr = math.pi / 180
    jd1 = 2415020.75933 + 29.53058868 * k + 0.0001178 * T2 - 0.000000155 * T3
    jd1 += 0.00033 * math.sin((166.56 + 132.87 * T - 0.009173 * T2) * dr)
    M = 359.2242 + 29.10535608 * k - 0.0000333 * T2 - 0.00000347 * T3
    Mpr = 306.0253 + 385.81691806 * k + 0.0107306 * T2 + 0.00001236 * T3
    F = 21.2964 + 390.67050646 * k - 0.0016528 * T2 - 0.00000239 * T3
    C1 = (0.1734 - 0.000393 * T) * math.sin(M * dr) + 0.0021 * math.sin(2 * dr * M)
    C1 += -0.4068 * math.sin(Mpr * dr) + 0.0161 * math.sin(2 * dr * Mpr)
    C1 += -0.0004 * math.sin(3 * dr * Mpr)
    C1 += 0.0104 * math.sin(2 * dr * F) - 0.0051 * math.sin((M + Mpr) * dr)
    C1 += -0.0074 * math.sin((M - Mpr) * dr) + 0.0004 * math.sin((2 * F + M) * dr)
    C1 += -0.0004 * math.sin((2 * F - M) * dr) - 0.0006 * math.sin((2 * F + Mpr) * dr)
    C1 += 0.0010 * math.sin((2 * F - Mpr) * dr) + 0.0005 * math.sin((2 * Mpr + M) * dr)
    if T < -11:
        delta_t = 0.001 + 0.000839 * T + 0.0002261 * T2 - 0.00000845 * T3 - 0.000000081 * T * T3
    else:
        delta_t = -0.000278 + 0.000265 * T + 0.000262 * T2
    jd_new = jd1 + C1 - delta_t
    return math.floor(jd_new + 0.5 + time_zone / 24)


def sun_longitude(jdn, time_zone):
    """Kinh tuyen mat troi tai nua dem ngay Julian jdn, tra ve chi so 0..11 (moi 30 do)."""
    T = (jdn - 2451545.5 - time_zone / 24) / 36525
    T2 = T * T
    dr = math.pi / 180
    M = 357.52910 + 35999.05030 * T - 0.0001559 * T2 - 0.00000048 * T * T2
    L0 = 280.46645 + 36000.76983 * T + 0.0003032 * T2
    DL = (1.914600 - 0.004817 * T - 0.000014 * T2) * math.sin(dr * M)
    DL += (0.019993 - 0.000101 * T) * math.sin(dr * 2 * M) + 0.000290 * math.sin(dr * 3 * M)
    L = (L0 + DL) * dr
    L = L - math.pi * 2 * math.floor(L / (math.pi * 2))
    return math.floor(L / math.pi * 6)


def get_lunar_month_11(yy, time_zone):
    """Ngay bat dau thang 11 am lich cua nam am chua thang 11 cua nam duong yy."""
    off = jd_from_date(31, 12, yy) - 2415021
    k = math.floor(off / 29.530588853)
    nm = new_moon_day(k, time_zone)
    if sun_longitude(nm, time_zone) >= 9:
        nm = new_moon_day(k - 1, time_zone)
    return nm


def get_leap_month_offset(a11, time_zone):
    """Vi tri thang nhuan tinh tu thang 11 (a11 la ngay bat dau thang 11)."""
    k = math.floor((a11 - 2415021.076998695) / 29.530588853 + 0.5)
    last = 0
    i = 1  # bat dau tu thang ngay sau thang 11
    arc = sun_longitude(new_moon_day(k + i, time_zone), time_zone)
    while arc != last and i < 14:
        last = arc
        i += 1
        arc = sun_longitude(new_moon_day(k + i, time_zone), time_zone)
    return i - 1


def solar_to_lunar(dd, mm, yy, time_zone=TIME_ZONE):
    """Doi ngay duong sang am: tra ve (ngay, thang, nam, la_thang_nhuan 0/1)."""
    day_number = jd_from_date(dd, mm, yy)
    k = math.floor((day_number - 2415021.076998695) / 29.530588853)
    month_start = new_moon_day(k + 1, time_zone)
    if month_start > day_number:
        month_start = new_moon_day(k, time_zone)
    a11 = get_lunar_month_11(yy, time_zone)
    b11 = a11
    if a11 >= month_start:
        lunar_year = yy
        a11 = get_lunar_month_11(yy - 1, time_zone)
    else:
        lunar_year = yy + 1
        b11 = get_lunar_month_11(yy + 1, time_zone)
    lunar_day = day_number - month_start + 1
    diff = math.floor((month_start - a11) / 29)
    lunar_leap = 0
    lunar_month = diff + 11
    if b11 - a11 > 365:
        leap_month_diff = get_leap_month_offset(a11, time_zone)
        if diff >= leap_month_diff:
            lunar_month = diff + 10
            if diff == leap_month_diff:
                lunar_leap = 1
    if lunar_month > 12:
        lunar_month -= 12
    if lunar_month >= 11 and diff < 4:
        lunar_year -= 1
    return lunar_day, lunar_month, lunar_year, lunar_leap


def can_chi_year(lunar_year):
    can = CAN[(lunar_year + 6) % 10]
    chi = CHI[(lunar_year + 8) % 12]
    return can + " " + chi


def format_lunar(dd, mm, yy):
    ld, lm, ly, leap = solar_to_lunar(dd, mm, yy)
    s = "%02d-%02d-%s" % (ld, lm, can_chi_year(ly))
    if leap:
        s += " (nhuận)"
    return s


def main():
    if len(sys.argv) > 1:
        parts = sys.argv[1].split("/")
        if len(parts) != 3:
            print("Dinh dang ngay phai la dd/mm/yyyy")
            return 1
        dd, mm, yy = (int(p) for p in parts)
    else:
        today = date.today()
        dd, mm, yy = today.day, today.month, today.year
    print(format_lunar(dd, mm, yy))
    return 0


if __name__ == "__main__":
    sys.exit(main())
