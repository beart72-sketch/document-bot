from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

class SubscriptionType(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    TRIAL = "trial"

class DocumentStatus(str, Enum):
    DRAFT = "draft"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class DocumentCategory(str, Enum):
    CIVIL_LAW = "civil_law"
    HOUSING_LAW = "housing_law"
    FAMILY_LAW = "family_law"
    BUSINESS_LAW = "business_law"

class TemplateComplexity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXPERT = "expert"

# Состояния разговора для FSM
class ConversationState(int, Enum):
    MAIN_MENU = 0
    CHOOSING_CATEGORY = 1
    CHOOSING_DOCUMENT = 2
    FILLING_DETAILS = 3
    SMART_ASSISTANT = 4
    PREMIUM_MENU = 5
    PAYMENT_PROCESS = 6
    ACTIVATE_PREMIUM = 7
    VIEW_DOCUMENTS = 8
    USER_PROFILE = 9
    CACHE_MANAGEMENT = 10
    ADMIN_PANEL = 11
    RATING_FEEDBACK = 12
