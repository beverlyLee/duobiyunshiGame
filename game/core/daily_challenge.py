import json
import os
import random
import math
from datetime import datetime, date
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Any


class ModifierType(Enum):
    INFINITE_BULLETS = "infinite_bullets"
    FRAGILE_SHIP = "fragile_ship"
    ACCELERATED_TIME = "accelerated_time"
    MINI_MODE = "mini_mode"
    MIRROR_MODE = "mirror_mode"
    GRAVITY_REVERSAL = "gravity_reversal"


MODIFIER_CONFIG = {
    ModifierType.INFINITE_BULLETS: {
        "name": "无限子弹",
        "description": "无需道具，一直可射击",
        "icon": "🔫",
        "color": (255, 215, 0),
    },
    ModifierType.FRAGILE_SHIP: {
        "name": "脆弱飞船",
        "description": "生命值只有1",
        "icon": "💔",
        "color": (255, 100, 100),
    },
    ModifierType.ACCELERATED_TIME: {
        "name": "加速时间",
        "description": "游戏速度1.5倍",
        "icon": "⏩",
        "color": (100, 255, 200),
    },
    ModifierType.MINI_MODE: {
        "name": "迷你模式",
        "description": "所有物体缩小30%",
        "icon": "🔍",
        "color": (200, 100, 255),
    },
    ModifierType.MIRROR_MODE: {
        "name": "镜像模式",
        "description": "屏幕左右镜像",
        "icon": "🪞",
        "color": (100, 200, 255),
    },
    ModifierType.GRAVITY_REVERSAL: {
        "name": "重力反转",
        "description": "陨石向上飞",
        "icon": "⬆️",
        "color": (255, 150, 50),
    },
}


class RewardType(Enum):
    SHIP_SKIN = "ship_skin"
    PARTICLE_EFFECT = "particle_effect"
    GOLDEN_BORDER = "golden_border"


REWARD_CONFIG = {
    RewardType.SHIP_SKIN: {
        "name": "新飞船皮肤",
        "description": "解锁新的飞船外观",
        "required_stars": 10,
        "icon": "🚀",
    },
    RewardType.PARTICLE_EFFECT: {
        "name": "特殊粒子特效",
        "description": "解锁特殊的粒子效果",
        "required_stars": 25,
        "icon": "✨",
    },
    RewardType.GOLDEN_BORDER: {
        "name": "金色飞船边框",
        "description": "解锁金色飞船边框",
        "required_stars": 50,
        "icon": "👑",
    },
}


@dataclass
class DailyChallenge:
    date_str: str
    seed: int
    modifiers: List[ModifierType]
    created_at: datetime
    
    @classmethod
    def generate(cls, target_date: Optional[date] = None) -> "DailyChallenge":
        if target_date is None:
            target_date = datetime.now().date()
        
        date_str = target_date.strftime("%Y-%m-%d")
        
        seed = cls._generate_seed(target_date)
        
        modifiers = cls._select_modifiers(seed)
        
        return cls(
            date_str=date_str,
            seed=seed,
            modifiers=modifiers,
            created_at=datetime.now()
        )
    
    @staticmethod
    def _generate_seed(target_date: date) -> int:
        date_int = int(target_date.strftime("%Y%m%d"))
        return date_int * 17 + 20260430
    
    @staticmethod
    def _select_modifiers(seed: int) -> List[ModifierType]:
        rng = random.Random(seed)
        all_modifiers = list(ModifierType)
        rng.shuffle(all_modifiers)
        return all_modifiers[:3]
    
    def is_today_challenge(self) -> bool:
        today = datetime.now().strftime("%Y-%m-%d")
        return self.date_str == today
    
    def get_modifier_names(self) -> List[str]:
        return [MODIFIER_CONFIG[m]["name"] for m in self.modifiers]
    
    def get_modifier_configs(self) -> List[Dict]:
        return [{"type": m.value, **MODIFIER_CONFIG[m]} for m in self.modifiers]


@dataclass
class ChallengeRecord:
    date_str: str
    score: int
    stars: int
    is_first_completion: bool
    completed_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "date_str": self.date_str,
            "score": self.score,
            "stars": self.stars,
            "is_first_completion": self.is_first_completion,
            "completed_at": self.completed_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChallengeRecord":
        return cls(
            date_str=data["date_str"],
            score=data["score"],
            stars=data["stars"],
            is_first_completion=data.get("is_first_completion", False),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else datetime.now(),
        )


@dataclass
class LeaderboardEntry:
    player_name: str
    score: int
    stars: int
    date_str: str
    rank: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "player_name": self.player_name,
            "score": self.score,
            "stars": self.stars,
            "date_str": self.date_str,
            "rank": self.rank,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LeaderboardEntry":
        return cls(
            player_name=data["player_name"],
            score=data["score"],
            stars=data["stars"],
            date_str=data["date_str"],
            rank=data.get("rank", 0),
        )


