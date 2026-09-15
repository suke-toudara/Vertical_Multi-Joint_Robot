#!/usr/bin/env python3
"""可搬質量・速度性能の試算.

docs/design_calculations.md の数値はすべて本スクリプトの出力。
前提を変えたら再実行してドキュメントを更新する。

  python3 tools/calc_payload.py
"""
from dataclasses import dataclass

G = 9.81


@dataclass
class Actuator:
    name: str
    tau_rated: float   # N*m  連続定格トルク
    tau_peak: float    # N*m  ピークトルク
    speed_rpm: float   # rpm  定格回転数 (出力軸)
    mass: float        # kg

    @property
    def w_rated(self) -> float:      # rad/s
        return self.speed_rpm * 2 * 3.141592653589793 / 60


AK80_64_48V = Actuator("AK80-64 (48V)", 48.0, 120.0, 48.0, 0.85)
AK80_64_24V = Actuator("AK80-64 (24V)", 48.0, 120.0, 23.0, 0.85)
EDULITE_05 = Actuator("EduLite 05", 1.8, 6.0, 100.0, 0.242)


@dataclass
class Arm:
    L1: float = 0.25        # m  J2 -> J3 (上腕)
    L2: float = 0.20        # m  J3 -> TCP (前腕 + ツールオフセット)
    m_link1: float = 0.35   # kg 上腕の構造質量 (重心 L1/2)
    m_link2: float = 0.25   # kg 前腕の構造質量 (重心 L2/2)
    m_tool: float = 0.30    # kg エンドエフェクタ (TCP 位置)
    m_j3: float = 0.242     # kg J3 アクチュエータ質量 (J3 位置)

    @property
    def R(self) -> float:
        return self.L1 + self.L2

    # --- 水平全伸展姿勢での重力モーメント (ペイロード分を除く) ---
    def static_moment_j3(self) -> float:
        """J3 まわり Sum(m*r)  [kg*m]"""
        return self.m_link2 * (self.L2 / 2) + self.m_tool * self.L2

    def static_moment_j2(self) -> float:
        return (self.m_link1 * (self.L1 / 2)
                + self.m_j3 * self.L1
                + self.m_link2 * (self.L1 + self.L2 / 2)
                + self.m_tool * self.R)

    # --- 慣性モーメント (ペイロード分を除く) ---
    def inertia_j3(self) -> float:
        """J3 まわり  細長い棒: I = m L^2 / 3"""
        return self.m_link2 * self.L2 ** 2 / 3 + self.m_tool * self.L2 ** 2

    def inertia_j2(self) -> float:
        return (self.m_link1 * self.L1 ** 2 / 3
                + self.m_j3 * self.L1 ** 2
                + self.m_link2 * (self.L1 ** 2 + self.L1 * self.L2 + self.L2 ** 2 / 3)
                + self.m_tool * self.R ** 2)

    # J1 は鉛直軸まわり。水平伸展時の半径は J2 と同じなので慣性も同形。
    def inertia_j1(self) -> float:
        return self.inertia_j2()


def max_payload(tau_allow: float, moment: float, inertia: float,
                r: float, alpha: float) -> float:
    """tau_allow >= g*(moment + mp*r) + alpha*(inertia + mp*r^2) を満たす最大 mp."""
    numer = tau_allow - G * moment - alpha * inertia
    denom = G * r + alpha * r ** 2
    return numer / denom


def move_time(angle: float, w_max: float, alpha: float) -> float:
    """台形速度プロファイルでの移動時間 [s]."""
    d_acc = w_max ** 2 / alpha          # 加速+減速で進む角度
    if d_acc >= angle:                  # 三角プロファイル (最高速に届かない)
        return 2 * (angle / alpha) ** 0.5
    return 2 * w_max / alpha + (angle - d_acc) / w_max


def line(cells):
    return "| " + " | ".join(cells) + " |"


# =====================================================================
SF = 1.5          # 安全率 (連続定格に対して)
ALPHA = 10.0      # rad/s^2  設計角加速度

