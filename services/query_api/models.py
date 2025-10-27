"""
資料模型定義

定義 API 返回的資料格式
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ==================== 會話相關模型 ====================

class SessionSummary(BaseModel):
    """會話摘要（列表視圖）"""
    sess_uuid: str = Field(..., description="會話唯一識別碼")
    peer_ip: str = Field(..., description="攻擊來源 IP")
    peer_port: int = Field(..., description="攻擊來源端口")
    user_agent: str = Field(..., description="User Agent")
    attack_types: List[str] = Field(..., description="攻擊類型列表")
    risk_score: int = Field(..., description="風險分數 (0-100)")
    threat_level: str = Field(..., description="威脅等級")
    alert_level: str = Field(..., description="警報等級")
    processed_at: str = Field(..., description="處理時間")
    total_requests: int = Field(..., description="總請求數")
    has_malicious_activity: bool = Field(..., description="是否包含惡意活動")

    # 簡化的威脅情報
    is_scanner: Optional[bool] = Field(None, description="是否為掃描工具")
    tool_identified: Optional[str] = Field(None, description="識別的工具名稱")

    class Config:
        json_schema_extra = {
            "example": {
                "sess_uuid": "test-sqli-attack-001",
                "peer_ip": "192.168.1.100",
                "peer_port": 54321,
                "user_agent": "sqlmap/1.7.2",
                "attack_types": ["sqli", "sqli", "sqli"],
                "risk_score": 51,
                "threat_level": "HIGH",
                "alert_level": "HIGH",
                "processed_at": "2025-10-26T14:00:58.374263",
                "total_requests": 2,
                "has_malicious_activity": True,
                "is_scanner": True,
                "tool_identified": "sqlmap"
            }
        }


class SessionListResponse(BaseModel):
    """會話列表響應"""
    sessions: List[SessionSummary] = Field(..., description="會話列表")
    total: int = Field(..., description="總數量")
    limit: int = Field(..., description="每頁數量")
    offset: int = Field(..., description="偏移量")
    has_more: bool = Field(..., description="是否還有更多資料")

    class Config:
        json_schema_extra = {
            "example": {
                "sessions": [],
                "total": 150,
                "limit": 50,
                "offset": 0,
                "has_more": True
            }
        }


class SessionDetailResponse(BaseModel):
    """會話詳細響應（包含所有欄位）"""
    # 基本資訊
    sess_uuid: str
    peer_ip: str
    peer_port: int
    user_agent: str
    snare_uuid: str
    processed_at: str

    # 攻擊資訊
    attack_types: List[str]
    attack_count: Dict[str, int]
    total_requests: int
    unique_attack_types: int
    has_malicious_activity: bool

    # 請求詳情
    paths: List[Dict[str, Any]]

    # 地理位置
    location: Dict[str, Any]

    # 威脅情報
    threat_intelligence: Dict[str, Any]

    # 攻擊模式
    attack_patterns: Dict[str, Any]

    # User Agent 分析
    user_agent_info: Dict[str, Any]

    # 請求模式
    request_patterns: Dict[str, Any]

    # Payload 分析
    payload_analysis: Dict[str, Any]

    # 時間模式
    temporal_patterns: Dict[str, Any]

    # 行為標籤
    behavior_tags: List[str]

    # 攻擊階段
    attack_phases: List[str]

    # 風險評估
    risk_score: int
    risk_breakdown: Dict[str, int]
    threat_level: str
    priority: str
    confidence_score: float
    exploitation_likelihood: str

    # 影響評估
    impact_assessment: Dict[str, Any]

    # 建議
    recommendations: List[str]

    # 標記
    requires_review: bool
    alert_level: str


# ==================== 警報相關模型 ====================

class AlertSummary(BaseModel):
    """警報摘要"""
    sess_uuid: str
    peer_ip: str
    alert_level: str
    threat_level: str
    risk_score: int
    attack_types: List[str]
    tool_identified: Optional[str]
    processed_at: str
    recommendations_count: int

    class Config:
        json_schema_extra = {
            "example": {
                "sess_uuid": "test-sqli-attack-001",
                "peer_ip": "192.168.1.100",
                "alert_level": "HIGH",
                "threat_level": "HIGH",
                "risk_score": 51,
                "attack_types": ["sqli"],
                "tool_identified": "sqlmap",
                "processed_at": "2025-10-26T14:00:58.374263",
                "recommendations_count": 9
            }
        }


class AlertListResponse(BaseModel):
    """警報列表響應"""
    alerts: List[AlertSummary]
    total: int
    limit: int
    offset: int
    has_more: bool


# ==================== 統計相關模型 ====================

class StatisticsResponse(BaseModel):
    """統計資料響應"""
    date: str = Field(..., description="統計日期")
    total_sessions: int = Field(..., description="總會話數")

    # 威脅等級分布
    threat_level_distribution: Dict[str, int] = Field(..., description="威脅等級分布")

    # 風險分數分布
    risk_score_distribution: Dict[str, int] = Field(..., description="風險分數分布")

    # 攻擊類型分布
    attack_type_distribution: Dict[str, int] = Field(..., description="攻擊類型分布")

    # TOP 來源 IP
    top_source_ips: Dict[str, int] = Field(..., description="TOP 攻擊來源 IP")

    # TOP User Agents
    top_user_agents: Dict[str, int] = Field(..., description="TOP User Agents")

    # 警報統計
    alert_counts: Dict[str, int] = Field(..., description="警報等級統計")

    # 平均風險分數
    average_risk_score: float = Field(..., description="平均風險分數")

    # 需要審查數量
    requires_review_count: int = Field(..., description="需要人工審查的數量")

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2025-10-26",
                "total_sessions": 150,
                "threat_level_distribution": {
                    "CRITICAL": 5,
                    "HIGH": 20,
                    "MEDIUM": 50,
                    "LOW": 45,
                    "INFO": 30
                },
                "risk_score_distribution": {
                    "critical": 5,
                    "high": 20,
                    "medium": 50,
                    "low": 45,
                    "info": 30
                },
                "attack_type_distribution": {
                    "sqli": 30,
                    "xss": 25,
                    "lfi": 15,
                    "cmd_exec": 10,
                    "index": 70
                },
                "top_source_ips": {
                    "192.168.1.100": 15,
                    "10.0.0.50": 12,
                    "172.16.0.99": 8
                },
                "top_user_agents": {
                    "sqlmap/1.7.2": 10,
                    "curl/7.68.0": 8
                },
                "alert_counts": {
                    "CRITICAL": 5,
                    "HIGH": 20,
                    "MEDIUM": 50,
                    "LOW": 45,
                    "INFO": 30
                },
                "average_risk_score": 42.5,
                "requires_review_count": 25
            }
        }


# ==================== 儀表板相關模型 ====================

class DashboardResponse(BaseModel):
    """儀表板資料響應"""
    # 概覽統計
    today_summary: Dict[str, Any] = Field(..., description="今日摘要")

    # 最近警報
    recent_alerts: List[AlertSummary] = Field(..., description="最近的高風險警報")

    # 威脅趨勢（最近24小時）
    hourly_trend: List[Dict[str, Any]] = Field(..., description="每小時趨勢")

    # TOP 威脅
    top_threats: Dict[str, Any] = Field(..., description="TOP 威脅資訊")

    class Config:
        json_schema_extra = {
            "example": {
                "today_summary": {
                    "total_sessions": 150,
                    "high_risk_count": 25,
                    "critical_alerts": 5,
                    "average_risk": 42.5,
                    "unique_ips": 45
                },
                "recent_alerts": [],
                "hourly_trend": [],
                "top_threats": {
                    "top_ips": {},
                    "top_attacks": {},
                    "top_tools": {}
                }
            }
        }


# ==================== 威脅情報相關模型 ====================

class ThreatIntelligenceResponse(BaseModel):
    """威脅情報響應"""
    date: str = Field(..., description="日期")

    # IP 黑名單
    malicious_ips: List[str] = Field(..., description="惡意 IP 列表")
    malicious_ips_count: int = Field(..., description="惡意 IP 數量")

    # 攻擊簽名
    attack_signatures: List[str] = Field(..., description="攻擊模式簽名")
    attack_signatures_count: int = Field(..., description="攻擊簽名數量")

    # 惡意 User Agents
    malicious_user_agents: List[str] = Field(..., description="惡意 User Agents")

    # Payload 樣本
    sample_payloads: List[Dict[str, Any]] = Field(..., description="Payload 樣本")

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2025-10-26",
                "malicious_ips": ["192.168.1.100", "10.0.0.50"],
                "malicious_ips_count": 2,
                "attack_signatures": ["sqli", "cmd_exec-rfi"],
                "attack_signatures_count": 2,
                "malicious_user_agents": ["sqlmap/1.7.2"],
                "sample_payloads": []
            }
        }
