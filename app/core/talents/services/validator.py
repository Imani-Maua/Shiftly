from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, date, datetime
from abc import ABC, abstractmethod
from app.core.talents.schema import TalentIn, TalentUpdate
from app.database.models import Talent
from app.core.talents.utils import set_contract_hours, context_finder



class AbstractValidator(ABC):
    @abstractmethod
    def validate_talent(context: dict):
        raise NotImplementedError


class TalentInputValidator(AbstractValidator):
    def validate_talent(context: dict):
        data: TalentIn = context["data"]
        talent: Talent = context["talent"]

        if data.start_date > date.today() + timedelta(days=7):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail="Start date too far in the future")
        
        if data.start_date < date.today():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Start date cannot be in the past")
        
        if talent:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail="A talent with this email already exists")
        if not data.firstname.strip() or not data.lastname.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail="Name cannot be empty")

class TalentUpdateValidator(AbstractValidator):

    def validate_talent(context: dict):
        db: Session = context["db"]
        data: TalentUpdate = context["data"]
        talent: Talent = context["talent"]
        if not talent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Talent not found")

        if data.is_active is True:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Reactivation is not allowed. Please create a new talent profile.")
        
        if data.is_active is False:
            talent.end_date = datetime.now().date()
        
        if data.contract_type:
            talent.hours = set_contract_hours(data.contract_type)

        if data.firstname is not None and not data.firstname.strip():
            return

        if data.lastname is not None and not data.lastname.strip():
            return


input_validators = [TalentInputValidator]
update_validators = [TalentUpdateValidator]