arm_A = Arm(m_j3=EDULITE_05.mass)   # 案A: J3 = EduLite 05
arm_B = Arm(m_j3=AK80_64_48V.mass)  # 案B: J3 = AK80-64

print("# 計算結果 (tools/calc_payload.py)\n")
print(f"共通前提: g={G} m/s^2, 安全率 SF={SF}, 設計角加速度 alpha={ALPHA} rad/s^2")
print(f"リンク: L1={arm_A.L1*1000:.0f} mm, L2={arm_A.L2*1000:.0f} mm, "
      f"リーチ R={arm_A.R*1000:.0f} mm")
print(f"質量: 上腕 {arm_A.m_link1} kg, 前腕 {arm_A.m_link2} kg, "
      f"ツール {arm_A.m_tool} kg\n")

# ---------------------------------------------------------------- 案A
print("\n## 案A: J1=AK80-64 / J2=AK80-64 / J3=EduLite 05\n")
print(f"J3 静的モーメント Sum(m*r) = {arm_A.static_moment_j3():.4f} kg*m")
print(f"  -> 無負荷の重力トルク = {G*arm_A.static_moment_j3():.3f} N*m")
print(f"J3 慣性 (無負荷) = {arm_A.inertia_j3():.5f} kg*m^2")
print(f"J2 静的モーメント Sum(m*r) = {arm_A.static_moment_j2():.4f} kg*m")
print(f"  -> 無負荷の重力トルク = {G*arm_A.static_moment_j2():.3f} N*m")
print(f"J2 慣性 (無負荷) = {arm_A.inertia_j2():.5f} kg*m^2\n")

print(line(["軸", "アクチュエータ", "許容トルク", "最大ペイロード"]))
print(line(["---", "---", "---:", "---:"]))
rows_A = {}
for jname, act, mom, inr, r in [
    ("J3", EDULITE_05, arm_A.static_moment_j3(), arm_A.inertia_j3(), arm_A.L2),
    ("J2", AK80_64_48V, arm_A.static_moment_j2(), arm_A.inertia_j2(), arm_A.R),
]:
    tau_allow = act.tau_rated / SF
    mp = max_payload(tau_allow, mom, inr, r, ALPHA)
    rows_A[jname] = mp
    print(line([jname, act.name, f"{tau_allow:.2f} N*m", f"{mp:.2f} kg"]))
mp_A = min(rows_A.values())
print(f"\n**案A の可搬質量 = {mp_A:.2f} kg** (制約軸: "
      f"{min(rows_A, key=rows_A.get)})")

# J2 の使用率
tau_j2_A = G * (arm_A.static_moment_j2() + mp_A * arm_A.R) + \
    ALPHA * (arm_A.inertia_j2() + mp_A * arm_A.R ** 2)
print(f"このときの J2 所要トルク = {tau_j2_A:.2f} N*m "
      f"(定格 48 N*m に対し {tau_j2_A/48*100:.1f} %)")

# ---------------------------------------------------------------- 案B
print("\n\n## 案B: J1=EduLite 05 / J2=AK80-64 / J3=AK80-64\n")
print(f"J2 静的モーメント Sum(m*r) = {arm_B.static_moment_j2():.4f} kg*m")
print(f"  -> 無負荷の重力トルク = {G*arm_B.static_moment_j2():.3f} N*m\n")
print(line(["軸", "アクチュエータ", "許容トルク", "最大ペイロード"]))
print(line(["---", "---", "---:", "---:"]))
rows_B = {}
for jname, act, mom, inr, r in [
    ("J3", AK80_64_48V, arm_B.static_moment_j3(), arm_B.inertia_j3(), arm_B.L2),
    ("J2", AK80_64_48V, arm_B.static_moment_j2(), arm_B.inertia_j2(), arm_B.R),
]:
    tau_allow = act.tau_rated / SF
    mp = max_payload(tau_allow, mom, inr, r, ALPHA)
    rows_B[jname] = mp
    print(line([jname, act.name, f"{tau_allow:.2f} N*m", f"{mp:.2f} kg"]))

