import json
import os
from enum import Enum


class SkillBranchType(Enum):
    ATTACK = "attack"
    DEFENSE = "defense"
    MOBILITY = "mobility"


class SkillType(Enum):
    BASIC_ATTACK = "basic_attack"
    BULLET_DAMAGE = "bullet_damage"
    FIRE_RATE = "fire_rate"
    PENETRATION = "penetration"
    EXPLOSION_RANGE = "explosion_range"
    
    BASIC_LIFE = "basic_life"
    SHIELD_STRENGTH = "shield_strength"
    MAX_LIFE = "max_life"
    SHIELD_DURATION = "shield_duration"
    COLLISION_DAMAGE_REDUCTION = "collision_damage_reduction"
    
    BASIC_MOVE = "basic_move"
    MOVE_SPEED = "move_speed"
    DODGE_REWARD = "dodge_reward"
    COMBO_DURATION = "combo_duration"
    POWERUP_DURATION = "powerup_duration"


SKILL_CONFIG = {
    SkillBranchType.ATTACK: {
        "name": "攻击",
        "color": (255, 100, 100),
        "skills": [
            {
                "type": SkillType.BASIC_ATTACK,
                "name": "基础攻击",
                "description": "子弹伤害 +1",
                "max_level": 3,
                "cost_per_level": 0,
                "base_bonus": 1,
                "bonus_per_level": 1,
                "requires": [],
                "is_starter": True,
            },
            {
                "type": SkillType.BULLET_DAMAGE,
                "name": "子弹伤害",
                "description": "每级子弹伤害 +2",
                "max_level": 3,
                "cost_per_level": 1,
                "base_bonus": 0,
                "bonus_per_level": 2,
                "requires": [SkillType.BASIC_ATTACK],
            },
            {
                "type": SkillType.FIRE_RATE,
                "name": "射速",
                "description": "每级射击冷却 -1帧",
                "max_level": 3,
                "cost_per_level": 1,
                "base_bonus": 0,
                "bonus_per_level": 1,
                "requires": [SkillType.BASIC_ATTACK],
            },
            {
                "type": SkillType.PENETRATION,
                "name": "穿透力",
                "description": "每级穿透次数 +1",
                "max_level": 3,
                "cost_per_level": 2,
                "base_bonus": 0,
                "bonus_per_level": 1,
                "requires": [SkillType.BULLET_DAMAGE, SkillType.FIRE_RATE],
            },
            {
                "type": SkillType.EXPLOSION_RANGE,
                "name": "爆炸范围",
                "description": "每级爆炸范围 +10%",
                "max_level": 3,
                "cost_per_level": 2,
                "base_bonus": 0,
                "bonus_per_level": 0.1,
                "requires": [SkillType.PENETRATION],
            },
        ],
    },
    SkillBranchType.DEFENSE: {
        "name": "防御",
        "color": (100, 150, 255),
        "skills": [
            {
                "type": SkillType.BASIC_LIFE,
                "name": "基础生命",
                "description": "最大生命 +1",
                "max_level": 3,
                "cost_per_level": 0,
                "base_bonus": 1,
                "bonus_per_level": 1,
                "requires": [],
                "is_starter": True,
            },
            {
                "type": SkillType.SHIELD_STRENGTH,
                "name": "护盾强度",
                "description": "每级护盾吸收伤害 +1",
                "max_level": 3,
                "cost_per_level": 1,
                "base_bonus": 0,
                "bonus_per_level": 1,
                "requires": [SkillType.BASIC_LIFE],
            },
            {
                "type": SkillType.MAX_LIFE,
                "name": "生命上限",
                "description": "每级最大生命 +1",
                "max_level": 3,
                "cost_per_level": 1,
                "base_bonus": 0,
                "bonus_per_level": 1,
                "requires": [SkillType.BASIC_LIFE],
            },
            {
                "type": SkillType.SHIELD_DURATION,
                "name": "护盾持续时间",
                "description": "每级护盾持续时间 +1秒",
                "max_level": 3,
                "cost_per_level": 2,
                "base_bonus": 0,
                "bonus_per_level": 1,
                "requires": [SkillType.SHIELD_STRENGTH, SkillType.MAX_LIFE],
            },
            {
                "type": SkillType.COLLISION_DAMAGE_REDUCTION,
                "name": "碰撞伤害减免",
                "description": "每级碰撞伤害减免 +15%",
                "max_level": 3,
                "cost_per_level": 2,
                "base_bonus": 0,
                "bonus_per_level": 0.15,
                "requires": [SkillType.SHIELD_DURATION],
            },
        ],
    },
    SkillBranchType.MOBILITY: {
        "name": "机动",
        "color": (100, 255, 150),
        "skills": [
            {
                "type": SkillType.BASIC_MOVE,
                "name": "基础移动",
                "description": "移动速度 +1",
                "max_level": 3,
                "cost_per_level": 0,
                "base_bonus": 1,
                "bonus_per_level": 1,
                "requires": [],
                "is_starter": True,
            },
            {
                "type": SkillType.MOVE_SPEED,
                "name": "移动速度",
                "description": "每级移动速度 +1",
                "max_level": 3,
                "cost_per_level": 1,
                "base_bonus": 0,
                "bonus_per_level": 1,
                "requires": [SkillType.BASIC_MOVE],
            },
            {
                "type": SkillType.DODGE_REWARD,
                "name": "躲避奖励",
                "description": "每级躲避得分 +10%",
                "max_level": 3,
                "cost_per_level": 1,
                "base_bonus": 0,
                "bonus_per_level": 0.1,
                "requires": [SkillType.BASIC_MOVE],
            },
            {
                "type": SkillType.COMBO_DURATION,
                "name": "连击持续时间",
                "description": "每级连击持续时间 +0.5秒",
                "max_level": 3,
                "cost_per_level": 2,
                "base_bonus": 0,
                "bonus_per_level": 0.5,
                "requires": [SkillType.MOVE_SPEED, SkillType.DODGE_REWARD],
            },
            {
                "type": SkillType.POWERUP_DURATION,
                "name": "道具持续时间",
                "description": "每级道具持续时间 +15%",
                "max_level": 3,
                "cost_per_level": 2,
                "base_bonus": 0,
                "bonus_per_level": 0.15,
                "requires": [SkillType.COMBO_DURATION],
            },
        ],
    },
}


