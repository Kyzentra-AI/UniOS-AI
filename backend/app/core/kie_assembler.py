from typing import Dict, Any

class LearnerContextAssembler:
    @staticmethod
    def assemble(learner_data: dict, academic_data: dict, preferences_data: dict) -> Dict[str, Any]:
        """
        Assembles a normalized Learner Context from raw database rows.
        """
        return {
            "learner_id": learner_data.get("id"),
            
            "education": {
                "academic_status": academic_data.get("academic_status"),
                "university": academic_data.get("university"),
                "degree_program": academic_data.get("degree_program"),
                "domain": academic_data.get("domain"),
                "current_year": academic_data.get("current_year"),
                "graduation_year": academic_data.get("graduation_year"),
                "subjects": academic_data.get("subjects") or []
            } if academic_data else {},
            
            "career": {
                "primary_goal": learner_data.get("primary_goal"),
                "target_skills": learner_data.get("target_skills") or []
            },
            
            "skills": learner_data.get("skills") or [],
            "projects": learner_data.get("projects") or [],
            "research": learner_data.get("research"),
            "experience": learner_data.get("experience"),
            
            "preferences": {
                "daily_study_hours": preferences_data.get("daily_study_hours"),
                "learning_depth": preferences_data.get("learning_depth")
            } if preferences_data else {}
        }