# J1 (EduLite) は重力トルク 0、慣性のみ
tau_allow_j1 = EDULITE_05.tau_rated / SF
mp_j1 = max_payload(tau_allow_j1, 0.0, arm_B.inertia_j1(), arm_B.R, ALPHA)
rows_B["J1"] = mp_j1
print(line(["J1", EDULITE_05.name + " (重力0/慣性のみ)",
            f"{tau_allow_j1:.2f} N*m", f"{mp_j1:.2f} kg"]))
mp_B = min(rows_B.values())
print(f"\n**案B の可搬質量 = {mp_B:.2f} kg** (制約軸: "
      f"{min(rows_B, key=rows_B.get)})")

# J1 を低加速度で使った場合
print("\nJ1 (EduLite 05) の角加速度とペイロードの関係:")
print(line(["alpha_J1 [rad/s^2]", "許容ペイロード [kg]"]))
print(line(["---:", "---:"]))
for a in [2.0, 5.0, 10.0, 20.0]:
    mp = max_payload(tau_allow_j1, 0.0, arm_B.inertia_j1(), arm_B.R, a)
    print(line([f"{a:.0f}", f"{mp:.2f}"]))

# J1 にかかる転倒モーメント (ペイロード 2kg 時)
mp_ref = 2.0
moment_j1 = G * (arm_B.static_moment_j2() + mp_ref * arm_B.R)
print(f"\nJ1 出力軸が受ける曲げモーメント (ペイロード {mp_ref} kg 時) "
      f"= {moment_j1:.1f} N*m")

# --------------------------------------------- 感度分析: 前腕長 vs 可搬質量
print("\n\n## 感度分析: 前腕長 L2 と可搬質量 (案A / J3=EduLite 05)\n")
print(line(["L2 [mm]", "ツール質量 [kg]", "J3重力(無負荷) [N*m]", "可搬質量 [kg]"]))
print(line(["---:", "---:", "---:", "---:"]))
for L2 in [0.10, 0.15, 0.20, 0.25, 0.30]:
    for m_tool in [0.15, 0.30]:
        a = Arm(L2=L2, m_tool=m_tool, m_j3=EDULITE_05.mass)
        mp = max_payload(EDULITE_05.tau_rated / SF, a.static_moment_j3(),
                         a.inertia_j3(), a.L2, ALPHA)
        print(line([f"{L2*1000:.0f}", f"{m_tool:.2f}",
                    f"{G*a.static_moment_j3():.3f}", f"{max(mp, 0):.2f}"]))

# ------------------------------------------------------------ 速度性能
print("\n\n## 速度性能\n")
print(line(["アクチュエータ", "定格回転数", "角速度 [rad/s]",
            f"R={arm_A.R*1000:.0f}mm での手先速度 [m/s]"]))
print(line(["---", "---:", "---:", "---:"]))
for act in [AK80_64_24V, AK80_64_48V, EDULITE_05]:
    print(line([act.name, f"{act.speed_rpm:.0f} rpm",
                f"{act.w_rated:.2f}", f"{act.w_rated*arm_A.R:.2f}"]))

print("\n### 90 deg 移動の所要時間 (台形プロファイル)\n")
import math
angle = math.pi / 2
print(line(["軸 / アクチュエータ", "alpha [rad/s^2]", "w_max [rad/s]",
            "時間 [s]", "プロファイル"]))
print(line(["---", "---:", "---:", "---:", "---"]))
for label, act in [("J2 AK80-64 @24V", AK80_64_24V),
                   ("J2 AK80-64 @48V", AK80_64_48V),
                   ("J3 EduLite 05", EDULITE_05)]:
    for a in [10.0, 20.0]:
        t = move_time(angle, act.w_rated, a)
        shape = "三角" if act.w_rated ** 2 / a >= angle else "台形"
        print(line([label, f"{a:.0f}", f"{act.w_rated:.2f}",
                    f"{t:.2f}", shape]))