class Skill:
    def __init__(self, skill_type: SkillType, config: dict):
        self.type = skill_type
        self.name = config["name"]
        self.description = config["description"]
        self.max_level = config["max_level"]
        self.cost_per_level = config["cost_per_level"]
        self.base_bonus = config["base_bonus"]
        self.bonus_per_level = config["bonus_per_level"]
        self.requires = config.get("requires", [])
        self.is_starter = config.get("is_starter", False)
        self.current_level = 0
        self.unlocked = False
    
    def get_bonus(self):
        if not self.unlocked:
            return 0
        return self.base_bonus + (self.current_level * self.bonus_per_level)
    
    def get_next_cost(self):
        if self.current_level >= self.max_level:
            return None
        return self.cost_per_level
    
    def can_upgrade(self, skill_points: int, unlocked_skills: set):
        if self.current_level >= self.max_level:
            return False
        
        next_cost = self.get_next_cost()
        if next_cost is None or skill_points < next_cost:
            return False
        
        for required in self.requires:
            if required not in unlocked_skills:
                return False
        
        return True
    
    def upgrade(self):
        if self.current_level >= self.max_level:
            return False
        self.current_level += 1
        self.unlocked = True
        return True
    
    def to_dict(self):
        return {
            "type": self.type.value,
            "current_level": self.current_level,
            "unlocked": self.unlocked,
        }
    
    @classmethod
    def from_dict(cls, data: dict, config: dict):
        skill = cls(SkillType(data["type"]), config)
        skill.current_level = data.get("current_level", 0)
        skill.unlocked = data.get("unlocked", False)
        return skill


