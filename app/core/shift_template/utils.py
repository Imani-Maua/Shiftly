from fastapi import HTTPException, status
from app.core.shift_template.schema import Role, TemplateIn
from app.database.models import ShiftTemplate

#this utility function will be more useful in the scheduling engine since that is where the staffing and scheduling logic is applied
def staffing_configuration(template: TemplateIn) -> dict:


        STAFFING_CONFIGURATION_RULES = {
            Role.MANAGER.value : {"low": 1, "med": 1, "high": 1},
            Role.LEADER.value: {"low": 1, "med": 2, "high": 3},
            Role.BARTENDER.value: {"low": 1, "med": 2, "high": 3},
            Role.SERVER.value: {"low": 2, "med": 3, "high": 4},
            Role.RUNNER.value: {"low": 1, "med": 2, "high": 3},
            Role.HOSTESS.value: {"low": 1, "med": 1, "high": 2}
        }

        role_staffing = STAFFING_CONFIGURATION_RULES.get(template.role)
        if not role_staffing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail=f"Unknown role: {template}")
        
        return role_staffing

def set_staffing_needs(staffing: str, staffing_config: dict, template: ShiftTemplate) -> int:

    staffing_needs: int = staffing_config.get(staffing)
    if not staffing_needs:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid staffing level: {staffing}")
    template.role_count = staffing_needs
    return staffing_needs


