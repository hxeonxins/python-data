from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import pandas as pd
from fastapi.responses import HTMLResponse

app = FastAPI(title="Public Transport Congestion API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 혼잡도 데이터 모델 정의
class CongestionResponse(BaseModel):
    line_id: str
    data: List[Dict[str, str]]  # 시간대별 혼잡도 데이터

# 혼잡도 데이터 로드 및 처리 함수
def get_congestion_data(line_id: str):
    # CSV 파일 경로 (예제 데이터 파일)
    csv_file_path = "data/congestion_data.csv"
    df = pd.read_csv(csv_file_path)
    filtered_data = df[df["line_id"] == line_id]
    return filtered_data.to_dict(orient="records")

# 메인 페이지 - 혼잡도 시각화
@app.get("/", response_class=HTMLResponse)
async def render_home():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Public Transport Congestion</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <h1>Public Transport Congestion Visualization</h1>
        <h2>Enter a line ID to view its congestion level:</h2>
        <form id="lineForm">
            <input type="text" id="lineId" placeholder="Enter line ID" required>
            <button type="submit">Submit</button>
        </form>
        <canvas id="congestionChart" width="800" height="400"></canvas>

        <script>
            document.getElementById("lineForm").onsubmit = async function (e) {
                e.preventDefault();
                const lineId = document.getElementById("lineId").value;
                const response = await fetch(`/congestion/${lineId}`);
                const data = await response.json();

                const labels = data.data.map(item => item.time_slot);
                const values = data.data.map(item => item.congestion_level);

                const ctx = document.getElementById("congestionChart").getContext("2d");
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Congestion Level',
                            data: values,
                            backgroundColor: 'rgba(54, 162, 235, 0.2)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { position: 'top' },
                            title: { display: true, text: 'Congestion Level by Time Slot' }
                        },
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# 특정 노선의 혼잡도 API
@app.get("/congestion/{line_id}", response_model=CongestionResponse)
async def get_congestion(line_id: str):
    """
    특정 노선의 혼잡도를 반환합니다.
    """
    data = get_congestion_data(line_id)
    return {"line_id": line_id, "data": data}