# ------------------------------------------------------------ 精度
print("\n\n## バックラッシ由来の手先位置誤差\n")
backlash_arcmin = 10.0
rad = backlash_arcmin / 60 * math.pi / 180
print(f"AK80-64 バックラッシ {backlash_arcmin:.0f} arcmin = {rad*1000:.3f} mrad")
print(line(["軸", "腕の長さ [mm]", "手先誤差 [mm]"]))
print(line(["---", "---:", "---:"]))
print(line(["J1 (旋回)", f"{arm_A.R*1000:.0f}", f"{rad*arm_A.R*1000:.2f}"]))
print(line(["J2 (肩)", f"{arm_A.R*1000:.0f}", f"{rad*arm_A.R*1000:.2f}"]))
print(f"\nJ1+J2 の直交方向単純和 = {2*rad*arm_A.R*1000:.2f} mm, "
      f"RSS = {math.sqrt(2)*rad*arm_A.R*1000:.2f} mm")


# =====================================================================
# 追加検討: 目標ペイロードからの逆算 / ピークトルク基準 / 推奨構成
# =====================================================================

def solve_L2(target_mp: float, tau_allow: float, m_link2: float,
             m_tool: float, alpha: float, lo=0.02, hi=0.60) -> float:
    """目標ペイロードを満たす最大の L2 を二分法で求める (見つからなければ 0)."""
    def margin(L2):
        a = Arm(L2=L2, m_link2=m_link2, m_tool=m_tool, m_j3=EDULITE_05.mass)
        return max_payload(tau_allow, a.static_moment_j3(), a.inertia_j3(),
                           L2, alpha) - target_mp
    if margin(lo) < 0:
        return 0.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if margin(mid) >= 0:
            lo = mid
        else:
            hi = mid
    return lo


print("\n\n## 目標ペイロードから逆算した許容前腕長 L2 (案A / J3=EduLite 05)\n")
print(line(["目標ペイロード [kg]", "ツール0.15kg: 許容L2 [mm]",
            "ツール0.30kg: 許容L2 [mm]"]))
print(line(["---:", "---:", "---:"]))
for target in [0.25, 0.50, 0.75, 1.00, 1.50]:
    vals = []
    for m_tool in [0.15, 0.30]:
        L2 = solve_L2(target, EDULITE_05.tau_rated / SF, 0.25, m_tool, ALPHA)
        vals.append(f"{L2*1000:.0f}" if L2 > 0 else "不可")
    print(line([f"{target:.2f}"] + vals))


print("\n\n## ピーク(瞬時)トルク基準での許容ペイロード — 連続保持は不可\n")
print(line(["軸/構成", "基準トルク", "許容トルク(SF=1.5)", "ペイロード [kg]"]))
print(line(["---", "---:", "---:", "---:"]))
for label, act, arm, mom, inr, r in [
    ("案A J3 (EduLite 定格)", EDULITE_05, arm_A, arm_A.static_moment_j3(),
     arm_A.inertia_j3(), arm_A.L2),
]:
    for basis, tau in [("定格 1.8 N*m", act.tau_rated),
                       ("ピーク 6.0 N*m", act.tau_peak)]:
        mp = max_payload(tau / SF, mom, inr, r, ALPHA)
        print(line([label, basis, f"{tau/SF:.2f} N*m", f"{max(mp,0):.2f}"]))


print("\n\n## 安全率の感度 (案A / L2=200mm / ツール0.30kg)\n")
print(line(["安全率 SF", "許容トルク [N*m]", "可搬質量 [kg]"]))
print(line(["---:", "---:", "---:"]))
for sf in [1.0, 1.2, 1.5, 2.0]:
    mp = max_payload(EDULITE_05.tau_rated / sf, arm_A.static_moment_j3(),
                     arm_A.inertia_j3(), arm_A.L2, ALPHA)
    print(line([f"{sf:.1f}", f"{EDULITE_05.tau_rated/sf:.2f}",
                f"{max(mp,0):.2f}"]))


# ---------------------------------------------------------------- 案C
print("\n\n## 案C (推奨): 手持ち部品のまま前腕を詰めた構成\n")
arm_C = Arm(L1=0.25, L2=0.12, m_link1=0.35, m_link2=0.18,
            m_tool=0.20, m_j3=EDULITE_05.mass)
