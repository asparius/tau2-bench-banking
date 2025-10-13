import json
from typing import Optional

from tau2.data_model.tasks import Task
from tau2.domains.banking.data_model import BankingDB
from tau2.domains.banking.tools import BankingTools
from tau2.domains.banking.utils import BANKING_DB_PATH, BANKING_POLICY_PATH, BANKING_TASKS_PATH
from tau2.environment.environment import Environment


def get_environment(
    db: Optional[BankingDB] = None,
    solo_mode: bool = False,
) -> Environment:
    """Get the banking environment."""
    if db is None:
        db = BankingDB.load(BANKING_DB_PATH)
    
    tools = BankingTools(db)
    with open(BANKING_POLICY_PATH, "r") as fp:
        policy = fp.read()
    
    env = Environment(
        domain_name="banking",
        policy=policy,
        tools=tools,
        user_tools=None,  # Banking domain doesn't have user tools
    )
    
    if solo_mode:
        env.set_solo_mode(True)
    
    return env


def get_tasks() -> list[Task]:
    """Get the tasks for the banking domain."""
    with open(BANKING_TASKS_PATH, "r") as fp:
        tasks = json.load(fp)
    return [Task.model_validate(task) for task in tasks]
