# 서울 시간대별 평균 풍속 분석
# 원본: 기상청 ASOS 시간자료

from pathlib import Path
import pandas as pd

# 1. 프로젝트 경로 설정
base_path = Path(__file__).resolve().parent.parent

csv_path = (
    base_path
    / "data"
    / "raw"
    / "OBS_ASOS_TIM_20261019111228.csv"
)

# 2. 원본 CSV 읽기
df = pd.read_csv(csv_path, encoding="cp949")

# 3. 날짜와 시간 변환
df["일시"] = pd.to_datetime(df["일시"], errors="coerce")

# 4. 풍속을 숫자로 변환
df["풍속(m/s)"] = pd.to_numeric(
    df["풍속(m/s)"],
    errors="coerce"
)

# 5. 분석에 필요한 값이 없는 행 제외
valid = df.dropna(
    subset=["일시", "풍속(m/s)"]
).copy()

# 6. 관측 시각에서 시간만 추출
valid["시간"] = valid["일시"].dt.hour

# 7. 시간대별 평균 풍속 계산
hourly = (
    valid.groupby("시간")["풍속(m/s)"]
    .agg(["count", "mean"])
    .round(2)
)

# 8. 분석 결과 출력
print("\n서울 시간대별 평균 풍속 분석")
print("--------------------------------")
print("전체 관측 기록:", len(df))
print("분석에 사용한 기록:", len(valid))

print("\n시간대별 관측 건수와 평균 풍속")
print(hourly.to_string())

# 9. 평균 풍속이 가장 강한 시간 확인
if not hourly.empty:
    max_hour = hourly["mean"].idxmax()
    max_wind = hourly.loc[max_hour, "mean"]

    print("\n평균 풍속이 가장 강한 시간")
    print(f"{max_hour:02d}시 / {max_wind:.2f}m/s")
else:
    print("\n분석 가능한 풍속 데이터가 없습니다.")
  # 10. 시간대별 평균 풍속 그래프 만들기
import matplotlib.pyplot as plt

if not hourly.empty:
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.bar(
        hourly.index,
        hourly["mean"],
        color="skyblue",
        edgecolor="black"
    )

    # 평균 풍속이 가장 높은 시간 강조
    ax.bar(
        max_hour,
        max_wind,
        color="tomato",
        edgecolor="black"
    )

    ax.set_title("Seoul Hourly Average Wind Speed (Oct 12-18, 2026)")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Average Wind Speed (m/s)")

    ax.set_xticks(range(24))
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", alpha=0.3)

    # 가장 높은 풍속 표시
    ax.text(
        max_hour,
        max_wind + 0.05,
        f"{max_wind:.2f} m/s",
        ha="center",
        fontsize=11
    )

    # 그래프 저장
    save_path = base_path / "screenshots" / "hourly_wind_analysis.png"
    save_path.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(save_path, dpi=200, bbox_inches="tight")

    print(f"\n그래프 저장 완료: {save_path}")

    plt.show()  