class DailyChallengeManager:
    _instance = None
    SAVE_FILE = "daily_challenge_save.json"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        
        self.current_challenge: Optional[DailyChallenge] = None
        self.challenge_records: Dict[str, ChallengeRecord] = {}
        self.total_stars: int = 0
        self.unlocked_rewards: Set[RewardType] = set()
        self.today_first_completed: bool = False
        self.best_scores: Dict[str, int] = {}
        
        self._load()
        self._initialize_today_challenge()
        self._initialized = True
    
    def _initialize_today_challenge(self):
        today = datetime.now().strftime("%Y-%m-%d")
        
        if not self.current_challenge or self.current_challenge.date_str != today:
            self.current_challenge = DailyChallenge.generate()
            
            if today not in self.challenge_records:
                self.today_first_completed = False
        
        self._save()
    
    def get_current_challenge(self) -> DailyChallenge:
        today = datetime.now().strftime("%Y-%m-%d")
        if not self.current_challenge or self.current_challenge.date_str != today:
            self._initialize_today_challenge()
        return self.current_challenge
    
    def calculate_stars(self, score: int) -> int:
        if score < 500:
            return 1
        elif score < 2000:
            return 2
        else:
            return 3
    
    def record_challenge_completion(self, score: int) -> ChallengeRecord:
        today = datetime.now().strftime("%Y-%m-%d")
        
        stars = self.calculate_stars(score)
        
        if not self.today_first_completed:
            stars *= 2
            self.today_first_completed = True
        
        existing_record = self.challenge_records.get(today)
        if existing_record and existing_record.score >= score:
            return existing_record
        
        if existing_record:
            stars_diff = stars - existing_record.stars
            if stars_diff > 0:
                self.total_stars += stars_diff
        else:
            self.total_stars += stars
        
        record = ChallengeRecord(
            date_str=today,
            score=score,
            stars=stars,
            is_first_completion=not existing_record,
            completed_at=datetime.now()
        )
        
        self.challenge_records[today] = record
        
        if today not in self.best_scores or score > self.best_scores[today]:
            self.best_scores[today] = score
        
        self._check_reward_unlocks()
        self._save()
        
        return record
    
    def _check_reward_unlocks(self):
        for reward_type in RewardType:
            config = REWARD_CONFIG[reward_type]
            if self.total_stars >= config["required_stars"]:
                self.unlocked_rewards.add(reward_type)
    
    def get_unlocked_rewards(self) -> List[RewardType]:
        return list(self.unlocked_rewards)
    
    def get_available_rewards(self) -> List[Dict]:
        rewards = []
        for reward_type in RewardType:
            config = REWARD_CONFIG[reward_type]
            rewards.append({
                "type": reward_type.value,
                "name": config["name"],
                "description": config["description"],
                "required_stars": config["required_stars"],
                "icon": config["icon"],
                "unlocked": reward_type in self.unlocked_rewards,
                "progress": min(1.0, self.total_stars / config["required_stars"]),
            })
        return rewards
    
    def get_history_records(self, limit: int = 30) -> List[ChallengeRecord]:
        sorted_dates = sorted(self.challenge_records.keys(), reverse=True)
        return [self.challenge_records[d] for d in sorted_dates[:limit]]
    
    def get_total_completions(self) -> int:
        return len(self.challenge_records)
    
    def get_average_stars(self) -> float:
        if not self.challenge_records:
            return 0.0
        total = sum(r.stars for r in self.challenge_records.values())
        return total / len(self.challenge_records)
    
    def get_best_score(self) -> int:
        if not self.best_scores:
            return 0
        return max(self.best_scores.values())
    
    def get_today_record(self) -> Optional[ChallengeRecord]:
        today = datetime.now().strftime("%Y-%m-%d")
        return self.challenge_records.get(today)
    
    def is_today_completed(self) -> bool:
        today = datetime.now().strftime("%Y-%m-%d")
        return today in self.challenge_records
    
    def _load(self):
        if os.path.exists(self.SAVE_FILE):
            try:
                with open(self.SAVE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    self.total_stars = data.get("total_stars", 0)
                    
                    records_data = data.get("challenge_records", {})
                    self.challenge_records = {
                        k: ChallengeRecord.from_dict(v) 
                        for k, v in records_data.items()
                    }
                    
                    rewards_data = data.get("unlocked_rewards", [])
                    self.unlocked_rewards = set(
                        RewardType(r) for r in rewards_data
                    )
                    
                    self.today_first_completed = data.get("today_first_completed", False)
                    
                    self.best_scores = data.get("best_scores", {})
                    
                    if data.get("current_challenge"):
                        ch_data = data["current_challenge"]
                        self.current_challenge = DailyChallenge(
                            date_str=ch_data["date_str"],
                            seed=ch_data["seed"],
                            modifiers=[ModifierType(m) for m in ch_data["modifiers"]],
                            created_at=datetime.now()
                        )
                        
            except (json.JSONDecodeError, KeyError, Exception) as e:
                print(f"加载每日挑战存档失败: {e}")
    
    def _save(self):
        try:
            data = {
                "total_stars": self.total_stars,
                "challenge_records": {
                    k: v.to_dict() for k, v in self.challenge_records.items()
                },
                "unlocked_rewards": [r.value for r in self.unlocked_rewards],
                "today_first_completed": self.today_first_completed,
                "best_scores": self.best_scores,
                "current_challenge": {
                    "date_str": self.current_challenge.date_str,
                    "seed": self.current_challenge.seed,
                    "modifiers": [m.value for m in self.current_challenge.modifiers],
                } if self.current_challenge else None,
            }
            
            with open(self.SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存每日挑战存档失败: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_challenge": {
                "date_str": self.current_challenge.date_str,
                "modifiers": self.current_challenge.get_modifier_configs(),
            } if self.current_challenge else None,
            "total_stars": self.total_stars,
            "today_completed": self.is_today_completed(),
            "today_first_completed": self.today_first_completed,
            "unlocked_rewards_count": len(self.unlocked_rewards),
            "best_score": self.get_best_score(),
            "total_completions": self.get_total_completions(),
        }


def get_daily_challenge_manager() -> DailyChallengeManager:
    return DailyChallengeManager()