class SkillBranch:
    def __init__(self, branch_type: SkillBranchType):
        self.type = branch_type
        config = SKILL_CONFIG[branch_type]
        self.name = config["name"]
        self.color = config["color"]
        self.skills = {}
        
        for skill_config in config["skills"]:
            skill_type = skill_config["type"]
            self.skills[skill_type] = Skill(skill_type, skill_config)
    
    def get_skill(self, skill_type: SkillType) -> Skill:
        return self.skills.get(skill_type)
    
    def get_unlocked_skills(self) -> set:
        unlocked = set()
        for skill in self.skills.values():
            if skill.unlocked:
                unlocked.add(skill.type)
        return unlocked
    
    def to_dict(self):
        return {
            "type": self.type.value,
            "skills": [skill.to_dict() for skill in self.skills.values()],
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        branch_type = SkillBranchType(data["type"])
        branch = cls(branch_type)
        
        config = SKILL_CONFIG[branch_type]
        skill_config_map = {sc["type"]: sc for sc in config["skills"]}
        
        for skill_data in data.get("skills", []):
            skill_type = SkillType(skill_data["type"])
            if skill_type in skill_config_map:
                branch.skills[skill_type] = Skill.from_dict(skill_data, skill_config_map[skill_type])
        
        return branch


class SkillTreeManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        
        self.skill_points = 0
        self.total_earned_points = 0
        self.branches = {}
        
        for branch_type in SkillBranchType:
            self.branches[branch_type] = SkillBranch(branch_type)
        
        self._unlock_starter_skills()
        self._initialized = True
    
    def _unlock_starter_skills(self):
        for branch in self.branches.values():
            for skill in branch.skills.values():
                if skill.is_starter:
                    skill.unlocked = True
                    skill.current_level = 1
    
    def get_branch(self, branch_type: SkillBranchType) -> SkillBranch:
        return self.branches.get(branch_type)
    
    def get_skill(self, skill_type: SkillType) -> Skill:
        for branch in self.branches.values():
            skill = branch.get_skill(skill_type)
            if skill:
                return skill
        return None
    
    def get_all_unlocked_skills(self) -> set:
        unlocked = set()
        for branch in self.branches.values():
            unlocked.update(branch.get_unlocked_skills())
        return unlocked
    
    def can_upgrade_skill(self, skill_type: SkillType) -> bool:
        skill = self.get_skill(skill_type)
        if not skill:
            return False
        
        unlocked_skills = self.get_all_unlocked_skills()
        return skill.can_upgrade(self.skill_points, unlocked_skills)
    
    def upgrade_skill(self, skill_type: SkillType) -> bool:
        if not self.can_upgrade_skill(skill_type):
            return False
        
        skill = self.get_skill(skill_type)
        cost = skill.get_next_cost()
        
        if cost is None:
            return False
        
        self.skill_points -= cost
        return skill.upgrade()
    
    def add_skill_points(self, amount: int):
        self.skill_points += amount
        self.total_earned_points += amount
    
    def get_skill_bonus(self, skill_type: SkillType):
        skill = self.get_skill(skill_type)
        if skill:
            return skill.get_bonus()
        return 0
    
    def get_attack_bonus(self, skill_type: SkillType):
        return self.get_skill_bonus(skill_type)
    
    def get_defense_bonus(self, skill_type: SkillType):
        return self.get_skill_bonus(skill_type)
    
    def get_mobility_bonus(self, skill_type: SkillType):
        return self.get_skill_bonus(skill_type)
    
    def get_total_bullet_damage(self) -> int:
        return int(self.get_skill_bonus(SkillType.BASIC_ATTACK) + 
                   self.get_skill_bonus(SkillType.BULLET_DAMAGE))
    
    def get_fire_rate_reduction(self) -> int:
        return int(self.get_skill_bonus(SkillType.FIRE_RATE))
    
    def get_penetration_count(self) -> int:
        return int(self.get_skill_bonus(SkillType.PENETRATION))
    
    def get_explosion_range_multiplier(self) -> float:
        return 1.0 + self.get_skill_bonus(SkillType.EXPLOSION_RANGE)
    
    def get_total_max_life(self) -> int:
        return int(self.get_skill_bonus(SkillType.BASIC_LIFE) + 
                   self.get_skill_bonus(SkillType.MAX_LIFE))
    
    def get_shield_strength(self) -> int:
        return int(self.get_skill_bonus(SkillType.SHIELD_STRENGTH))
    
    def get_shield_duration_extra(self) -> int:
        from game.config import FPS
        return int(self.get_skill_bonus(SkillType.SHIELD_DURATION) * FPS)
    
    def get_collision_damage_reduction(self) -> float:
        return self.get_skill_bonus(SkillType.COLLISION_DAMAGE_REDUCTION)
    
    def get_total_move_speed(self) -> int:
        return int(self.get_skill_bonus(SkillType.BASIC_MOVE) + 
                   self.get_skill_bonus(SkillType.MOVE_SPEED))
    
    def get_dodge_reward_multiplier(self) -> float:
        return 1.0 + self.get_skill_bonus(SkillType.DODGE_REWARD)
    
    def get_combo_duration_extra(self) -> int:
        from game.config import FPS
        return int(self.get_skill_bonus(SkillType.COMBO_DURATION) * FPS)
    
    def get_powerup_duration_multiplier(self) -> float:
        return 1.0 + self.get_skill_bonus(SkillType.POWERUP_DURATION)
    
    def to_dict(self):
        return {
            "skill_points": self.skill_points,
            "total_earned_points": self.total_earned_points,
            "branches": [branch.to_dict() for branch in self.branches.values()],
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        manager = cls()
        manager.skill_points = data.get("skill_points", 0)
        manager.total_earned_points = data.get("total_earned_points", 0)
        
        for branch_data in data.get("branches", []):
            branch = SkillBranch.from_dict(branch_data)
            manager.branches[branch.type] = branch
        
        return manager


SKILL_TREE_SAVE_FILE = "skill_tree_save.json"


def load_skill_tree():
    if os.path.exists(SKILL_TREE_SAVE_FILE):
        try:
            with open(SKILL_TREE_SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return SkillTreeManager.from_dict(data)
        except (json.JSONDecodeError, KeyError, Exception):
            pass
    
    return SkillTreeManager()


def save_skill_tree(manager: SkillTreeManager):
    try:
        with open(SKILL_TREE_SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(manager.to_dict(), f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def get_skill_tree_manager():
    return SkillTreeManager()
