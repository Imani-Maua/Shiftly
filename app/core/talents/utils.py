from sqlalchemy.orm import Session
from app.core.talents.schema import ContractType, TalentIn
from app.database.models import Talent

def set_contract_hours(contract_type: str):
    contract_hours = {
        ContractType.FULL_TIME.value: 40,
        ContractType.PART_TIME.value: 30,
        ContractType.STUDENT.value: 24
    }

    return contract_hours.get(contract_type)



    