mp_C_j3 = max_payload(EDULITE_05.tau_rated / SF, arm_C.static_moment_j3(),
                      arm_C.inertia_j3(), arm_C.L2, ALPHA)
mp_C_j2 = max_payload(AK80_64_48V.tau_rated / SF, arm_C.static_moment_j2(),
                      arm_C.inertia_j2(), arm_C.R, ALPHA)
mp_C = min(mp_C_j3, mp_C_j2)
print(f"寸法: L1={arm_C.L1*1000:.0f} mm, L2={arm_C.L2*1000:.0f} mm, "
      f"リーチ R={arm_C.R*1000:.0f} mm")
print(f"質量: 上腕 {arm_C.m_link1} kg, 前腕 {arm_C.m_link2} kg, "
      f"ツール {arm_C.m_tool} kg")
print(f"\n可搬質量 = {mp_C:.2f} kg (J3制約 {mp_C_j3:.2f} / J2制約 {mp_C_j2:.2f})\n")

print(line(["軸", "アクチュエータ", "所要トルク", "定格", "使用率"]))
print(line(["---", "---", "---:", "---:", "---:"]))
tau_j3_C = G * (arm_C.static_moment_j3() + mp_C * arm_C.L2) + \
    ALPHA * (arm_C.inertia_j3() + mp_C * arm_C.L2 ** 2)
tau_j2_C = G * (arm_C.static_moment_j2() + mp_C * arm_C.R) + \
    ALPHA * (arm_C.inertia_j2() + mp_C * arm_C.R ** 2)
tau_j1_C = ALPHA * (arm_C.inertia_j1() + mp_C * arm_C.R ** 2)
for jn, act, tau in [("J1", AK80_64_48V, tau_j1_C),
                     ("J2", AK80_64_48V, tau_j2_C),
                     ("J3", EDULITE_05, tau_j3_C)]:
    print(line([jn, act.name, f"{tau:.2f} N*m", f"{act.tau_rated:.1f} N*m",
                f"{tau/act.tau_rated*100:.1f} %"]))

v_tcp_C = AK80_64_48V.w_rated * arm_C.R
print(f"\n手先最大速度 (J2 単軸, 全伸展 R={arm_C.R*1000:.0f}mm) "
      f"= {v_tcp_C:.2f} m/s")
print(f"手先最大速度 (J1+J2 同時, 幾何合成の上限) "
      f"= {v_tcp_C*math.sqrt(2):.2f} m/s")

mass_total = (2 * AK80_64_48V.mass + EDULITE_05.mass + arm_C.m_link1
              + arm_C.m_link2 + arm_C.m_tool)
print(f"\n可動部+アクチュエータ質量合計 = {mass_total:.2f} kg (ベース構造を除く)")
print(f"ペイロード/自重比 = {mp_C/mass_total*100:.1f} %")


print("\n\n## 電源概算\n")
p_ak = 220.0   # W, AK80-64 定格出力 (カタログ値)
print(line(["項目", "値", "根拠"]))
print(line(["---", "---:", "---"]))
print(line(["AK80-64 定格出力", f"{p_ak:.0f} W x2 = {2*p_ak:.0f} W", "カタログ値"]))
print(line(["EduLite 05 定格出力",
            f"約 {1.8*EDULITE_05.w_rated:.0f} W", "定格トルク x 定格角速度"]))
print(line(["合計 (定格)", f"約 {2*p_ak + 1.8*EDULITE_05.w_rated:.0f} W", "単純和"]))
print(line(["48V 系の定格電流",
            f"約 {(2*p_ak + 1.8*EDULITE_05.w_rated)/48:.1f} A", "P/V"]))
print(line(["推奨電源", "48 V / 600 W 以上", "定格の約1.3倍 + 突入余裕"]))
print("\n注: 実運用では全軸同時に定格を出すことは稀。ただし電流制限に"
      "かかると軌道が崩れるため、ピーク電流に耐える電源を選ぶこと。")
